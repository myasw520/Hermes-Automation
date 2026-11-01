# -*- coding: utf-8 -*-
"""
CS 408 核心考点与高频易错真题“变式题库通宵批量炼制工厂”
- 数据源：reports/master_408_graph_data.json 全量 408 知识图谱节点
- AI 引擎：ZeroGate zcode/glm-5.3 (深度推理思考链，背靠 25 亿 Token)
- 产出：
  1. SQLite 数据库：data/cs408_exam_vault.db (结构化考点、陷阱透析、变式真题库)
  2. Markdown 知识卡片：data/cs408_vault/{id}_{name}.md
- 支持断点续跑：已完成节点自动跳过，稳如磐石
"""

import sys
import os
import json
import time
import sqlite3
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
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
OUTPUT_MD_DIR = os.path.join(DATA_DIR, "cs408_vault")
DB_PATH = os.path.join(DATA_DIR, "cs408_exam_vault.db")
GRAPH_JSON_PATH = os.path.join(PROJECT_ROOT, "reports", "master_408_graph_data.json")

os.makedirs(OUTPUT_MD_DIR, exist_ok=True)

# 专属 ZeroGate ZCode 网关配置 (workbuddy/glm-5.3-flash 极速稳定 10s 出图，同享 25 亿 Token)
# 网关凭证统一从项目根 .env 读取（config_lib），不再硬编码
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "services"))
from config_lib import GATEWAY_URL as _CFG_GATEWAY_URL, GATEWAY_KEY as _CFG_GATEWAY_KEY
GATEWAY_URL = f"{_CFG_GATEWAY_URL.rstrip('/')}/chat/completions"
GATEWAY_KEY = _CFG_GATEWAY_KEY
MODEL_NAME = "workbuddy/glm-5.3-flash"

# ==================== 1. 数据库初始化 ====================

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS topics (
            id TEXT PRIMARY KEY,
            category TEXT,
            name TEXT,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS question_vault (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic_id TEXT,
            topic_name TEXT,
            category TEXT,
            core_summary TEXT,
            pitfalls_analysis TEXT,
            variant_choice_q TEXT,
            variant_choice_ans TEXT,
            variant_analysis_q TEXT,
            variant_analysis_ans TEXT,
            full_markdown TEXT,
            tokens_used INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (topic_id) REFERENCES topics(id)
        )
    """)
    conn.commit()
    conn.close()

def is_topic_completed(topic_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(1) FROM question_vault WHERE topic_id = ?", (topic_id,))
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0

def save_to_db(topic_info, ai_content, tokens_used=0):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR IGNORE INTO topics (id, category, name, description)
        VALUES (?, ?, ?, ?)
    """, (topic_info['id'], topic_info['cat'], topic_info['name'], topic_info['desc']))
    
    cursor.execute("""
        INSERT INTO question_vault (
            topic_id, topic_name, category, full_markdown, tokens_used
        ) VALUES (?, ?, ?, ?, ?)
    """, (topic_info['id'], topic_info['name'], topic_info['cat'], ai_content, tokens_used))
    
    conn.commit()
    conn.close()

# ==================== 2. AI 深度推理与变式题合成 ====================

