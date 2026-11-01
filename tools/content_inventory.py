# -*- coding: utf-8 -*-
"""
内容库存每日提醒 (content_inventory.py)
========================================
只读扫描三处内容资产，组装一条 Telegram 提醒，让"内容线停摆"变得可感知：
1. reports/xiaoheihe_articles/  最新推文距今几天
2. reports/hermes_output/stockpile_drafts/ + reports/stockpile_drafts/  可用囤稿套数
3. config/monitored_articles.json  巡检池条数（发新帖后忘了喂池子会在这里暴露）

设计约束：无浏览器、无 LLM、无写操作（唯一 IO 是 TG 推送），不会坏。
注册：daemon_scheduler.py TASKS['content_inventory']，每日一次。
"""

import sys
import os
import json
import time
import glob

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "services"))
from config_lib import BOT_TOKEN, CHAT_ID
from wool_radar import send_telegram_text, TOPIC_CHAT_ID


def days_since(ts):
    return int((time.time() - ts) / 86400)


def fmt_days(n):
    if n <= 1:
        return "1 天内"
    return f"{n} 天前"


def scan_latest_article():
    """最新小黑盒推文距今天数"""
    patterns = [
        os.path.join(BASE_DIR, "reports", "xiaoheihe_articles", "*.md"),
        os.path.join(BASE_DIR, "reports", "ai_daily_posts", "*.md"),
    ]
    newest = 0
    for pat in patterns:
        for f in glob.glob(pat):
            mtime = os.path.getmtime(f)
            if mtime > newest:
                newest = mtime
    if newest == 0:
        return None, "从未产出"
    return days_since(newest), time.strftime("%m-%d", time.localtime(newest))


def scan_stockpile():
    """可用囤稿套数（两处 stockpile 目录里的 md/blocks 文件数）"""
    count = 0
    patterns = [
        os.path.join(BASE_DIR, "reports", "hermes_output", "stockpile_drafts", "**", "*.md"),
        os.path.join(BASE_DIR, "reports", "stockpile_drafts", "**", "*.md"),
        os.path.join(BASE_DIR, "reports", "stockpile_drafts", "**", "*.json"),
    ]
    for pat in patterns:
        count += len(glob.glob(pat, recursive=True))
    return count


def scan_monitored():
    """巡检池条数"""
    p = os.path.join(BASE_DIR, "config", "monitored_articles.json")
    try:
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
        return len(data) if isinstance(data, list) else 0
    except Exception:
        return 0


def main():
    days, latest_date = scan_latest_article()
    stock = scan_stockpile()
    monitored = scan_monitored()

    lines = ["📦 内容库存日报"]
    lines.append(f"• 最新推文：{fmt_days(days) if days is not None else '从未产出'}（{latest_date}）")
    lines.append(f"• 可用囤稿：{stock} 篇/套")
    lines.append(f"• 巡检池：{monitored} 篇在盯")

    hints = []
    if days is not None and days >= 3:
        hints.append(f"已经 {days} 天没发新帖")
    if stock > 0 and (days is None or days >= 3):
        hints.append("囤稿在吃灰，挑一套走 post-xiaoheihe 流水线")
    if days is not None and days < 3 and monitored < 1:
        hints.append("新帖可能还没喂巡检池，记得把 link_id 加进 config/monitored_articles.json")
    if hints:
        lines.append("")
        lines.append("⚠️ " + "；".join(hints))
    else:
        lines.append("")
        lines.append("✅ 节奏正常")

    text = "\n".join(lines)
    print(text)
    try:
        send_telegram_text(TOPIC_CHAT_ID, text)
        print("[+] 已推送 Telegram")
    except Exception as e:
        print(f"[!] Telegram 推送失败（不影响退出码）: {e}")


if __name__ == "__main__":
    main()
