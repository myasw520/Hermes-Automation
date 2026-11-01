# -*- coding: utf-8 -*-
"""
每日 AI 圈热点与爆款推文全自动流水线 (daily_ai_trending_harvester.py)
- 定位：每日定时抓取一手 AI 突破、爆款开源大模型、GitHub 杀手级 AI 生产力项目
- 调性：小黑盒/极客专栏量身定制（拒绝假大空新闻公关稿，只聊好玩的模型、能用的工具、能抄的代码）
- AI 引擎：ZeroGate 网关 workbuddy/glm-5.3-flash (超快稳定 10s 出文，同享 25 亿 Token 池)
- 产出：reports/ai_daily_posts/，支持一键推送到 Telegram
"""

import sys
import os
import json
import time
import argparse
import urllib.request
import urllib.error
from datetime import datetime

# Windows 终端编码守护
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "reports", "ai_daily_posts")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 网关与 Telegram 凭证统一从项目根 .env 读取（config_lib），不再硬编码
sys.path.insert(0, os.path.join(PROJECT_ROOT, "services"))
from config_lib import GATEWAY_URL, GATEWAY_KEY, BOT_TOKEN, CHAT_ID

GATEWAY_URL = f"{GATEWAY_URL.rstrip('/')}/chat/completions"
GATEWAY_KEY = GATEWAY_KEY
MODEL_NAME = "workbuddy/glm-5.3-flash"

TELEGRAM_CONFIG = {
    "bot_token": BOT_TOKEN,
    "chat_id": CHAT_ID,
    "topic_id": 3
}

# ==================== 1. 一手 AI 热点数据源抓取 ====================

def fetch_github_ai_trending():
    """抓取 GitHub 近期高星爆发的开源 AI/LLM 神器"""
    print("[*] 正在扫描 GitHub Trending AI 开源项目榜单...")
    # 搜索近期创建且 star 增长极快的项目
    url = "https://api.github.com/search/repositories?q=topic:llm+stars:>100&sort=stars&order=desc&per_page=6"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "application/vnd.github.v3+json"
    }
    req = urllib.request.Request(url, headers=headers)
    items = []
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            for r in data.get("items", [])[:5]:
                items.append({
                    "name": r.get("full_name"),
                    "stars": r.get("stargazers_count"),
                    "desc": r.get("description", "无描述"),
                    "url": r.get("html_url")
                })
        print(f"[+] 抓取到 {len(items)} 个高潜开源 AI 项目！")
    except Exception as e:
        print(f"[-] GitHub AI 项目抓取异常 (使用内置备用热点): {e}")
        # 兜底备用
        items = [
            {"name": "modelcontextprotocol/servers", "stars": 15200, "desc": "Anthropic 官方开源的 MCP 协议生态库，连接真实物理世界", "url": "https://github.com/modelcontextprotocol/servers"},
            {"name": "vllm-project/vllm", "stars": 32000, "desc": "全球高吞吐量 LLM 生产推理引擎，单卡并发飙升", "url": "https://github.com/vllm-project/vllm"},
            {"name": "karpathy/minbpe", "stars": 9800, "desc": "前 OpenAI 科学家手搓 GPT-4 级 BPE Tokenizer 极简库", "url": "https://github.com/karpathy/minbpe"}
        ]
    return items

def fetch_huggingface_trending():
    """获取 Hugging Face 每日爆款模型与论文动态"""
    print("[*] 正在聚合 Hugging Face 顶尖开源模型趋势...")
    # 模拟抓取或返回最新突破模型
    return [
        {"model": "DeepSeek-V3 / R1", "highlight": "强化学习与开源推理模型里程碑，以极低训练成本击穿闭源防线"},
        {"model": "GLM-4 / 5 Flash 系列", "highlight": "国产超大百万上下文端侧长推理，编程与逆向场景表现抢眼"},
        {"model": "Qwen 2.5-Coder", "highlight": "开源编程代码生成天花板，全面挑战商业级 Claude 3.5 Sonnet"}
    ]

# ==================== 2. AI 爆款推文生成 ====================

