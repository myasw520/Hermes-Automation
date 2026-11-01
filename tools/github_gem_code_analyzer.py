#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub ~100-Star Gem Codebase Deep Diver (百星神仙仓库源码级逆向解构与架构剖析)
=============================================================================
深入 50~300 星 S 级宝藏项目代码层：
- 抓取全项目代码树与核心源文件 (.rs, .py, .c, .cpp, .cs, .go)
- 零依赖架构还原、逆向协议解析解密、Win32/底层系统调用骚操作剖析
- 核心代码逐行带批注精读 + 二次开发魔改避坑指南
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
DB_PATH = os.path.join(PROJECT_ROOT, "data", "github_gems.db")
DEEP_DIVE_DIR = os.path.join(PROJECT_ROOT, "reports", "github_gems", "deep_dive")

GATEWAY_URL = os.environ.get("GATEWAY_URL", "http://100.114.18.45:7863/v1/chat/completions")
# 网关凭证统一从项目根 .env 读取（config_lib），不再硬编码
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "services"))
from config_lib import GATEWAY_KEY as _ENV_GATEWAY_KEY
GATEWAY_KEY = os.environ.get("GATEWAY_KEY") or _ENV_GATEWAY_KEY
MODEL_NAME = os.environ.get("MODEL_NAME", "workbuddy/glm-5.3-flash")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")

# 源代码重要扩展名
SRC_EXTENSIONS = [".rs", ".py", ".c", ".cpp", ".cc", ".h", ".hpp", ".cs", ".go", ".swift", ".ts", ".js"]
IGNORE_DIRS = ["test", "tests", "docs", "node_modules", "vendor", "build", "dist", ".git", ".github", "venv"]

def init_tables():
    os.makedirs(DEEP_DIVE_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE github_gems ADD COLUMN deep_dive_path TEXT")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE github_gems ADD COLUMN deep_dive_at TEXT")
    except Exception:
        pass
    conn.commit()
    conn.close()

def fetch_file_tree(full_name):
    """获取项目代码树"""
    url = f"https://api.github.com/repos/{full_name}/git/trees/HEAD?recursive=1"
    headers = {"User-Agent": "Hermes-Code-Diver/1.0", "Accept": "application/vnd.github.v3+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("tree", [])
    except Exception as e:
        print(f"[-] 获取代码树失败 [{full_name}]: {e}")
        return []

def select_key_source_files(tree):
    """挑选前 3~5 个最核心的源码文件"""
    candidates = []
    for item in tree:
        if item.get("type") != "blob":
            continue
        path = item.get("path", "")
        # 忽略测试与依赖目录
        if any(ign in path.lower().split("/") for ign in IGNORE_DIRS):
            continue
        ext = os.path.splitext(path)[1].lower()
        if ext in SRC_EXTENSIONS:
            size = item.get("size", 0)
            if 100 < size < 100000:  # 排除空文件与超大生成代码
                candidates.append((path, size))

    # 按路径特征排序（优先 main, core, parser, lib 等核心词）
    def score_path(p_size):
        p, s = p_size
        score = 0
        p_low = p.lower()
        for kw in ["main", "app", "core", "parser", "flasher", "protocol", "inject", "engine", "client"]:
            if kw in p_low:
                score += 50
        if "/" not in p or p.startswith("src/"):
            score += 20
        return score - (s / 5000)

    candidates.sort(key=score_path, reverse=True)
    return [p for p, s in candidates[:4]]

def fetch_raw_file(full_name, file_path):
    """通过 raw.githubusercontent.com 直抓源代码，不受 API 速率限制"""
    branches = ["HEAD", "main", "master"]
    headers = {"User-Agent": "Hermes-Code-Diver/1.0"}
    for b in branches:
        url = f"https://raw.githubusercontent.com/{full_name}/{b}/{file_path}"
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                return resp.read().decode("utf-8", errors="ignore")
        except Exception:
            continue
    return ""

def analyze_codebase_with_llm(repo, file_tree, code_snippets):
    full_name = repo["full_name"]
    stars = repo["stars"]
    lang = repo["language"]
    pain_point = repo["pain_point"]
    why_gem = repo["why_gem"]

    prompt = f"""你是一位极其挑剔、精通底层系统编程、逆向工程与架构设计的顶级资深架构师。
现在请对 GitHub 上这个百星神仙项目进行【代码级深度逆向解构与架构剖析】：

【项目背景】
- 仓库名称: {full_name} ({stars}★ | 主力语言: {lang})
- 解决核心痛点: {pain_point}
- 降维优势: {why_gem}

【项目代码结构 (前 40 个文件)】
{chr(10).join([item.get('path', '') for item in file_tree[:40]])}

【核心源代码节选 (真实代码片段)】
"""
    for path, code in code_snippets.items():
        snippet = code[:3500] if len(code) > 3500 else code
        prompt += f"\n--- [文件: {path}] ---\n```\n{snippet}\n```\n"

    prompt += f"""
【深度剖析要求】
请撰写一份极其详尽、极客味十足的【万字硬核源码剖析报告】（Markdown 格式），包含：
1. **全局架构与数据流拓扑 (Mermaid 流程图)**：清晰刻画其模块划分与状态转移。
2. **底层骚操作解密 (核心技术突破点)**：深入剖析它是如何绕过官方限制、逆向闭源协议、调用底层 OS API 或运用精妙算法的（指出具体函数与技术选型）。
3. **关键源码逐行透视与精读**：挑选代码中最惊艳、最硬核的 2~3 个函数片段，进行逐行代码级剖析，讲透其防御性设计与极致性能考量。
4. **性能与轻量化秘密**：分析它为什么能做到体积极小、零依赖、内存占用低（相比几万星臃肿软件的具体代码差异）。
5. **极客二次开发与魔改避坑指南**：如果想给它增加功能或移植到其他环境，有哪些隐藏的坑点、环境依赖与技术边界。
"""

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }
    data_bytes = json.dumps(payload).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GATEWAY_KEY}"
    }

    try:
        t0 = time.time()
        req = urllib.request.Request(GATEWAY_URL, data=data_bytes, headers=headers)
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            elapsed = time.time() - t0
            content = result["choices"][0]["message"]["content"].strip()
            tokens = result.get("usage", {}).get("total_tokens", 0)
            return content, tokens, elapsed
    except Exception as e:
        print(f"[-] LLM 源码剖析出错 [{full_name}]: {e}")
        return None, 0, 0

