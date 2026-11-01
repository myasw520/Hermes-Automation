import requests

token = os.environ.get("TELEGRAM_BOT_TOKEN")  # 从 .env 读取
chat_id = "-1004415041729"
topic_id = 3
proxies = {'http': 'http://127.0.0.1:7897', 'https': 'http://127.0.0.1:7897'}

msg = """⚠️ 【计算机考研恶名昭彰避雷黑名单与高校套路深度警示已就绪】

一、 考研圈公认四大“恶名套路”：
1. 自命题恶意压分：故意将一志愿压至 40~60 分不过国家线，腾空名额吸纳 985 调剂生
2. 超高差额复试比：1:200% ~ 1:300%，叫大批高分考生陪跑当分母
3. 复试极度拖后：拖至 4 月中旬才出结果，直接锁死考生调剂黄金期
4. 暗箱操作：不公开排名、不公布复试小分、非盲审

二、 避雷照妖镜 5 招识破渣男高校：
• 查往年拟录取名单：是否存在大面积“一志愿无人上线，全靠调剂”？
• 坚决考 408 统考：全国统一流水阅卷，天然免疫自命题恶意压分！
• 避开偏远地区某些有压分留调剂前科的 B 区 211 / 地方双非

报告已同步沉淀至 Obsidian 本地知识库！"""

try:
    r = requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json={"chat_id": chat_id, "message_thread_id": topic_id, "text": msg}, proxies=proxies, timeout=10)
    print("TG Response:", r.status_code)
except Exception as e:
    print("TG Error:", e)
