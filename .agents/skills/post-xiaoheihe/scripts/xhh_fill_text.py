# -*- coding: utf-8 -*-
"""小黑盒：把标题 + 正文（纯文本/Markdown 文件）填进当前编辑器，然后存草稿。

适用场景：
    短图文（发「图文」而不是「文章」），或你只想贴一段已经写好的文案。
    带大量配图的长文请用 xhh_build.py。

用法：
    python xhh_fill_text.py --title "标题" --content body.txt [--save-draft]
    python xhh_fill_text.py --title "标题" --content body.md --content-is-markdown --save-draft

说明：
    - 正文用 keyboard.insert_text 逐段插入，不走剪贴板，避免编码问题。
    - 编辑器支持 Markdown 输入规则（# 标题、- 列表、> 引用会在打字时自动转换），
      但 **加粗不支持 `**粗体**`**，`行内代码` 和 `---` 也不转换。
      所以 --content-is-markdown 只是把 `#` / `-` 原样打字，让编辑器自己转。
    - 标题/正文用键盘输入天然规避 ProseMirror 的 React 受控组件坑。
"""
from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

try:
    from playwright.async_api import async_playwright
except ImportError:
    from patchright.async_api import async_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
from xhh_common import (  # noqa: E402
    EDITOR_ARTICLE,
    EDITOR_IMAGE_TEXT,
    EDITOR_TITLE,
    connect,
    find_editor_page,
    log,
    print_config,
    require_login,
)


async def detect_editor(page):
    """返回 (正文选择器, 类型名)。文章编辑器优先，其次图文。"""
    if await page.locator(EDITOR_ARTICLE).count():
        return EDITOR_ARTICLE, "文章"
    if await page.locator(EDITOR_IMAGE_TEXT).count():
        return EDITOR_IMAGE_TEXT, "图文"
    return None, None


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--title", default="", help="标题（≤20 字最稳）")
    ap.add_argument("--content", default="", help="正文文本文件路径")
    ap.add_argument("--content-is-markdown", action="store_true",
                    help="按行输入，保留 # / - / > 让编辑器自动转换")
    ap.add_argument("--save-draft", action="store_true", help="填完点「保存草稿」")
    ap.add_argument("--publish", action="store_true",
                    help="⚠️ 点「发布」（文章类型实测会失效跳转，推荐用 --save-draft）")
    args = ap.parse_args()

    body = ""
    if args.content:
        body = Path(args.content).read_text(encoding="utf-8")
        log("[check] 正文 %d 字，前 40 字: %r" % (len(body), body[:40]))

    print_config()
    async with async_playwright() as p:
        browser, ctx = await connect(p)
        page = find_editor_page(ctx)
        if page is None:
            log("[FATAL] 没有编辑器标签页。请先打开「发布内容 → 发布文章/图文」。")
            await browser.close()
            return 1
        await page.bring_to_front()
        await page.wait_for_timeout(800)
        log("[0] 编辑器: %s" % page.url[:90])

        if not await require_login(page):
            await browser.close()
            return 1

        content_sel, kind = await detect_editor(page)
        if not content_sel:
            log("[FATAL] 编辑器没渲染出来（检查登录态，或页面还在加载）")
            await browser.close()
            return 1
        log("[1] 识别为「%s」编辑器" % kind)

        if args.title:
            t = page.locator(EDITOR_TITLE).first
            await t.click(timeout=8000)
            await page.keyboard.press("Control+a")
            await page.keyboard.press("Delete")
            await page.keyboard.type(args.title, delay=6)
            log("[2] 标题已填: %s" % args.title)

        if body:
            ed = page.locator(content_sel).first
            await ed.click(timeout=8000)
            await page.keyboard.press("Control+a")
            await page.keyboard.press("Delete")
            if args.content_is_markdown:
                lines = body.splitlines()
                for i, line in enumerate(lines):
                    if i:
                        await page.keyboard.press("Enter")
                    if line.strip():
                        await page.keyboard.insert_text(line)
                        await page.wait_for_timeout(35)
            else:
                # 整段插入（带换行），比逐行快且不会丢字
                await page.keyboard.insert_text(body)
            await page.wait_for_timeout(800)
            st = await page.evaluate(
                "(sel) => { const c = document.querySelector(sel);"
                " return c ? {len: (c.innerText||'').length, blocks: c.children.length} : null; }",
                content_sel,
            )
            log("[3] 正文已填: %s" % st)

        if args.publish:
            log("[warn] 正在点「发布」。文章类型实测会失效跳转，若失败请改用 --save-draft。")
            await page.get_by_text("发布", exact=True).first.click()
            await page.wait_for_timeout(6000)
            log("[4] 已点发布，请人工确认")
        elif args.save_draft:
            await page.get_by_text("保存草稿", exact=True).first.click()
            await page.wait_for_timeout(7000)
            log("[4] 已点「保存草稿」，到手机 App 草稿箱确认（网页点开是空白属正常）")
        else:
            log("[4] 未指定 --save-draft / --publish，内容只填在页面上，请自己操作")

        await browser.close()
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
