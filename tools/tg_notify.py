import sys
import json
import os
import urllib.request

# 凭证统一从项目根 .env 读取（config_lib），不再硬编码
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "services"))
from config_lib import BOT_TOKEN, CHAT_ID

# 默认话题映射
TOPICS = {
    "wool": 3,
    "github": 4,
    "chat": 5,
    "3": 3,
    "4": 4,
    "5": 5
}

def send_notify(text, topic="4"):
    thread_id = TOPICS.get(str(topic).lower(), 4)
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = json.dumps({
        "chat_id": CHAT_ID,
        "message_thread_id": thread_id,
        "text": text,
        "parse_mode": "Markdown"
    }).encode("utf-8")
    
    proxies = [
        {"http": "http://127.0.0.1:7897", "https": "http://127.0.0.1:7897"},
        {"http": "http://127.0.0.1:7890", "https": "http://127.0.0.1:7890"},
        {}
    ]
    
    for p in proxies:
        try:
            handler = urllib.request.ProxyHandler(p)
            opener = urllib.request.build_opener(handler)
            req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
            with opener.open(req, timeout=8) as r:
                return r.status == 200
        except Exception:
            continue
    return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python tg_notify.py [消息内容] [话题ID/名称: 3/4/5，默认4]")
        sys.exit(1)
        
    content = sys.argv[1]
    target_topic = sys.argv[2] if len(sys.argv) > 2 else "4"
    
    ok = send_notify(content, target_topic)
    if ok:
        print("[SUCCESS] Telegram sent!")
    else:
        print("[FAIL] Failed to send")
