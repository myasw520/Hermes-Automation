#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CS 408 Exam Universe Generator (408 计算机考研千题宇宙与全真模拟卷引擎)
====================================================================
批量炼制海量高难度变式题库：
- 46 个考点全覆盖
- 每个考点深度生成高陷阱选择题 (含选项逐项排雷分析) + 综合设计大题 (含评分标准与完整代码)
- 自动编排标准 150 分全真模拟卷
"""

import os
import sys
import json
import time
import sqlite3
import argparse
import urllib.request
import urllib.error
from datetime import datetime

# Windows 终端 UTF-8 编码安全重置
try:
    if sys.stdout.encoding.lower() != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
    if sys.stderr.encoding.lower() != 'utf-8':
        sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

import functools
print = functools.partial(print, flush=True)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, "data", "cs408_exam_vault.db")
GRAPH_JSON_PATH = os.path.join(PROJECT_ROOT, "reports", "master_408_graph_data.json")
UNIVERSE_DIR = os.path.join(PROJECT_ROOT, "data", "cs408_universe")
MOCK_DIR = os.path.join(PROJECT_ROOT, "reports", "cs408_mock_exams")

GATEWAY_URL = os.environ.get("GATEWAY_URL", "http://100.114.18.45:7863/v1/chat/completions")
# 网关凭证统一从项目根 .env 读取（config_lib），不再硬编码
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "services"))
from config_lib import GATEWAY_KEY as _ENV_GATEWAY_KEY
GATEWAY_KEY = os.environ.get("GATEWAY_KEY") or _ENV_GATEWAY_KEY
MODEL_NAME = os.environ.get("MODEL_NAME", "workbuddy/glm-5.3-flash")

def init_tables():
    os.makedirs(UNIVERSE_DIR, exist_ok=True)
    os.makedirs(MOCK_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS universe_mcq (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic_id TEXT,
            topic_name TEXT,
            category TEXT,
            stem TEXT,
            option_a TEXT,
            option_b TEXT,
            option_c TEXT,
            option_d TEXT,
            answer TEXT,
            trap_analysis TEXT,
            full_explanation TEXT,
            difficulty INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS universe_comprehensive (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic_id TEXT,
            topic_name TEXT,
            category TEXT,
            title TEXT,
            stem TEXT,
            sub_questions TEXT,
            rubric TEXT,
            solution_code TEXT,
            explanation TEXT,
            score INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def call_llm(prompt_text, max_retries=3):
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "user", "content": prompt_text}
        ],
        "temperature": 0.4
    }
    data_bytes = json.dumps(payload).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GATEWAY_KEY}"
    }

    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(GATEWAY_URL, data=data_bytes, headers=headers)
            t0 = time.time()
            with urllib.request.urlopen(req, timeout=120) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                elapsed = time.time() - t0
                content = result["choices"][0]["message"]["content"].strip()
                tokens = result.get("usage", {}).get("total_tokens", 0)
                return content, tokens, elapsed
        except Exception as e:
            print(f"[-] 请求错误 (重试 {attempt+1}/{max_retries}): {e}")
            time.sleep(3)
    return None, 0, 0

def generate_topic_universe(node, mcq_count=5, comp_count=1):
    topic_id = node["id"]
    topic_name = node["name"]
    category = node["cat"]
    desc = node["desc"]

    prompt = f"""你是一位命题水平极高、深谙教育部计算机考研 408 统考出题套路的名校命题组组长。
现在请针对以下核心考点，高密度生成【{mcq_count} 道高陷阱单选题】与【{comp_count} 道综合设计/计算大题】。

【考点信息】
- 编号: {topic_id}
- 科目/考点: {category} - {topic_name}
- 考点核心大纲: {desc}

【命题原则】
1. 绝不出死记硬背概念题，只出考察底层机制理解、边界条件、反直觉陷阱、软硬件协同设计的深度好题。
2. 单选题必须详细给出每一个错误选项（A/B/C/D）的致命陷阱剖析。
3. 综合大题必须包含：严谨题干、分步小问、官方考研阅卷踩分标准（如扣分点细则）、完整 C/C++ 代码或精确计算推导。
4. 【极其重要 JSON 规范】：所有字符串内容中绝对严禁出现未转义的英文双引号！若需引用术语，必须统一使用中文引号「」或《》或单引号 ''，确保 JSON 解析 100% 成功。

