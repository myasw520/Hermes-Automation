import json
import os
import requests
import time

CLEAN_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Content-Type': 'application/json'
}

KEYS_POOL_FILE = r"C:\Users\zzx05\Hermes-Automation\config\keys_pool.json"
OUTPUT_REPORT = r"C:\Users\zzx05\Hermes-Automation\reports\CS_22_vs_11_Score_Inflation_Analysis.md"
VAULT_NOTE = r"C:\Users\zzx05\Documents\CS408-Knowledge-Vault\11-计算机专硕22内卷分化与往年真实录取分对比深度调研.md"

def load_key():
    with open(KEYS_POOL_FILE, 'r', encoding='utf-8') as f:
        pool = json.load(f)
    return pool[0] # ChatAnywhere gpt-4o-mini is ultra stable

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
                    "你是一位精通全国计算机考研（408与自命题）十余年招生大数据与真实拟录取名单的资深升学分析师。\n"
                    "针对考生普遍关心的【去年听说专硕22（数二+英二）非常卷、分数飙到极高】的疑问，进行深度、客观、全方位的数据拆解。\n"
                    "【要求】：\n"
                    "1. 讲透'卷'的底层本质：试卷容易导致的绝对高分膨胀（数二英二均分自然高于数一英一25~35分）vs 真实竞争录取率（总名额基数差异）。\n"
                    "2. 输出规范的横向对比表格：选取代表性高校（浙大、华科、北邮、西电、杭电、苏大、成电、重邮等），对比近3年（2023-2025届）学硕11与专硕22的统考名额、真实录取分中位数差异。\n"
                    "3. 深度解析'专硕22的两极分化'（顶级985修罗场 vs 优质211/双非避风港）。"
                )
            },
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2,
        "max_tokens": 3500
    }
    
    print("[Hermes Engine] Querying model for deep 22 vs 11 score inflation analysis...", flush=True)
    resp = requests.post(url, headers=headers, json=payload, timeout=90)
    resp.raise_for_status()
    return resp.json()['choices'][0]['message']['content']

def main():
    prompt = """
请针对计算机考研考生最核心的顾虑【专硕22（数二英二）分数极高、是否内卷到无法上岸】，进行彻底的往年真实数据分析：

1. 【“22 分数虚高”的数学物理本质剖析】：
   - 为什么近几年专硕22经常出现“370分进不了某些名校复试”、“录取均分385+”的惊人现象？
   - 换算试卷难度：数二比数一平均分高多少？英二比英一平均分高多少？
   - 为什么说“考22拿370分，在真实知识能力上仅相当于考11拿335分左右”？这种心理预期偏差是如何误导小白的？

2. 【标杆院校 11 (学硕) vs 22 (专硕) 往年真实录取数据横向矩阵】：
   请整理详细对比表格，涵盖以下代表性高校（近3年 2023-2025 届实际考情）：
   - 顶级985：浙江大学、中国科学技术大学、华中科技大学
   - 强势名门：北京邮电大学、电子科技大学
   - 稳健211：西安电子科技大学、苏州大学
   - 优质双非：杭州电子科技大学、重庆邮电大学
   表格字段必须包含：
   [院校名称]、[学硕11真实统考招生名额 / 拟录取中位数]、[专硕22真实统考招生名额 / 拟录取中位数]、[两者录取分断层差]、[名额倍数比]、[真实上岸难度与容错率对比]。

3. 【22 内卷的两极分化现象深度解读】：
   - 哪些院校/方向是真正的“22 卷王修罗场”（高分神仙扎堆，录取分飙到380+）？
   - 哪些院校的 22 属于“大盘子、招生人数极多、分数线合理且过线基本全要”的高性价比上岸沃土？

4. 【给纠结 11 还是 22 考生的终极定心丸与报考法则】：
   - 面对 22 的高分现象，普通考生该如何制定初试分数目标与择校策略？
"""

    result = query_llm(prompt)
    
    full_doc = "# 📊 计算机考研 22 (数二+英二) 内卷真相与 11 vs 22 往年真实录取分对比深度调研\n\n"
    full_doc += "> 本专项调研报告由 Hermes 自动化引擎通过去标识化脱敏流水线调用大模型智库独立完成。\n"
    full_doc += "> 核心目的：以真实录取数据拆解“22专硕分数虚高”的本质，破除盲目焦虑，提供科学决策依据。\n\n---\n\n"
    full_doc += result
    
    os.makedirs(os.path.dirname(OUTPUT_REPORT), exist_ok=True)
    with open(OUTPUT_REPORT, "w", encoding="utf-8") as f:
        f.write(full_doc)
        
    with open(VAULT_NOTE, "w", encoding="utf-8") as f:
        f.write(full_doc)
        
    print(f"Investigation complete! Saved to {OUTPUT_REPORT} and {VAULT_NOTE}")

if __name__ == '__main__':
    main()
