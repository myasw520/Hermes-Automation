import sys
import os
import requests

msg = """📅 【408 院校库补齐逐年历史日期 & 考研小程序数据获取方案】

1. 日期与历史年限标注已全面升级：
   • 补齐 2023、2024、2025 连续三年真实复试线与录取均分对比
   • 明确标注 2026 最新招生简章发布日期（9月中下旬）
   • 全页面打上数据采集与验证时间戳：2026-10-21

2. 关于“考研小程序”更细数据（一分一段表/拟录取名单）获取分析：
   • 数据本质：高校每年仅公示7天的拟录取PDF/Excel存档 + 考生自愿晒分大数据
   • Hermes 自动化抓取可行性：
     - PC 微信小程序由 WeChatAppEx 运行，底层均为标准 HTTPS REST API
     - Hermes 可通过本地代理截获 Token 与签名接口，直接全量拉取一分一段表
     - 亦可直接监控各大高校研招办官网，自动下载并解析拟录取名单 Excel/PDF

3. 前端交互看板与本地 Obsidian 智库已同步刷新！"""

token = os.environ.get("TELEGRAM_BOT_TOKEN")  # 从 .env 读取
chat_id = "-1004415041729"
topic_id = 3
proxies = {'http': 'http://127.0.0.1:7897', 'https': 'http://127.0.0.1:7897'}

try:
    r = requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json={"chat_id": chat_id, "message_thread_id": topic_id, "text": msg}, proxies=proxies, timeout=10)
    print("TG Response:", r.status_code)
except Exception as e:
    print("Push error:", e)