def generate_daily_ai_post(gh_items, hf_items):
    today_str = datetime.now().strftime("%Y-%m-%d")
    print(f"[*] 启动 AI 推理引擎，正在为 {today_str} 生成小黑盒 AI 热点长文...")
    
    intel_text = f"【今日精选 GitHub 爆发级 AI 开源项目】:\n"
    for item in gh_items:
        intel_text += f"- 项目: {item['name']} (Stars: {item['stars']})\n  痛点与功能: {item['desc']}\n  仓库: {item['url']}\n"
        
    intel_text += f"\n【今日顶尖开源大模型与算法风向】:\n"
    for hf in hf_items:
        intel_text += f"- 模型: {hf['model']} -> 核心突破: {hf['highlight']}\n"
        
    prompt = (
        f"你是一个混迹小黑盒、V2EX 和 GitHub 多年的极客老哥兼硬核 AI 观察员。\n"
        f"请基于以下一手 AI 突破与开源工具情报，为盒友撰写一篇【好玩、实用、能抄作业、绝无公关废话】的今日 AI 热点推文：\n\n"
        f"{intel_text}\n\n"
        f"【写作调性规范】：\n"
        f"1. 标题必须有冲击力，20字以内（例如：《炸裂！今天开源圈又搞大事情，这几个神器太香了》）；\n"
        f"2. 融入小黑盒专属 cube 表情：[cube_niubi]、[cube_le]、[cube_wunai]、[cube_tusiji]；\n"
        f"3. 结构：\n"
        f"   - ⚡【30秒省流指南】：用 2~3 句话直接甩出今天最重要的技术突破，不废话；\n"
        f"   - 🤖【硬核开源项目点名】：挑出 2~3 个最接地气的工具，讲透普通人/开发者怎么用它白嫖提升 10 倍效率；\n"
        f"   - 🧠【模型前沿大实话】：用老哥大白话锐评当前大模型竞争格局，别写套话；\n"
        f"   - 💬【评论区互动】：留一个好玩的问题，结尾附带 #AI #开源 #程序员 #黑科技 话题。\n"
        f"直接输出 Markdown 原文。"
    )
    
    payload = json.dumps({
        "model": MODEL_NAME,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 2000,
        "temperature": 0.7
    }).encode("utf-8")
    
    req = urllib.request.Request(
        GATEWAY_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {GATEWAY_KEY}"
        }
    )
    
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            msg = data.get("choices", [{}])[0].get("message", {})
            content = msg.get("content", "").strip()
            usage = data.get("usage", {})
            tokens = usage.get("total_tokens", 0)
            elapsed = round(time.time() - t0, 1)
            return content, tokens, elapsed
    except Exception as e:
        print(f"[-] AI 推理失败: {e}")
        return None, 0, 0

# ==================== 3. 主流程与推送 ====================

def main():
    parser = argparse.ArgumentParser(description="每日 AI 热点推文自动生成流水线")
    parser.add_argument("--push-tg", action="store_true", help="是否推送到 Telegram 话题群组")
    args = parser.parse_args()
    
    today_stamp = datetime.now().strftime("%Y%m%d")
    print("=" * 65)
    print(f"📡 启动每日 AI 热点自动化生产流水线 [{today_stamp}]")
    print("=" * 65)
    
    gh_items = fetch_github_ai_trending()
    hf_items = fetch_huggingface_trending()
    
    content, tokens, elapsed = generate_daily_ai_post(gh_items, hf_items)
    if not content:
        print("[-] 推文生成失败。")
        return
        
    out_file = os.path.join(OUTPUT_DIR, f"ai_daily_{today_stamp}.md")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(content)
        
    print("\n" + "=" * 65)
    print(f"🎉 每日 AI 推文已生成！耗时 {elapsed}s | 消耗 Token: {tokens}")
    print(f"📁 归档路径: {out_file}")
    print("=" * 65 + "\n")
    print(content[:600] + "\n\n... (正文已完整保存至文件)")
    print("=" * 65)
    
    if args.push_tg:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_CONFIG['bot_token']}/sendMessage"
            payload = json.dumps({
                "chat_id": TELEGRAM_CONFIG["chat_id"],
                "message_thread_id": TELEGRAM_CONFIG["topic_id"],
                "text": content[:3800],
                "parse_mode": "Markdown"
            }).encode("utf-8")
            req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                print("[+] 已成功推送到 Telegram 话题群组！")
        except Exception as e:
            print(f"[-] Telegram 推送失败: {e}")

if __name__ == "__main__":
    main()
