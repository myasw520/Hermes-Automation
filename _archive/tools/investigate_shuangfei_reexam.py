import json
import os
import requests
import time

CLEAN_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Content-Type': 'application/json'
}

KEYS_POOL_FILE = r"C:\Users\zzx05\Hermes-Automation\config\keys_pool.json"
OUTPUT_REPORT = r"C:\Users\zzx05\Hermes-Automation\reports\CS_Reexam_Discrimination_Analysis.md"
VAULT_NOTE = r"C:\Users\zzx05\Documents\CS408-Knowledge-Vault\12-计算机考研复试双非歧视红黑榜与南中医考生破局策略.md"

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
                    "你是一位长期跟踪全国计算机考研（408与自命题）复试录取实况、各大高校复试细则的资深升学首席规划师。\n"
                    "针对考生提出的【本科为南京中医药大学（国家双一流、医药类背景），担忧复试是否存在严重的双非歧视】的问题，提供真实、客观、犀利、具备极高指导价值的深度调查报告。\n"
                    "【核心内容要求】：\n"
                    "1. 揭秘'歧视'真相：高校复试歧视的真实运作机制（压一志愿留名额给名校调剂生、复试主观打分、同分优选本校生）vs 纯粹公平透明的高校机制（盲审抽签、机试代码定乾坤）。\n"
                    "2. 全国与江苏本地高校【复试红黑榜】：哪些院校是公认的'极度公平、保护一志愿、绝不歧视双非'（如南航、西电、南邮、苏大、华科等）；哪些院校有压分/偏好名校调剂的不良声誉。\n"
                    "3. 针对【南京中医药大学】考生的独家破局策略：如何把南中医的双一流招牌与医药学科背景，转化为计算机复试（尤其是医学大模型、医工交叉、智能诊疗）中的降维打击王牌。"
                )
            },
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2,
        "max_tokens": 3500
    }
    
    print("[Hermes Engine] Querying model for re-exam discrimination & Nanjing TCM analysis...", flush=True)
    resp = requests.post(url, headers=headers, json=payload, timeout=90)
    resp.raise_for_status()
    return resp.json()['choices'][0]['message']['content']

def main():
    prompt = """
请针对南京中医药大学的考生，进行一次深度的计算机考研复试“双非歧视与保护一志愿”专题调研：

1. 【复试“歧视”的本质与真实内幕】：
   - 考研复试所谓的“歧视双非”，在现实中到底是以什么形式发生的？（拆解恶性操作：差额复试故意刷双非高分等调剂、专业课压分导致学生无法调剂、面试主观分压至不合格）。
   - 考研公认的“极度公平透明高校”具备哪些特征？（盲审、抽签进场、禁带本科成绩单、机试代码定生死、初复试成绩同天公示、一志愿上线即招满不接受外校调剂）。

2. 【院校复试生态红黑榜（重点聚焦江苏省内及周边知名工科高校）】：
   - 【白名单（公认极度公平、保护一志愿、欢迎双非逆袭的标杆院校）】：
     * 江苏本地及邻近：南京航空航天大学、南京理工大学、苏州大学、南京邮电大学、河海大学、江南大学等。
     * 全国公认典范：西安电子科技大学、华中科技大学、北京邮电大学、杭州电子科技大学等。
     * 逐一说明每所学校的保护政策（如南航初复试加权机制、西电CSP抵机试、保护一志愿）。
   - 【避坑名单（考生反馈存在压分严重、偏好名校调剂生或复试不确定性大的院校类型）】。

3. 【为“南京中医药大学”考生的精准定制画像与王牌破局法】：
   - 明确南中医的真实地位：虽然计算机非传统工科强项，但南中医是“国家双一流建设高校”，绝非普通二本！
   - “医工交叉与医学AI大模型”的降维打击王牌：当前人工智能前沿正在疯狂涌向生物医药、临床问诊、医学影像、中医药知识图谱。如果面试中导师发现考生懂一些医学术语/生物学常识、并做过医疗数据分析，会带来怎样不可替代的面试加分？
   - 面试自我介绍与项目包装的具体建议。
"""

    result = query_llm(prompt)
    
    full_doc = "# ⚖️ 计算机考研复试“双非歧视”深度真相调查与南京中医药大学考生破局指南\n\n"
    full_doc += "> 本专题报告由 Hermes 自动化引擎通过去标识化脱敏流水线调用大模型智库独立完成。\n"
    full_doc += "> 针对南京中医药大学考生的真实背景，深度剖析考研复试生态、高校保护一志愿红黑榜及跨界破局法则。\n\n---\n\n"
    full_doc += result
    
    os.makedirs(os.path.dirname(OUTPUT_REPORT), exist_ok=True)
    with open(OUTPUT_REPORT, "w", encoding="utf-8") as f:
        f.write(full_doc)
        
    with open(VAULT_NOTE, "w", encoding="utf-8") as f:
        f.write(full_doc)
        
    print(f"Investigation complete! Saved to {OUTPUT_REPORT} and {VAULT_NOTE}")

if __name__ == '__main__':
    main()