请严格输出合法的 JSON 格式（不得输出包含 JSON 以外的多余闲话）：
```json
{{
  "mcqs": [
    {{
      "stem": "题干内容...",
      "options": {{
        "A": "选项A内容",
        "B": "选项B内容",
        "C": "选项C内容",
        "D": "选项D内容"
      }},
      "answer": "B",
      "trap_analysis": "选项A陷阱：...；选项C陷阱：...；选项D陷阱：...",
      "full_explanation": "深度解析与解题破局思维...",
      "difficulty": 4 // 1~5 难度
    }}
  ],
  "comprehensive": [
    {{
      "title": "综合大题标题",
      "stem": "大题背景与上下文...",
      "sub_questions": [
        "(1) 第一小问...",
        "(2) 第二小问..."
      ],
      "rubric": "踩分标准细则（分步给分原则）...",
      "solution_code": "// 完整规范 C/C++ 代码实现或详细推导矩阵\\n...",
      "explanation": "系统级破局分析与命题陷阱点评",
      "score": 15
    }}
  ]
}}
```"""

    content, tokens, elapsed = call_llm(prompt)
    if not content:
        return None, 0, 0

    clean_json = content
    if "```json" in clean_json:
        clean_json = clean_json.split("```json")[1].split("```")[0].strip()
    elif "```" in clean_json:
        clean_json = clean_json.split("```")[1].split("```")[0].strip()

    try:
        data = json.loads(clean_json)
        return data, tokens, elapsed
    except Exception as e:
        # 尝试容错修复双引号
        try:
            import re
            # 替换非键值对分界处的双引号
            fixed = re.sub(r'(?<![:,\{\[\s])"(?![:,\}\]\s])', '“', clean_json)
            data = json.loads(fixed)
            return data, tokens, elapsed
        except Exception:
            print(f"[-] JSON 解析异常: {e} | 内容片段: {content[:150]}")
            return None, tokens, elapsed

def save_universe_data(node, data):
    topic_id = node["id"]
    topic_name = node["name"]
    category = node["cat"]

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 存 MCQ
    for mcq in data.get("mcqs", []):
        opts = mcq.get("options", {})
        cursor.execute("""
            INSERT INTO universe_mcq (
                topic_id, topic_name, category, stem,
                option_a, option_b, option_c, option_d,
                answer, trap_analysis, full_explanation, difficulty
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            topic_id, topic_name, category, mcq.get("stem", ""),
            opts.get("A", ""), opts.get("B", ""), opts.get("C", ""), opts.get("D", ""),
            mcq.get("answer", ""), mcq.get("trap_analysis", ""),
            mcq.get("full_explanation", ""), mcq.get("difficulty", 3)
        ))

    # 存 综合大题
    for comp in data.get("comprehensive", []):
        sub_q_str = "\n".join(comp.get("sub_questions", []))
        cursor.execute("""
            INSERT INTO universe_comprehensive (
                topic_id, topic_name, category, title, stem,
                sub_questions, rubric, solution_code, explanation, score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            topic_id, topic_name, category, comp.get("title", ""),
            comp.get("stem", ""), sub_q_str, comp.get("rubric", ""),
            comp.get("solution_code", ""), comp.get("explanation", ""),
            comp.get("score", 15)
        ))

    conn.commit()
    conn.close()

    # 生成 Markdown 讲义备份 (清理文件名中的非法字符如 / \ : 等)
    import re
    safe_topic_name = re.sub(r'[\\/*?:"<>|]', '_', topic_name.replace(' ', '_'))
    md_filename = f"{topic_id}_{category}_{safe_topic_name}.md"
    md_path = os.path.join(UNIVERSE_DIR, md_filename)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# 📘 408 核心考点真题宇宙: [{category}] {topic_name}\n\n")
        f.write(f"> 大纲描述: {node['desc']}\n\n---\n\n")
        f.write("## 🎯 高陷阱单选专项演练\n\n")
        for idx, m in enumerate(data.get("mcqs", []), 1):
            opts = m.get("options", {})
            f.write(f"### 第 {idx} 题 (难度: {'⭐'*m.get('difficulty', 3)})\n")
            f.write(f"**题干**：{m.get('stem')}\n\n")
            f.write(f"- A. {opts.get('A')}\n- B. {opts.get('B')}\n- C. {opts.get('C')}\n- D. {opts.get('D')}\n\n")
            f.write(f"<details><summary><b>👉 查看答案与致命陷阱拆解</b></summary>\n\n")
            f.write(f"**【正确答案】**: `{m.get('answer')}`\n\n")
            f.write(f"**【各选项排雷剖析】**:\n{m.get('trap_analysis')}\n\n")
            f.write(f"**【深度解析】**:\n{m.get('full_explanation')}\n\n")
            f.write("</details>\n\n---\n\n")

        f.write("## 🏆 综合应用与算法设计大题\n\n")
        for idx, c in enumerate(data.get("comprehensive", []), 1):
            f.write(f"### 大题 {idx}: {c.get('title')} ({c.get('score', 15)} 分)\n\n")
            f.write(f"**【背景与题干】**:\n{c.get('stem')}\n\n")
            f.write("**【问题清单】**:\n")
            for sq in c.get("sub_questions", []):
                f.write(f"- {sq}\n")
            f.write("\n<details><summary><b>👉 查看踩分标准与标准参考实现</b></summary>\n\n")
            f.write(f"**【考研阅卷踩分细则】**:\n{c.get('rubric')}\n\n")
            if c.get("solution_code"):
                f.write(f"**【核心算法/推导实现】**:\n```cpp\n{c.get('solution_code')}\n```\n\n")
            f.write(f"**【命题人解题思维点拨】**:\n{c.get('explanation')}\n\n")
            f.write("</details>\n\n")

def assemble_mock_exam(exam_num=1):
    """从宇宙题库中随机组卷一套 150 分标准 408 全真模拟卷"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(1) FROM universe_mcq")
    mcq_total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(1) FROM universe_comprehensive")
    comp_total = cursor.fetchone()[0]

    if mcq_total < 40 or comp_total < 7:
        conn.close()
        return None

    # 按科目抽取 40 道选择题 (DS: 11, COA: 11, OS: 10, CN: 8)
    quota_mcq = {"ds": 11, "coa": 11, "os": 10, "cn": 8}
    mcqs = []
    for cat, num in quota_mcq.items():
        cursor.execute("""
            SELECT id, topic_name, category, stem, option_a, option_b, option_c, option_d,
                   answer, trap_analysis, full_explanation
            FROM universe_mcq WHERE LOWER(category) = LOWER(?) ORDER BY RANDOM() LIMIT ?
        """, (cat, num))
        mcqs.extend(cursor.fetchall())

    # 抽取 7 道大题 (DS: 2, COA: 2, OS: 2, CN: 1)
    quota_comp = {"ds": 2, "coa": 2, "os": 2, "cn": 1}
    comps = []
    for cat, num in quota_comp.items():
        cursor.execute("""
            SELECT id, topic_name, category, title, stem, sub_questions, rubric, solution_code, explanation, score
            FROM universe_comprehensive WHERE LOWER(category) = LOWER(?) ORDER BY RANDOM() LIMIT ?
        """, (cat, num))
        comps.extend(cursor.fetchall())
    conn.close()

    # 组装试卷 Markdown
    now_str = datetime.now().strftime("%Y-%m-%d")
    exam_title = f"2026 年全国硕士研究生入学统考计算机 408 全真模拟冲刺卷 (第 {exam_num:02d} 套)"
    exam_md_path = os.path.join(MOCK_DIR, f"408_MOCK_EXAM_{exam_num:02d}.md")

    with open(exam_md_path, "w", encoding="utf-8") as f:
        f.write(f"# 📝 {exam_title}\n")
        f.write(f"> 考试时间: 180 分钟 | 满分: 150 分 | 生成日期: {now_str}\n\n")
        f.write("---\n\n## 一、单项选择题（第 1~40 小题，每小题 2 分，共 80 分）\n\n")
        for i, m in enumerate(mcqs, 1):
            f.write(f"**{i}.** [{m[2]}] {m[3]}\n")
            f.write(f"- A. {m[4]}\n- B. {m[5]}\n- C. {m[6]}\n- D. {m[7]}\n\n")

        f.write("---\n\n## 二、综合应用题（第 41~47 小题，共 70 分）\n\n")
        for i, c in enumerate(comps, 41):
            f.write(f"### 第 {i} 题：{c[3]}（本题共 {c[9]} 分，所属科目：{c[2]}）\n\n")
            f.write(f"{c[4]}\n\n")
            f.write(f"**【问题清单】**:\n{c[5]}\n\n")

        f.write("\n\n---\n# 🔑 试题全解、陷阱排查与阅卷评分细则\n\n")
        f.write("## 一、单项选择题答案与逐项解析\n\n")
        for i, m in enumerate(mcqs, 1):
            f.write(f"### 第 {i} 题：参考答案 `{m[8]}`\n")
            f.write(f"- **选项排雷分析**：{m[9]}\n")
            f.write(f"- **解题思路详解**：{m[10]}\n\n")

        f.write("## 二、综合应用题评分标准与参考解答\n\n")
        for i, c in enumerate(comps, 41):
            f.write(f"### 第 {i} 题：{c[3]}（满分 {c[9]} 分）\n")
            f.write(f"- **【阅卷采分点细则】**：\n{c[6]}\n\n")
            if c[7]:
                f.write(f"- **【标准算法实现/推导】**：\n```cpp\n{c[7]}\n```\n\n")
            f.write(f"- **【命题组深度总结】**：\n{c[8]}\n\n")

    print(f"[+] 模拟卷已生成: {exam_md_path}")
    return exam_md_path

