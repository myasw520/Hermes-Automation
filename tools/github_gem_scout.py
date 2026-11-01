#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub ~100-Star Hidden Gem Scout & Classifier (百星小众神级仓库雷达与分类器)
========================================================================
专门挖掘并深度分类 50~300 星左右的硬核低调宝藏仓库，过滤几万星的膨胀课件与营销玩具。
集成 ZeroGate (workbuddy/glm-5.3-flash) 进行深度痛点剖析与分类评估。
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

# Windows 终端 UTF-8 编码防爆处理
try:
    if sys.stdout.encoding.lower() != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
    if sys.stderr.encoding.lower() != 'utf-8':
        sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

# 全局强制标准输出即时刷新 (避免后台日志缓冲)
import functools
print = functools.partial(print, flush=True)

DB_PATH = os.path.join("data", "github_gems.db")
REPORTS_DIR = os.path.join("reports", "github_gems")
CARDS_DIR = os.path.join(REPORTS_DIR, "cards")

GATEWAY_URL = os.environ.get("GATEWAY_URL", "http://100.114.18.45:7863/v1")
# 网关凭证统一从项目根 .env 读取（config_lib），不再硬编码
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "services"))
from config_lib import GATEWAY_KEY as _ENV_GATEWAY_KEY
GATEWAY_KEY = os.environ.get("GATEWAY_KEY") or _ENV_GATEWAY_KEY
MODEL_EVAL = os.environ.get("MODEL_EVAL", "workbuddy/glm-5.3-flash")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")

# 预设高含金量探索主题
DEFAULT_QUERIES = [
    {"name": "Windows原生优化与调教", "q": "topic:windows+topic:tool+stars:50..250+fork:false"},
    {"name": "Rust极简高性能CLI", "q": "topic:cli+language:rust+stars:60..260+fork:false"},
    {"name": "逆向工程与安全取证", "q": "topic:reverse-engineering+stars:50..280+fork:false"},
    {"name": "极客终端TUI应用", "q": "topic:tui+stars:50..250+fork:false"},
    {"name": "工作流与效率自动化", "q": "topic:automation+topic:productivity+stars:50..260+fork:false"},
    {"name": "系统运维与硬件监控", "q": "topic:sysadmin+stars:50..250+fork:false"},
    {"name": "网络协议与私有代理工具", "q": "topic:network-tool+stars:50..250+fork:false"},
    {"name": "本地轻量级AI/LLM工具", "q": "topic:local-ai+stars:50..300+fork:false"},
    {"name": "极简极客轻量级替代品", "q": "topic:minimal+stars:50..250+fork:false"},
    {"name": "Go语言网络抓取与实用微工具", "q": "topic:scraper+language:go+stars:50..250+fork:false"},
    {"name": "音视频与媒体极客工具", "q": "topic:media-tool+stars:50..250+fork:false"},
]

