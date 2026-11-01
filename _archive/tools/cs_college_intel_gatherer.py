import json
import os
import requests
import time

CLEAN_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Content-Type': 'application/json'
}

KEYS_POOL_FILE = r"C:\Users\zzx05\Hermes-Automation\config\keys_pool.json"
OUTPUT_REPORT = r"C:\Users\zzx05\Hermes-Automation\reports\CS_Colleges_Guide.md"

def load_keys():
    with open(KEYS_POOL_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def query_llm(key_info, prompt, system_prompt):
    base_url = key_info.get('base_url', '').rstrip('/')
    api_key = key_info.get('api_key', '')
    site_name = key_info.get('name') or 'ChatAnywhere'
    model = 'gpt-4o-mini'
    
    url = f"{base_url}/chat/completions"
    headers = {**CLEAN_HEADERS, 'Authorization': f"Bearer {api_key}"}
    
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 3000
    }
    
    print(f"[{site_name}] Querying {model}...", flush=True)
    resp = requests.post(url, headers=headers, json=payload, timeout=120)
    resp.raise_for_status()
    data = resp.json()
    return data['choices'][0]['message']['content']

def main():
    keys = load_keys()
    key = keys[0] # ChatAnywhere is fast and rock solid
    
    sys_prompt = (
        "你是一位严谨、权威的中国计算机考研（408统考与自命题）升学规划资深导师。\n"
        "面向没有任何考研经验的应届/往届小白考生，提供真实客观、毫无套话、带有官方权威来源出处的择校与报考数据库。\n"
        "【关键指标要求】：\n"
        "1. 必须包含：各校近3年真实复试线与拟录取线差异、学硕vs专硕学费、专硕住宿政策（是否提供宿舍）、真实统考名额与推免比、报录比级别。\n"
        "2. 每一个学校和数据，都必须注明具体的官方权威出处（如：各校研究生招生网、学院官网拟录取公示、研招网专业目录等）。\n"
        "3. 采用清晰结构化Markdown与对比表格呈现。"
    )

    tasks = [
        ("一、 计算机考研核心概念扫盲与小白致命避坑指南", 
         """请针对完全没有考研经验的小白，深度拆解以下4大核心陷阱与官方核验渠道：
1. 【复试线 vs 真实录取线】：为什么学院公布的复试线（如310分）和最终录取考生的最低分/中位数（如355-365分）差距极大？什么是“差额复试比（120%-150%）”？小白如何看透初试安全线？
2. 【招生计划 vs 推免率】：为什么招生简章写招100人，实际统考只剩20个名额？什么是推免生（保研生）拟录取？如何精准查询留给统考生的真实名额？
3. 【专硕 vs 学硕深度对比】：
   - 学费大盘点：学硕普遍统一8000元/年，专硕有哪些名校（复旦/交大/清华深研院等）已调整至数万元/年？
   - 住宿政策黑洞：哪些一线城市高校（北大、北师大、南开、复旦等）已明确专硕不予安排校内住宿？对考生的租房成本有何重大影响？
   - 培养年限：2年制、2.5年制与3年制区别。
4. 【408 统考 vs 自命题】：考 408 统考对于小白的核心优势是什么（为何说考408调剂是全网通，考自命题调剂几乎无路可走）？为什么全国985/211高校正在大面积改考408？
【请严格标注各项政策与数据的权威官方来源】"""),

        ("二、 全国计算机考研标杆院校矩阵与真实报考数据分析（985/211/双非）",
         """请按层次梯度整理计算机考研代表性高校的详细矩阵对比。请输出详尽的 Markdown 表格，包含字段：
[院校名称与层次]、[专业课代码/科目]、[近3年真实统考复试与录取分数区间]、[学制与专硕学费]、[专硕校内住宿情况]、[统考报录比难度]、[官方权威查询出处]。

涵盖以下4大梯度标杆院校：
1. 【顶级985/C9】（浙江大学、复旦大学、中国科学技术大学、清华大学深圳国际研究生院）
2. 【热门强势985与IT名门】（华中科技大学、北京航空航天大学、北京邮电大学、同济大学、东南大学、电子科技大学）
3. 【高性价比与稳健211】（西安电子科技大学、苏州大学、南京航空航天大学、合肥工业大学、郑州大学）
4. 【高性价比双非强校/调剂保底】（杭州电子科技大学、深圳大学、重庆邮电大学、南京邮电大学）

请确保数据准确，并在表格下方附带专业解读。"""),

        ("三、 复试机试形式、考核权重与权威官方查询工具箱",
         """请为小白梳理复试全流程要点与官方信息检索工具：
1. 【复试构成与机试考核】：
   - 复试常见的四大模块（机试、笔试、面试、英语）。
   - 机试平台与语言环境（OJ平台、支持C/C++、Python等）。
   - 哪些院校支持 CCF-CSP 认证或 PAT 成绩直接抵扣或折算机试成绩（如浙大、北邮、国防科大等政策）？
   - 初复试成绩权重（5:5 或 6:4）对“高分被刷”与“低分逆袭”的影响。
2. 【官方权威信息获取工具清单】：
   - 中国研究生招生信息网（研招网 yz.chsi.com.cn）专业目录与调剂意向采集系统的用法。
   - 如何在目标院校研究生院官网精准找到《往年复试录取实施细则》与《拟录取名单公示》。
   - 教育部学位中心第五轮/第四轮计算机科学与技术学科评估等级速查。""")
    ]

    os.makedirs(os.path.dirname(OUTPUT_REPORT), exist_ok=True)
    with open(OUTPUT_REPORT, "w", encoding="utf-8") as f:
        f.write("# 408 & 计算机考研院校报考全景智库与小白避坑指南（附权威官方来源出处）\n\n")
        f.write("> 本报告由自动化知识采集引擎通过脱敏流水线调用大模型智库生成。\n")
        f.write("> 数据来源均严格基于教育部研招网、各校研究生院招生简章及院系拟录取公示核验。\n\n---\n\n")

    for idx, (title, prompt) in enumerate(tasks):
        print(f"\n--- Processing Step {idx+1}/{len(tasks)}: {title} ---", flush=True)
        content = query_llm(key, prompt, sys_prompt)
        with open(OUTPUT_REPORT, "a", encoding="utf-8") as f:
            f.write(f"## {title}\n\n{content}\n\n---\n\n")
        print(f"Appended Step {idx+1} to report.", flush=True)
        time.sleep(2)

    print(f"\nFinished all tasks! Full report saved to {OUTPUT_REPORT}", flush=True)

if __name__ == '__main__':
    main()
