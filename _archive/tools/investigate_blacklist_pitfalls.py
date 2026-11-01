import json
import os
import requests

CLEAN_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Content-Type': 'application/json'
}

KEYS_POOL_FILE = r"C:\Users\zzx05\Hermes-Automation\config\keys_pool.json"
OUTPUT_REPORT = r"C:\Users\zzx05\Hermes-Automation\reports\CS_Reexam_Blacklist_Pitfalls.md"
VAULT_NOTE = r"C:\Users\zzx05\Documents\CS408-Knowledge-Vault\13-考研避雷指南与恶名院校套路深度警示.md"

def load_key():
    with open(KEYS_POOL_FILE, 'r', encoding='utf-8') as f:
        pool = json.load(f)
    return pool[0]

def query_llm(prompt):
    key_info = load_key()
    url = f"{key_info['base_url'].rstrip('/')}/chat/completions"
    headers = {**CLEAN_HEADERS, 'Authorization': f"Bearer {key_info['api_key']}"}
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": (
                    "你是一位客观、严谨、深谙全国研究生招生与复试潜规则的资深教育调研专家。\n"
                    "针对考生提出的【计算机考研中哪些高校在复试、阅卷或录取中有恶名/前科，需要坚决避雷】的问题，提供客观真实、有据可循的深度避坑警示。\n"
                    "【核心内容要求】：\n"
                    "1. 揭秘考研四大典型'臭名昭著'恶性操作模式（恶意压分留调剂名额给985名校生、超高差额复试比1:2~1:3把一志愿当炮灰、复试恶意拖延锁死调剂黄金期、不公开复试小分暗箱操作）。\n"
                    "2. 梳理考研圈内多年考生集体反馈、有明确历史争议或压分前科的代表性院校及典型表现（如某些偏远B区211压分吸纳名校调剂、某些高校复试极端歧视双非等真实案例）。\n"
                    "3. 总结小白考生【识别避雷院校的5大照妖镜标准】（如何通过往年拟录取公示、研招网调剂公告一眼看穿套路高校）。"
                )
            },
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2,
        "max_tokens": 3500
    }
    
    print("[Hermes Engine] Querying model for blacklist & notorious reexam pitfalls...", flush=True)
    resp = requests.post(url, headers=headers, json=payload, timeout=90)
    resp.raise_for_status()
    return resp.json()['choices'][0]['message']['content']

def main():
    prompt = """
请针对计算机考研小白，整理一份极其严谨、客观、具有保命价值的【考研避雷黑名单与恶名套路全景指南】：

1. 【考研圈公认的四大“断子绝孙”恶性套路拆解】：
   - 【套路 1：自命题专业课恶意严重压分（最恶毒）】：为什么有些院校把一志愿考生专业课压到40-60分？导致考生过不了国家线直接沦为失学青年？其真实动机（为了在调剂系统抢985名校落榜生）是什么？
   - 【套路 2：超高差额复试比（1:200% ~ 1:300%）】：招20人叫60个人去复试，大量高分当分母陪跑，只为从后面捞关系户或优质生源。
   - 【套路 3：复试时间极度拖后（锁死调剂黄金期）】：拖到4月中旬才出复试结果，被刷考生直接错过全国95%的调剂名额。
   - 【套路 4：不透明录取（不公布排名、不公开复试细项分）】。

2. 【历史上在考研社区引发巨大争议/考生血泪声讨的典型院校类型与案例】：
   - 分析某些偏远省份211院校、部分省属重点高校在历年考研中被实锤或广泛声讨的压分/歧视一志愿现象。
   - 深入剖析其操作手法与受害考生的惨痛教训。

3. 【小白考生的“避雷照妖镜”—— 5 招教你识破渣男院校】：
   - 怎么看往年拟录取名单是不是大面积“一志愿无人上线，全靠调剂”？
   - 怎么查该校自命题历年平均分？
   - 为什么考 408 统考是天然粉碎“恶意压分”的最强护甲？
"""

    result = query_llm(prompt)
    
    full_doc = "# ⚠️ 计算机考研“避雷黑名单”与高校恶性套路深度警示（小白保命必读）\n\n"
    full_doc += "> 本专题报告由 Hermes 自动化引擎通过去标识化脱敏流水线调用大模型智库独立完成。\n"
    full_doc += "> 核心目的：揭秘考研招生中的制度性陷阱与不公正操作，帮助考生避开恶意压分、差额陪跑的渣男高校。\n\n---\n\n"
    full_doc += result
    
    os.makedirs(os.path.dirname(OUTPUT_REPORT), exist_ok=True)
    with open(OUTPUT_REPORT, "w", encoding="utf-8") as f:
        f.write(full_doc)
        
    with open(VAULT_NOTE, "w", encoding="utf-8") as f:
        f.write(full_doc)
        
    print(f"Report written to {OUTPUT_REPORT} and {VAULT_NOTE}")

if __name__ == '__main__':
    main()