def run_deep_diver(target_count=5):
    init_tables()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, full_name, stars, language, pain_point, why_gem, gem_score
        FROM github_gems
        WHERE is_gem = 1 AND gem_score >= 8 AND (deep_dive_path IS NULL OR deep_dive_path = '')
        ORDER BY gem_score DESC, stars ASC
        LIMIT ?
    """, (target_count,))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("[*] 没有待深度剖析的高星宝藏仓库。")
        return

    print(f"[*] 🚀 启动百星宝藏代码级深度剖析引擎 (计划深度解构: {len(rows)} 个项目)")
    accum_tokens = 0

    for idx, r in enumerate(rows, 1):
        repo_info = {
            "id": r[0],
            "full_name": r[1],
            "stars": r[2],
            "language": r[3],
            "pain_point": r[4],
            "why_gem": r[5],
            "gem_score": r[6]
        }
        full_name = repo_info["full_name"]
        print(f"\n[{idx}/{len(rows)}] 🔍 正在深度挖掘源码: [{full_name}] ({repo_info['stars']}★ | {repo_info['language']}) ...")

        # 抓取文件树
        tree = fetch_file_tree(full_name)
        key_files = select_key_source_files(tree)
        print(f"    挑选核心源文件: {key_files}")

        # 抓取源码内容
        code_snippets = {}
        for kf in key_files:
            code = fetch_raw_file(full_name, kf)
            if code:
                code_snippets[kf] = code

        if not code_snippets:
            print("    [!] 未能拉取到有效源码片段，跳过。")
            continue

        print(f"    🧠 正在驱动 {MODEL_NAME} 进行架构逆向与源码精讲 ...")
        report_md, tokens, elapsed = analyze_codebase_with_llm(repo_info, tree, code_snippets)

        if report_md:
            accum_tokens += tokens
            clean_name = full_name.replace("/", "_")
            out_path = os.path.join(DEEP_DIVE_DIR, f"{clean_name}_deep_dive.md")
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(f"# 🛠️ 深度源码剖析: {full_name} ({repo_info['stars']}★)\n")
                f.write(f"> 评分: ⭐ {repo_info['gem_score']}/10 | 语言: `{repo_info['language']}` | 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
                f.write(report_md)

            # 更新数据库状态
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("""
                UPDATE github_gems
                SET deep_dive_path = ?, deep_dive_at = ?
                WHERE id = ?
            """, (out_path, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), repo_info["id"]))
            conn.commit()
            conn.close()

            print(f"    [+] 源码剖析报告已生成: {out_path} (耗时: {elapsed:.1f}s | 消耗 Token: {tokens})")
        time.sleep(2)

    print(f"\n🎉 百星神仙代码解构批次完成！累计消耗 Token: {accum_tokens}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GitHub Gem Codebase Deep Diver")
    parser.add_argument("--count", type=int, default=5, help="剖析项目数量")
    args = parser.parse_args()
    run_deep_diver(target_count=args.count)