def is_topic_completed(topic_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM universe_mcq WHERE topic_id = ?", (topic_id,))
    row = cursor.fetchone()
    conn.close()
    return row is not None

def run_universe_factory(target_nodes=None):
    init_tables()
    with open(GRAPH_JSON_PATH, "r", encoding="utf-8") as f:
        graph_data = json.load(f)

    nodes = [n for n in graph_data.get("nodes", []) if n.get("cat") != "center"]
    if target_nodes:
        nodes = nodes[:target_nodes]

    total = len(nodes)
    print(f"[*] 🚀 启动 408 计算机考研千题宇宙生成工厂 (共 {total} 个核心考点)")
    print(f"[*] 接入网关: {GATEWAY_URL} | 模型: {MODEL_NAME}")

    accum_tokens = 0
    for idx, node in enumerate(nodes, 1):
        if is_topic_completed(node["id"]):
            print(f"[{idx}/{total}] ⏩ 考点已在题库中，断点续传跳过: [{node['cat']}] {node['name']}")
            continue

        print(f"\n[{idx}/{total}] ⚡ 正在批量炼制考点千题: [{node['cat']}] {node['name']} ...")
        t0 = time.time()
        data, tokens, elapsed = generate_topic_universe(node, mcq_count=5, comp_count=1)
        if data:
            accum_tokens += tokens
            save_universe_data(node, data)
            print(f"    [+] 炼制成功！耗时: {elapsed:.1f}s | 消耗 Token: {tokens} | 累计已烧: {accum_tokens}")
            print(f"        已存入 5 道高陷阱单选 + 1 道综合大题")
        else:
            print(f"    [-] 考点生成失败，跳过。")
        time.sleep(1)

    print("\n🎉 考点批量炼制完毕！正在自动编排第 1 套 150 分全真模拟冲刺卷...")
    assemble_mock_exam(exam_num=1)
    print(f"🔥 全流程结束！本次千题宇宙累计燃烧 Token: {accum_tokens}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CS 408 Universe Generator")
    parser.add_argument("--nodes", type=int, default=None, help="限定生成考点数 (默认全部)")
    parser.add_argument("--assemble", type=int, default=None, help="仅组卷 (指定试卷编号)")
    args = parser.parse_args()

    if args.assemble:
        assemble_mock_exam(args.assemble)
    else:
        run_universe_factory(target_nodes=args.nodes)
