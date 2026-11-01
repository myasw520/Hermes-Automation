# -*- coding: utf-8 -*-
"""小黑盒：存完草稿后验内容（不靠肉眼，搭页面自己的请求便车）

背景：
    网页端点开草稿是空白的（编辑器不回填），这不代表内容丢了。
    真实内容在接口返回的 link.text 里（富文本 JSON）。

为什么不能自己 fetch：
    接口是 api.xiaoheihe.cn/bbs/app/link/drafts 和 /bbs/app/link/edit/info，
    必须带 app=heybox&os_type=web&x_app=heybox&hkey=<签名> 等一串 query 参数
    才返回数据，裸路径一律返回 null；hkey 是动态签名，脚本自己拼不出来。
    （2026-10-24 实测：裸 fetch 全部返回 null。）

正确做法（本脚本实现）：
    监听页面的网络响应 —— 打开草稿箱页，等它自己请求 /bbs/app/link/drafts；
    点进目标草稿，等它自己请求 /bbs/app/link/edit/info。搭便车拿数据。

用法：
    python xhh_verify_draft.py                     # 列出草稿箱，读第一条的正文
    python xhh_verify_draft.py --title "关键词"     # 按标题找草稿再读
    python xhh_verify_draft.py --expect 20         # 期望 20 张图，不符退出码 3
"""
from __future__ import annotations

import argparse
import asyncio
import json
import re
import sys
from pathlib import Path

try:
    from playwright.async_api import async_playwright
except ImportError:
    from patchright.async_api import async_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
from xhh_common import connect, log, print_config  # noqa: E402

DRAFTS_URL_KEY = "/bbs/app/link/drafts"
EDIT_INFO_URL_KEY = "/bbs/app/link/edit/info"


def dig_links(body):
    """从草稿列表响应里挖出 result.links[]（字段名容错）。"""
    if not isinstance(body, dict):
        return []
    result = body.get("result")
    if isinstance(result, dict):
        for key in ("links", "list", "drafts"):
            v = result.get(key)
            if isinstance(v, list) and v:
                return v
    # 兜底：全树找含 title 的对象数组
    stack = [body]
    while stack:
        cur = stack.pop()
        if isinstance(cur, list) and cur and isinstance(cur[0], dict) and "title" in cur[0]:
            return cur
        if isinstance(cur, dict):
            stack.extend(cur.values())
        elif isinstance(cur, list):
            stack.extend(cur)
    return []


def draft_id(item):
    for k in ("link_id", "linkid", "id"):
        v = item.get(k)
        if v not in (None, ""):
            return str(v)
    # 从 share_url 里挖
    m = re.search(r"link_id=([0-9a-f]+)", str(item.get("share_url", "")))
    return m.group(1) if m else None