# 垃圾/营销/课件黑名单关键词
JUNK_KEYWORDS = [
    "awesome", "course", "homework", "curriculum", "interview", "leetcode", 
    "resume", "roadmap", "cheatsheet", "collection", "book", "tutorial", 
    "learn-", "study", "notes", "assignment", "guide", "syllabus", "exam"
]

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    os.makedirs(CARDS_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS github_gems (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT UNIQUE,
            html_url TEXT,
            description TEXT,
            stars INTEGER,
            forks INTEGER,
            language TEXT,
            topics TEXT,
            pushed_at TEXT,
            is_gem INTEGER,
            gem_score INTEGER,
            category TEXT,
            pain_point TEXT,
            why_gem TEXT,
            target_audience TEXT,
            difficulty TEXT,
            verdict TEXT,
            highlights TEXT,
            created_at TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scan_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query_name TEXT,
            query_str TEXT,
            found_count INTEGER,
            scanned_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

def is_repo_analyzed(full_name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM github_gems WHERE full_name = ?", (full_name,))
    row = cursor.fetchone()
    conn.close()
    return row is not None

def fetch_github_search(query_str, per_page=15):
    """通过 GitHub Search API 搜索仓库"""
    url = f"https://api.github.com/search/repositories?q={query_str}&sort=updated&order=desc&per_page={per_page}"
    headers = {
        "User-Agent": "Hermes-Hidden-Gem-Scout/1.0",
        "Accept": "application/vnd.github.v3+json"
    }
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            return data.get("items", [])
    except Exception as e:
        print(f"[-] GitHub 搜索出错 [{query_str[:30]}...]: {e}")
        return []

def fetch_readme(full_name):
    """优先通过 raw.githubusercontent.com 抓取 README，无API限制"""
    branches = ["HEAD", "main", "master"]
    readme_names = ["README.md", "readme.md", "README.rst", "README.txt"]
    
    headers = {"User-Agent": "Hermes-Hidden-Gem-Scout/1.0"}
    for branch in branches:
        for rname in readme_names:
            raw_url = f"https://raw.githubusercontent.com/{full_name}/{branch}/{rname}"
            try:
                req = urllib.request.Request(raw_url, headers=headers)
                with urllib.request.urlopen(req, timeout=8) as resp:
                    text = resp.read().decode('utf-8', errors='ignore')
                    if len(text.strip()) > 100:
                        return text[:5000] # 取前5000字足以研判架构与痛点
            except Exception:
                continue
    return ""

def is_obvious_junk(repo):
    """根据名称、描述和话题做初筛"""
    name = repo.get("name", "").lower()
    desc = (repo.get("description") or "").lower()
    topics = " ".join(repo.get("topics", [])).lower()
    combo = f"{name} {desc} {topics}"

    for kw in JUNK_KEYWORDS:
        if kw in name or f" {kw} " in f" {desc} ":
            return True
            
    # 过滤空描述或描述极短
    if len(desc.strip()) < 5:
        return True
        
    return False

def evaluate_repo_with_llm(repo, readme_text):
    """通过 ZeroGate LLM 进行毒舌极客深度评测与分类"""
    meta_info = {
        "name": repo["full_name"],
        "url": repo["html_url"],
        "stars": repo["stargazers_count"],
        "forks": repo["forks_count"],
        "language": repo["language"] or "Unknown",
        "topics": repo.get("topics", []),
        "description": repo.get("description") or "无",
        "pushed_at": repo.get("pushed_at") or "Unknown"
    }

    user_prompt = f"""你是一个极其敏锐、品味挑剔的资深极客架构师与开源猎头。
你深知 GitHub 上很多几万星的项目只是面试刷题、资料合集、或者臃肿臃肿的商业全家桶，
而真正解决特定恶心痛点、轻量无依赖、代码优雅硬核的“神仙宝藏”，往往深藏在 50~300 星左右的低调小众仓库里！

现在请对以下约 100 星左右的开源仓库进行深度研判与分类：

【仓库基本信息】
- 仓库名称: {meta_info['name']}
- 仓库链接: {meta_info['url']}
- 星标数量: {meta_info['stars']} Stars (Forks: {meta_info['forks']})
- 主力语言: {meta_info['language']}
- 官方话题: {", ".join(meta_info['topics'])}
- 官方简介: {meta_info['description']}
- 最近更新: {meta_info['pushed_at']}

【README 节选 (前 4000 字符)】
{readme_text if readme_text else "(该项目无详细 README 或使用非标准格式，请主要依据项目名称、描述及话题推断)"}

【评测要求】
请从以下分类维度之一给出硬核归类：
1. 🛠️ 系统底层与原生增强 (OS & Native Utilities)
2. ⌨️ 极客CLI与TUI终端神器 (CLI / TUI Geek Tools)
3. 🕵️ 逆向工程与安全取证 (Reverse Engineering & Security)
4. ⚡ 开发者效率与工作流自动化 (Dev Productivity & Automation)
5. 📦 极简轻量替代品 (Minimalist Drop-in Replacements for Bloatware)
6. 🌐 网络抓取与协议工具 (Network / Scraper / Proxy)
7. 🤖 本地AI轻量工具 (Local AI & Micro Tooling)
8. 🎮 游戏黑科技与媒体处理 (Gaming & Media Hacks)
9. 🗑️ 垃圾玩具/废弃项目 (Junk / Toy / Outdated)

请严格以 JSON 格式输出，不得包含额外 Markdown 标签以外的文字：
```json
{{
  "is_gem": true, // 若是真正有价值的好东西填 true，若是玩具/作业/无意义轮子填 false
  "gem_score": 8, // 宝藏指数 1~10 分 (8分以上为重磅宝藏)
  "category": "极客CLI与TUI终端神器",
  "pain_point": "一句话精准指出它解决了什么恶心痛点 (20-40字)",
  "why_gem": "相比几万星的臃肿软件，它的降维优势是什么？(如单文件无依赖/极低内存/无需Docker/纯本地无遥测等)",
  "target_audience": "最适合哪类人群 (如: Windows洁癖党 / 终端重度用户 / 独立开发者 / 逆向老手)",
  "difficulty": "开箱即用 / 需基础配置 / 极客编译",
  "verdict": "一句话毒舌而客观的极客终审评语",
  "highlights": [
    "核心亮点1",
    "核心亮点2",
    "核心亮点3"
  ]
}}
```"""

    payload = {
        "model": MODEL_EVAL,
        "messages": [
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.3
    }

    req = urllib.request.Request(
        f"{GATEWAY_URL}/chat/completions",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {GATEWAY_KEY}"
        },
        data=json.dumps(payload).encode("utf-8")
    )

    try:
        t0 = time.time()
        with urllib.request.urlopen(req, timeout=45) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            elapsed = time.time() - t0
            content = data["choices"][0]["message"]["content"].strip()
            
            # 解析 JSON
            clean_json = content
            if "```json" in clean_json:
                clean_json = clean_json.split("```json")[1].split("```")[0].strip()
            elif "```" in clean_json:
                clean_json = clean_json.split("```")[1].split("```")[0].strip()
                
            res = json.loads(clean_json)
            res["_elapsed"] = round(elapsed, 1)
            res["_tokens"] = data.get("usage", {}).get("total_tokens", 0)
            return res
    except Exception as e:
        print(f"[-] LLM 研判失败 [{meta_info['name']}]: {e}")
        return None

def save_gem_to_db(repo, eval_res):
    """保存宝藏信息到 SQLite"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO github_gems (
            full_name, html_url, description, stars, forks, language, topics, pushed_at,
            is_gem, gem_score, category, pain_point, why_gem, target_audience,
            difficulty, verdict, highlights, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        repo["full_name"],
        repo["html_url"],
        repo.get("description") or "",
        repo["stargazers_count"],
        repo["forks_count"],
        repo.get("language") or "Unknown",
        json.dumps(repo.get("topics", []), ensure_ascii=False),
        repo.get("pushed_at") or "",
        1 if eval_res.get("is_gem") else 0,
        eval_res.get("gem_score", 0),
        eval_res.get("category", "未分类"),
        eval_res.get("pain_point", ""),
        eval_res.get("why_gem", ""),
        eval_res.get("target_audience", ""),
        eval_res.get("difficulty", "开箱即用"),
        eval_res.get("verdict", ""),
        json.dumps(eval_res.get("highlights", []), ensure_ascii=False),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()
    conn.close()

def generate_markdown_reports():
    """汇总 SQLite 中的宝藏并生成精美分类报告及小黑盒推文"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 查所有有效宝藏 (is_gem=1 且 gem_score >= 6)
    cursor.execute('''
        SELECT full_name, html_url, stars, language, gem_score, category,
               pain_point, why_gem, target_audience, difficulty, verdict, highlights
        FROM github_gems
        WHERE is_gem = 1 AND gem_score >= 6
        ORDER BY gem_score DESC, stars ASC
    ''')
    gems = cursor.fetchall()
    
    cursor.execute('SELECT COUNT(1) FROM github_gems')
    total_scanned = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(1) FROM github_gems WHERE is_gem = 1')
    total_gems = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(1) FROM github_gems WHERE gem_score >= 8')
    top_gems = cursor.fetchone()[0]
    conn.close()

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # 1. 生成总览 Dashboard: GEM_RADAR_SUMMARY.md
    summary_md = f"""# 🧭 GitHub ~100-Star 百星小众神仙仓库雷达
> *扫描时间: {now_str} | 已深度研判仓库: {total_scanned} 个 | 入库宝藏: {total_gems} 个 | S级高分神作: {top_gems} 个*

---

### 💡 为什么盯住 100 星左右的仓库？
在当下的 GitHub 生态中，动辄数万星的项目充斥着大量**刷题面经、课件资料、营销合集、或者臃肿到必须拉取几十个 Docker 容器的商业巨无霸**。
而真正属于**独立极客与黑客精神**的作品——单文件零依赖、C/Rust极速实现、专注解决某一个具体顽疾、无遥测无广告的神器，往往在初期只有 **50~300 颗星**！

---

## 🏆 S级神仙宝藏榜 (评分 ≥ 8)

| 评分 | 仓库名称 | 语言 | 星标 | 核心痛点与降维优势 | 类别 |
| :---: | :--- | :---: | :---: | :--- | :--- |
"""
    for g in gems:
        if g[4] >= 8:
            summary_md += f"| ⭐ **{g[4]}/10** | [{g[0]}]({g[1]}) | `{g[3]}` | `{g[2]}★` | **{g[6]}**<br><small style='color:gray'>{g[7]}</small> | `{g[5]}` |\n"

    summary_md += "\n---\n\n## 📂 分类宝藏速查索引\n\n"
    
    # 按分类聚合
    by_category = {}
    for g in gems:
        cat = g[5]
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(g)

    for cat, items in by_category.items():
        summary_md += f"### {cat} ({len(items)} 个)\n"
        for item in items:
            summary_md += f"- **[{item[0]}]({item[1]})** (`{item[3]}` | {item[2]}★ | 评级: {item[4]}/10)\n"
            summary_md += f"  - **解决痛点**: {item[6]}\n"
            summary_md += f"  - **降维优势**: {item[7]}\n"
            summary_md += f"  - **极客终审**: *\"{item[10]}\"*\n"
        summary_md += "\n"

    with open(os.path.join(REPORTS_DIR, "GEM_RADAR_SUMMARY.md"), "w", encoding="utf-8") as f:
        f.write(summary_md)

    # 2. 生成小黑盒直球风格推文: xiaoheihe_github_gems.md
    post_md = f"""# 别总盯着那些几万星的垃圾了！挖到了几个百星左右的极客神仙仓库

兄弟们好，我是老张！[cube_点赞]

平时在 GitHub 上找工具，是不是经常被那些几万星的“神作”恶心到？一打开全是几百页的面经资料，要么就是个破工具还要你起个几十 G 的 Docker 容器，后台挂满遥测和广告，内存直接吃饱饱。[cube_吐血]

反而是那些 **100 星左右的小众仓库**，藏着大量真正懂极客痛点的狠活：**纯原生无依赖、单文件免安装、C/Rust 跑满极速、专治恶心顽疾**！今天从雷达里捞几个硬核宝藏出来给兄弟们验验货！[cube_挑衅]

---

"""
    s_gems = [g for g in gems if g[4] >= 7][:5]
    for idx, g in enumerate(s_gems, 1):
        highlights = json.loads(g[11]) if g[11] else []
        hl_str = "、".join(highlights) if highlights else "单文件极简、无依赖"
        post_md += f"""## {idx}. [{g[0]}]({g[1]}) —— {g[5]}
- **当前星标**: `{g[2]} Stars` | **主力语言**: `{g[3]}` | **上手门槛**: `{g[9]}`
- **这玩意治什么病**: {g[6]}
- **为什么比臃肿大厂香**: {g[7]}
- **核心亮点**: {hl_str}
- **老哥毒舌锐评**: [cube_思考] *\"{g[10]}\"*

---

"""

    post_md += """
### 总结与自取
有需要的哥们直接顺着链接去 GitHub 自行下载 Release。好东西不用搞花里胡哨的宣传，单文件丢进环境变量就能用一年！[cube_酷]

你们平时遇到过什么冷门但离不开的百星小神器？评论区甩出来交流交流！[cube_干杯]
"""
    with open(os.path.join(REPORTS_DIR, "xiaoheihe_github_gems.md"), "w", encoding="utf-8") as f:
        f.write(post_md)

    print(f"[+] 报表生成完毕: {os.path.join(REPORTS_DIR, 'GEM_RADAR_SUMMARY.md')}")
    print(f"[+] 小黑盒文案生成: {os.path.join(REPORTS_DIR, 'xiaoheihe_github_gems.md')}")

def run_scout(queries=None, target_gems=20, continuous=False):
    """主挖掘流程"""
    init_db()
    if not queries:
        queries = DEFAULT_QUERIES

    total_added = 0
    print(f"[*] 🚀 启动百星小众神级仓库雷达 (目标发现: {target_gems} 个宝藏)")
    print(f"[*] 网关接口: {GATEWAY_URL} | 研判模型: {MODEL_EVAL}")

    while True:
        for q_obj in queries:
            q_name = q_obj["name"]
            q_str = q_obj["q"]
            print(f"\n📡 正在雷达扫描主题: [{q_name}] -> {q_str}")
            
            repos = fetch_github_search(q_str, per_page=15)
            print(f"    共检索到 {len(repos)} 个候选仓库")

            for repo in repos:
                full_name = repo["full_name"]
                stars = repo["stargazers_count"]
                
                if is_repo_analyzed(full_name):
                    continue

                if is_obvious_junk(repo):
                    # 记录为垃圾跳过
                    print(f"    [x] 跳过垃圾/课件/空描述仓库: {full_name} ({stars}★)")
                    continue

                print(f"    🔍 正在挖掘研判: {full_name} ({stars}★ | {repo.get('language')}) ...")
                
                # 抓取 README
                readme_text = fetch_readme(full_name)
                
                # LLM 深度研判
                eval_res = evaluate_repo_with_llm(repo, readme_text)
                if not eval_res:
                    continue

                # 存库
                save_gem_to_db(repo, eval_res)
                
                score = eval_res.get("gem_score", 0)
                is_gem = eval_res.get("is_gem", False)
                cat = eval_res.get("category", "未分类")
                
                if is_gem and score >= 6:
                    total_added += 1
                    status_badge = "🔥 S级宝藏" if score >= 8 else "✨ 入选宝藏"
                    print(f"    [+] {status_badge} [{score}/10] 分类: {cat} | 耗时: {eval_res.get('_elapsed')}s | 消耗 Token: {eval_res.get('_tokens')}")
                    print(f"        痛点: {eval_res.get('pain_point')}")
                    print(f"        优势: {eval_res.get('why_gem')}")
                else:
                    print(f"    [-] 过滤普通/低质轮子 [{score}/10]: {eval_res.get('verdict')}")

                # 生成最新报告
                generate_markdown_reports()

                if not continuous and total_added >= target_gems:
                    print(f"\n🎉 目标达成！本次已挖掘入库 {total_added} 个高含金量神级小众仓库！")
                    return

                # 避免频繁刷接口
                time.sleep(2)

            time.sleep(3)

        if not continuous:
            break
        print("\n⏳ 完成一轮全域扫描，休息 10 分钟后启动下一波增量雷达...")
        time.sleep(600)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GitHub ~100-Star Hidden Gem Scout")
    parser.add_argument("--target", type=int, default=15, help="目标挖掘的有效宝藏数量")
    parser.add_argument("--continuous", action="store_true", help="是否作为常驻守护进程持续长任务运行")
    args = parser.parse_args()

    run_scout(target_gems=args.target, continuous=args.continuous)
