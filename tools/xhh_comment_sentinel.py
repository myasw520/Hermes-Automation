# -*- coding: utf-8 -*-
"""小黑盒评论区黑名单哨兵（Hermes 专属舆情巡检）
功能：
1. 监控指定文章（link_id）的评论区（通过已登录的 Chrome CDP 9223 无感抓取）；
2. 扫描评论中是否有恶意扣帽子、带节奏的词汇（如：AI、机翻、豆包、人机、水帖、GPT、劣质等）；
3. 发现恶评立即通过 Telegram（Topic 5）向手机发送高优先级报警，附带发言人、违规内容与一键删评拉黑提醒。
"""
import os
import sys
import re
import json
import time
import asyncio
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

try:
    from playwright.async_api import async_playwright
except ImportError:
    from patchright.async_api import async_playwright

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = BASE_DIR / "config"
MONITOR_FILE = CONFIG_DIR / "monitored_articles.json"
HISTORY_FILE = CONFIG_DIR / "alerted_comments.json"

# 恶意带节奏/扣帽子关键词（只要命中立刻报警）
TOXIC_KEYWORDS = [
    r"ai", r"a\.i", r"人机", r"机翻", r"豆包", r"gpt", r"大模型",
    r"劣质", r"水帖", r"假帖", r"机器写", r"chatgpt", r"量产", r"洗稿",
    r"骗赞", r"营销号", r"搬运"
]

def load_json(p, default):
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return default
    return default

def save_json(p, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def send_tg_alert(article_title, author, content, link_id):
    """通过 tg_notify 或 Docker 发送预警"""
    script = BASE_DIR / "tools" / "tg_notify.py"
    msg = (
        f"🚨 *【小黑盒恶评预警 · 立即删评拉黑】*\n"
        f"📌 *文章*：{article_title} (ID: `{link_id}`)\n"
        f"👤 *违规用户*：{author}\n"
        f"💬 *恶评内容*：\n> {content}\n\n"
        f"⚡ *建议操作*：该用户可能在带节奏，请立即打开手机小黑盒，点击该评论右上角 **【删除评论】并勾选【拉黑该用户】**，防止破窗效应！"
    )
    import subprocess
    # Try local python or docker exec hermes
    res = subprocess.run([sys.executable, str(script), msg, "5"], capture_output=True, text=True)
    if "Failed" in res.stdout or res.returncode != 0:
        # Fallback to docker container hermes
        docker_cmd = ["docker", "exec", "hermes", "python", "/opt/data/work/treasure/tools/tg_notify.py", msg, "5"]
        subprocess.run(docker_cmd, capture_output=True)

async def fetch_comments_via_cdp(link_id: str):
    """通过本地 9223 CDP 获取评论列表"""
    try:
        async with async_playwright() as p:
            browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9223")
            ctx = browser.contexts[0]
            page = await ctx.new_page()
            
            captured_comments = []
            async def handle_resp(resp):
                if "bbs/app/link/tree" in resp.url and str(link_id) in resp.url:
                    try:
                        d = await resp.json()
                        res = d.get("result", {})
                        raw_c = res.get("comments", []) or []
                        captured_comments.extend(raw_c)
                    except Exception:
                        pass
            
            page.on("response", handle_resp)
            target_url = f"https://www.xiaoheihe.cn/app/bbs/link/{link_id}"
            await page.goto(target_url, timeout=15000)
            await page.wait_for_timeout(3000)
            
            # Scroll down to ensure comments are triggered
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(2000)
            await page.close()
            return captured_comments
    except Exception as e:
        print(f"[warn] CDP 抓取评论失败 (ID: {link_id}): {e}")
        return []

def scan_once():
    articles = load_json(MONITOR_FILE, [])
    if not articles:
        print("[info] 监控列表为空。可通过 python tools/xhh_comment_sentinel.py --add <link_id> <title> 添加。")
        return

    alerted = set(load_json(HISTORY_FILE, []))
    new_alerts = 0

    for item in articles:
        link_id = str(item.get("link_id"))
        title = item.get("title", f"文章 {link_id}")
        if not link_id:
            continue
        
        print(f"[scan] 正在巡检文章: {title} (ID: {link_id})...")
        comments = asyncio.run(fetch_comments_via_cdp(link_id))
        print(f"  当前评论总数: {len(comments)}")
        
        for c in comments:
            cid = str(c.get("comment_id") or c.get("id"))
            if cid in alerted:
                continue
            
            text = c.get("text", "") or c.get("content", "")
            user_info = c.get("user", {})
            uname = user_info.get("username", "匿名盒友")
            
            # 正则匹配恶评关键字
            is_toxic = False
            hit_word = ""
            for kw in TOXIC_KEYWORDS:
                if re.search(kw, text, re.IGNORECASE):
                    is_toxic = True
                    hit_word = kw
                    break
            
            if is_toxic:
                print(f"🚨 [ALERT] 命中带节奏词 [{hit_word}]！用户: {uname}, 内容: {text}")
                send_tg_alert(title, uname, text, link_id)
                alerted.add(cid)
                new_alerts += 1
            else:
                alerted.add(cid)

    save_json(HISTORY_FILE, list(alerted))
    print(f"[check] 巡检完成，本次新增报警: {new_alerts} 条。")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--add":
        lid = str(sys.argv[2])
        t = sys.argv[3] if len(sys.argv) > 3 else f"文章_{lid}"
        arts = load_json(MONITOR_FILE, [])
        # Check if already in list
        exists = any(str(a.get("link_id")) == lid for a in arts)
        if not exists:
            arts.append({"link_id": lid, "title": t, "added_at": time.strftime("%Y-%m-%d %H:%M:%S")})
            save_json(MONITOR_FILE, arts)
            print(f"[✓] 已添加监控: {t} ({lid})")
        else:
            print(f"[info] 文章 {lid} 已在监控列表中。")
    else:
        scan_once()