async def main():
    ap = argparse.ArgumentParser(description="读接口校验小黑盒草稿内容")
    ap.add_argument("--title", default="", help="按标题关键词找草稿（默认读第一条）")
    ap.add_argument("--expect", type=int, default=0, help="期望图片数（0 = 不校验）")
    ap.add_argument("--raw", action="store_true", help="打印原始 JSON 片段")
    args = ap.parse_args()

    print_config()
    async with async_playwright() as p:
        browser, ctx = await connect(p)
        page = None
        for pg in ctx.pages:
            if "creator.xiaoheihe.cn" in pg.url:
                page = pg
                break
        if page is None:
            log("[FATAL] 没有小黑盒 creator 页面，先跑 start_chrome.py")
            await browser.close()
            return 1
        await page.bring_to_front()

        # ---- 1) 搭便车：草稿列表 ----
        got_list = []
        def on_drafts(r):
            if DRAFTS_URL_KEY in r.url:
                got_list.append(r)
        page.on("response", on_drafts)
        await page.goto("https://creator.xiaoheihe.cn/creator/drafts",
                        wait_until="domcontentloaded")
        await page.wait_for_timeout(6000)
        page.remove_listener("response", on_drafts)

        if not got_list:
            log("[FATAL] 没等到草稿列表请求（登录态失效或页面没加载出来）。")
            await browser.close()
            return 1
        try:
            body = await got_list[-1].json()
        except Exception as e:
            log("[FATAL] 草稿列表响应解析失败: %s" % e)
            await browser.close()
            return 1
        links = dig_links(body)
        if not links:
            log("[FATAL] 草稿列表为空或结构变了。用 --raw 看。")
            if args.raw:
                log(json.dumps(body, ensure_ascii=False)[:1500])
            await browser.close()
            return 1
        log("[1] 草稿 %d 条" % len(links))
        for it in links[:5]:
            log("    - %s %r" % (draft_id(it), str(it.get("title", ""))[:30]))

        target = links[0]
        if args.title:
            hits = [it for it in links if args.title in str(it.get("title", ""))]
            if not hits:
                log("[FATAL] 没找到标题含 %r 的草稿" % args.title)
                await browser.close()
                return 1
            target = hits[0]
        tid = draft_id(target)
        ttitle = str(target.get("title", ""))
        log("[2] 目标草稿: id=%s 标题=%r" % (tid, ttitle[:30]))

        # ---- 2) 搭便车：点进草稿，等 edit/info 响应 ----
        got_info = []
        def on_info(r):
            if EDIT_INFO_URL_KEY in r.url:
                got_info.append(r)
        page.on("response", on_info)
        try:
            card = page.get_by_text(ttitle, exact=False).first
            await card.click(timeout=8000)
        except Exception as e:
            log("[FATAL] 点不进草稿卡片: %s" % str(e)[:80])
            await browser.close()
            return 1
        ok = False
        for _ in range(15):
            await page.wait_for_timeout(1000)
            if got_info:
                ok = True
                break
        page.remove_listener("response", on_info)
        if not ok:
            log("[FATAL] 没等到 edit/info 响应（草稿可能没点开）")
            await browser.close()
            return 1
        info_body = await got_info[-1].json()

        # ---- 3) 解析结构 ----
        link = None
        stack = [info_body]
        while stack:
            cur = stack.pop()
            if isinstance(cur, dict):
                if "link_id" in cur and ("text" in cur or "title" in cur):
                    link = cur
                    break
                stack.extend(cur.values())
            elif isinstance(cur, list):
                stack.extend(cur)
        if link is None:
            log("[FATAL] edit/info 里没找到 link 对象（结构变了，用 --raw 看）")
            if args.raw:
                log(json.dumps(info_body, ensure_ascii=False)[:1500])
            await browser.close()
            return 1

        text = link.get("text")
        if isinstance(text, list):
            text = json.dumps(text, ensure_ascii=False)
        text = text or ""
        title = str(link.get("title", ""))

        # 把 text 数组的 html 块拼起来（可能有多个 block）
        html = ""
        try:
            arr = json.loads(text)
            if isinstance(arr, list):
                html = "".join(str(b.get("text", "")) for b in arr if isinstance(b, dict))
            else:
                html = text
        except Exception:
            html = text

        imgs = len(re.findall(r"<img", html))
        game_cards = len(re.findall(r"mention-game", html))
        wiki_cards = len(re.findall(r"mention-wiki", html))
        ps = len(re.findall(r"<p[ >]", html))
        vote = link.get("vote_info") or {}

        log("\n===== 草稿内容校验 =====")
        log("  标题      : %s" % title)
        thumb = link.get("thumb") or link.get("cover") or link.get("covers") or ""
        log("  封面      : %s" % (thumb if thumb else "(无)"))
        log("  正文字符  : %d" % len(html))
        log("  <img> 数  : %d" % imgs)
        log("  游戏卡片  : %d" % game_cards)
        log("  百科卡片  : %d" % wiki_cards)
        log("  <p> 数    : %d" % ps)
        if vote.get("title"):
            opts = vote.get("vote_options") or []
            log("  投票      : %r (%s, %d 个选项, 截止 %s)"
                % (vote.get("title"), "单选" if vote.get("option_mode") == 0 else "多选",
                   len(opts), vote.get("expire_at", "?")))
        names = re.findall(r">(\d{2}\s[^<]{2,30})<", html)
        if names:
            uniq = list(dict.fromkeys(names))
            log("  编号行    : %d 条 -> %s" % (len(uniq), ", ".join(uniq[:6]) + (" ..." if len(uniq) > 6 else "")))

        if args.raw:
            log("\n--- text（截断）---")
            log(html[:2000])

        ok_flag = True
        if args.expect:
            if imgs == args.expect:
                log("\n[PASS] 图片数 %d 与预期一致" % imgs)
            else:
                log("\n[FAIL] 图片数 %d != 预期 %d" % (imgs, args.expect))
                ok_flag = False

        # 回到草稿箱页，别停在编辑页
        await page.goto("https://creator.xiaoheihe.cn/creator/drafts",
                        wait_until="domcontentloaded")
        await browser.close()
    return 0 if ok_flag else 3


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
