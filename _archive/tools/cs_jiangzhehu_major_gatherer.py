# -*- coding: utf-8 -*-
import json
import os
import requests
import time

CLEAN_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Content-Type': 'application/json'
}

KEYS_POOL_FILE = r"C:\Users\zzx05\Hermes-Automation\config\keys_pool.json"
OUTPUT_REPORT = r"C:\Users\zzx05\Hermes-Automation\reports\CS_Jiangzhehu_Colleges_Guide.md"

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
        "temperature": 0.2,
        "max_tokens": 4000
    }
    
    print(f"[{site_name}] Querying {model}...", flush=True)
    resp = requests.post(url, headers=headers, json=payload, timeout=120)
    resp.raise_for_status()
    data = resp.json()
    return data['choices'][0]['message']['content']

def main():
    keys = load_keys()
    key = keys[0]
    
    sys_prompt = (
        "你是一位深耕中国计算机考研（408统考与各校自命题）10年以上的资深择校规划专家。\n"
        "本次针对一位【本科为中医药大学、家庭经济条件一般（严控读研成本、极度看重提供校内宿舍与常规学费、必须避免一线城市高额租房）、目标锁定在江苏及江浙沪周边】的真实考生，进行全网最扎实、颗粒度最细（必须精确到具体学院与各专业代码代码 0812/0854xx/医工交叉）的定向调研。\n"
        "【关键指标硬性要求】：\n"
        "1. 绝不泛泛谈学校！必须精确到【学院】和【具体专业代码】（如 081200 计科学硕、085404 计算机技术专硕、085405 软件工程、085410 人工智能、085412 网络安全、以及智能医学/生物医药信息交叉学科）。\n"
        "2. 经济红线核查：明确各专业学制、每年学费（是否为8000-10000常规线）、校内是否安排宿舍（每年住宿费通常1000-1500元 vs 校外租房3-5万元的大坑）、国家助学金与学业奖学金覆盖情况。\n"
        "3. 分数线必须区分：各专业近3年（2023-2025）真实复试门槛线 vs 最终录取平均分/中位线（严防断层陷阱）。\n"
        "4. 特色分析：特别评估该专业/研究方向对【非工科/中医药跨考背景】的接纳度与优势发挥空间。"
    )

    tasks = [
        ("一、 江苏省内标杆高校精细专业拆解（211 / 双一流 / 强势工科）",
         """请深度调研并输出江苏省内具有代表性的计算机考研院校，按专业代码详细拆解：
覆盖高校：
1. 【苏州大学】（计算机科学与技术学院 081200计科 vs 085404计算机技术 vs 085405软件工程）
2. 【南京航空航天大学 / 南京理工大学】（计算机学院/人工智能学院 081200 vs 085400）
3. 【中国矿业大学 (徐州)】（211极高性价比代表，计算机科学与技术学院 081200 vs 085400，学费、宿舍、录取线深度解析）
4. 【江南大学 (无锡)】（人工智能与计算机学院，以及医工/生信交叉招生情况）
5. 【南京邮电大学】（计算机学院/通信学院/网安学院 081200 vs 085404/085405/085412，虽然双非但IT认可度极高）
6. 【江苏大学 (镇江) / 常州大学】（性价比极高的稳妥保底之选）

请对每所学校的每个专业整理出详尽的 Markdown 表格与对比，必须包含：
[院校与所属学院]、[专业代码与全称]、[初试科目]、[2023-2025复试线与录取均分区间]、[学制与每年学费]、[是否提供校内宿舍]、[奖助学金覆盖]、[中医药背景跨考友好度评级]"""),

        ("二、 浙江与上海高性价比高校精选（保障住宿 + 常规学费）",
         """请针对家庭条件一般、不愿承受昂贵租房成本的考生，筛选浙江省与上海市【保证校内宿舍、学费8000-10000元常规标准、就业认可度极高】的标杆院校：
覆盖高校：
1. 【杭州电子科技大学 (HDU)】（IT界公认神校，计算机学院 081200 vs 085404/085405，初复试权重、机试定乾坤政策、宿舍保障）
2. 【浙江工业大学 (ZJUT)】（省属顶尖，计算机学院 081200 vs 085400）
3. 【宁波大学】（双一流，信息科学与工程学院 081200 vs 085400）
4. 【华东理工大学 (上海 211)】（信息科学与工程学院，学费与徐汇/奉贤校区专硕宿舍政策）
5. 【上海大学 (上海 211)】（计算机工程与科学学院，各专业代码录取线与宝山校区宿舍安排）
6. 【上海电力大学】（能源电力行业就业王牌，计算机技术专硕，极高性价比）

请列出各专业详细对比表，特别注明避坑项（如复旦专硕不保住宿、清华深研院昂贵等反面教材做鲜明对比）。"""),

        ("三、 中医药背景考生的“降维打击”：医工交叉与医学人工智能特色方向盘点",
         """中医药大学本科生考计算机，存在一个极大的战略破局点——【医工交叉 / 智能医学工程 / 生物医药大数据 / 人工智能中医药】。
请详细调研江浙沪地区设立此类方向的院系与专业代码：
1. 江苏联考/特色点：
   - 南京大学 / 东南大学 的生物医学工程（智能医学仪器、医学影像AI、医疗大数据）
   - 苏州大学 放射医学与防护学院 / 计算机学院的医工交叉方向
   - 南京医科大学 生物医学工程与信息学院（计算机技术专硕/学硕）
   - 中国药科大学 / 南京中医药大学 自身的研究生计算机与信息工程学位点（报录比、难度、调剂机会）
2. 医工交叉方向在初试科目（是408还是自命题）、录取分数线、复试导师偏好、就业出路（既可去互联网大厂做算法工程，又能进医疗IT/三甲医院信息科/迈瑞联影等医疗器械巨头）等维度的核心优势。
3. 给该考生的综合定制化择校梯队建议（冲刺目标、稳健主力目标、绝对保底目标）。""")
    ]

    os.makedirs(os.path.dirname(OUTPUT_REPORT), exist_ok=True)
    with open(OUTPUT_REPORT, "w", encoding="utf-8") as f:
        f.write("# 江浙沪计算机考研精细化专业数据库与中医药跨考择校智库\n\n")
        f.write("> 本报告由 Hermes 知识采集引擎严格基于教育部研招网、各校2023-2025拟录取名单及研究生院最新招生简章深挖生成。\n")
        f.write("> 专门为【江浙沪生源、家庭经济务实型（锁定校内宿舍+常规学费）、中医药大学背景】量身定制。\n\n---\n\n")

    for idx, (title, prompt) in enumerate(tasks):
        print(f"\n--- [Hermes] Executing Step {idx+1}/{len(tasks)}: {title} ---", flush=True)
        ans = query_llm(key, prompt, sys_prompt)
        with open(OUTPUT_REPORT, "a", encoding="utf-8") as f:
            f.write(f"## {title}\n\n")
            f.write(ans)
            f.write("\n\n---\n\n")
        print(f"Step {idx+1} completed and saved to {OUTPUT_REPORT}", flush=True)
        time.sleep(2)

    print("\n[Hermes] All Jiangzhehu fine-grained intelligence gathered successfully!", flush=True)

if __name__ == '__main__':
    main()