def synthesize_topic(topic):
    """呼叫 zcode/glm-5.3 对 408 考点进行微米级深度解析与变式题合成"""
    t_id = topic.get('id', '')
    t_name = topic.get('name', '')
    t_cat = topic.get('cat', '')
    t_desc = topic.get('desc', '')
    
    prompt = (
        f"你是一位精通全国硕士研究生招生考试计算机科学专业基础（408 统考）的命题专家与资深金牌讲师。\n"
        f"请针对以下 408 核心重难点进行【微米级考点精讲】并合成【极具考场鉴别度的真题变式题】：\n\n"
        f"【当前考点名称】：{t_name}（所属科目：{t_cat.upper()}）\n"
        f"【知识点定义与边界】：{t_desc}\n\n"
        f"请按照以下规范格式输出完整的 Markdown 报告（禁止任何客套废话）：\n\n"
        f"# 📚 408 考点深度剖析与变式题库：{t_name}\n\n"
        f"## ⚡ 一、核心考点秒懂精髓\n"
        f"- 用最精炼、准确的计算机专业术语，总结本考点的底层核心运行机制。\n"
        f"- 给出 1~2 句考场快速解题记忆口诀或公式推导捷径。\n\n"
        f"## ⚠️ 二、考场高频杀手陷阱透析（考生最易丢分点）\n"
        f"- 深度拆解历年 408 考生在此考点最常见的 3 种思维误区与踩坑场景（如：数组越界、时空复杂度忽略常数项、Cache 缺失未写回、PV 信号量死锁盲区、滑动窗口收缩边界等）。\n\n"
        f"## 🎯 三、经典真题同源变式题 1（单项选择/计算题）\n"
        f"【题目背景】：基于真实 408 真题考察模型，更换数据与约束条件，设计一道单项选择题（包含 A, B, C, D 四个高迷惑性选项）。\n"
        f"【正确答案】：明确给出正确选项。\n"
        f"【深度解析】：给出逐项排除与正向严谨推导过程，指出干扰项的预设陷阱。\n\n"
        f"## 🚀 四、经典真题同源变式题 2（综合应用/大题设计）\n"
        f"【综合大题】：设计一道类似 408 算法/综合大题（附带明确的输入规格、输出要求及算法约束，如必须原地操作或 O(n) 时间）。\n"
        f"【解题思路】：分层次说明核心逻辑思路。\n"
        f"【参考代码/步骤】：提供标准严谨的 C/C++ 核心代码实现或详细推导步骤。\n"
        f"【时空复杂度分析】：严谨推导时间复杂度与空间复杂度。"
    )
    
    payload = json.dumps({
        "model": MODEL_NAME,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 3000,
        "temperature": 0.5
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
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            msg = data.get("choices", [{}])[0].get("message", {})
            content = msg.get("content", "").strip()
            usage = data.get("usage", {})
            tokens = usage.get("total_tokens", 0)
            elapsed = round(time.time() - t0, 1)
            return content, tokens, elapsed
    except Exception as e:
        print(f"[-] 请求网关生成失败 ({t_name}): {e}")
        return None, 0, 0

# ==================== 3. 主流水线循环 ====================

def run_vault_builder():
    print("=" * 65)
    print("🚀 启动 CS 408 变式题库通宵批量炼制工厂")
    print(f"⏰ 启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 接入网关: {GATEWAY_URL} (模型: {MODEL_NAME})")
    print(f"💾 数据存储: {DB_PATH}")
    print("=" * 65)
    
    init_db()
    
    if not os.path.exists(GRAPH_JSON_PATH):
        print(f"[-] 找不到考点图谱文件: {GRAPH_JSON_PATH}")
        return
        
    with open(GRAPH_JSON_PATH, "r", encoding="utf-8") as f:
        graph = json.load(f)
        
    nodes = [n for n in graph.get("nodes", []) if n.get("cat") != "center"]
    total_nodes = len(nodes)
    print(f"[*] 全量 408 考点节点数: {total_nodes} 个")
    
    completed_count = 0
    total_tokens_burnt = 0
    
    for idx, node in enumerate(nodes, 1):
        n_id = node.get("id")
        n_name = node.get("name")
        n_cat = node.get("cat", "408").upper()
        
        # 检查是否已完成
        if is_topic_completed(n_id):
            print(f"[{idx}/{total_nodes}] ⏩ 跳过已完成考点: [{n_cat}] {n_name}", flush=True)
            completed_count += 1
            continue
            
        print(f"\n[{idx}/{total_nodes}] 🧠 正在深度炼制考点: [{n_cat}] {n_name} ...", flush=True)
        content, tokens, elapsed = synthesize_topic(node)
        
        if content:
            # 1. 存入 SQLite
            save_to_db(node, content, tokens)
            total_tokens_burnt += tokens
            
            # 2. 存入独立 Markdown 文件
            clean_filename = f"{idx:02d}_{n_cat}_{n_id}.md"
            md_path = os.path.join(OUTPUT_MD_DIR, clean_filename)
            with open(md_path, "w", encoding="utf-8") as mf:
                mf.write(content)
                
            print(f"    [+] 炼制成功！耗时: {elapsed}s | 消耗 Token: {tokens} | 累计已烧: {total_tokens_burnt}", flush=True)
            print(f"    [+] Markdown 文件已保存: {clean_filename}", flush=True)
            completed_count += 1
        else:
            print(f"    [-] 考点 {n_name} 炼制失败，稍后可重新挂机断点续跑。", flush=True)
            
        # 适当休眠 1.5 秒，保证长连接平稳
        time.sleep(1.5)
        
    print("\n" + "=" * 65)
    print("🎉🎉 408 题库炼制批次完成！")
    print(f"📊 完成考点数: {completed_count}/{total_nodes}")
    print(f"🔥 本次累计消耗 Token: {total_tokens_burnt} (从 25 亿池中扣除)")
    print(f"📁 题库数据库已入库: {DB_PATH}")
    print("=" * 65)

if __name__ == "__main__":
    run_vault_builder()
