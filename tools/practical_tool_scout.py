#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Practical Tool Scout & Article Synthesizer (亲民神仙级实用工具雷达与推文生成器)
=============================================================================
专为普通玩家、电脑洁癖党、办公族打造的日常神仙小工具挖掘与发文生成工厂：
- 零配置、免安装、单文件、体积小、无广告
- 治好平时用电脑/打游戏时的各种精神内耗
- 自动生成小黑盒/知乎老哥风格的万字推文、独立专栏报告与汇总合辑
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
DB_PATH = os.path.join(PROJECT_ROOT, "data", "practical_tools.db")
REPORTS_DIR = os.path.join(PROJECT_ROOT, "reports", "practical_tools")
ARTICLES_DIR = os.path.join(REPORTS_DIR, "articles")

GATEWAY_URL = os.environ.get("GATEWAY_URL", "http://100.114.18.45:7863/v1/chat/completions")
# 网关凭证统一从项目根 .env 读取（config_lib），不再硬编码
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "services"))
from config_lib import GATEWAY_KEY as _ENV_GATEWAY_KEY
GATEWAY_KEY = os.environ.get("GATEWAY_KEY") or _ENV_GATEWAY_KEY
MODEL_NAME = os.environ.get("MODEL_NAME", "workbuddy/glm-5.3-flash")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")

# 精选超亲民神仙工具种子库（日常刚需、开箱即用、口碑爆棚）
CURATED_SEEDS = [
    {
        "repo": "emoacht/TwinkleTray",
        "category": "桌面体验救火",
        "highlight": "鼠标滚轮直接调显示器硬件亮度，告别抠屏幕屁股上的烂按键",
        "tag": "Windows必备"
    },
    {
        "repo": "QL-Win/QuickLook",
        "category": "桌面体验救火",
        "highlight": "按一下空格键秒级预览万物（图片/视频/代码/PDF/压缩包），不用开臃肿软件",
        "tag": "效率神器"
    },
    {
        "repo": "BluePointLilac/ContextMenuManager",
        "category": "系统深度清理",
        "highlight": "一键清除流氓软件塞在鼠标右键菜单里的所有牛皮癣选项",
        "tag": "洁癖党必装"
    },
    {
        "repo": "localsend/localsend",
        "category": "文件与网络传输",
        "highlight": "全平台局域网隔空投送，手机电脑互传免登录、不限速、不压画质",
        "tag": "全平台神器"
    },
    {
        "repo": "mifi/lossless-cut",
        "category": "影音处理神仙",
        "highlight": "1秒无损剪切大视频，无需重新编解码，画质零损失，速度等同于文件复制",
        "tag": "剪辑刚需"
    },
    {
        "repo": "JosefNemec/Playnite",
        "category": "游戏玩家刚需",
        "highlight": "全平台游戏一键归集大画廊，把Steam/Epic/GOG/学习版整合进PS5级海报大屏",
        "tag": "Steam玩家必备"
    },
    {
        "repo": "upscayl/upscayl",
        "category": "AI本地极客工具",
        "highlight": "本地免费 AI 图片超分放大，老壁纸/二次元低清图一键 4K/8K 锐化超清",
        "tag": "二次元壁纸党"
    },
    {
        "repo": "hiroi-sora/Umi-OCR",
        "category": "办公防抓狂",
        "highlight": "离线截图极速文字识别，专门复制网页禁止复制的文字与代码，纯本地保护隐私",
        "tag": "办公神器"
    },
    {
        "repo": "agalwood/Motrix",
        "category": "纯净下载工具",
        "highlight": "基于 Aria2 的多线程满速下载器，告别迅雷限速、开屏弹窗与流氓插件绑架",
        "tag": "下载利器"
    },
    {
        "repo": "mtkennerly/ludusavi",
        "category": "游戏玩家刚需",
        "highlight": "跨平台 PC 游戏存档全自动备份还原，Steam/Epic/各种学习版存档一键备份防翻车",
        "tag": "单机党护身符"
    },
    {
        "repo": "zhongyang219/TrafficMonitor",
        "category": "桌面体验救火",
        "highlight": "任务栏极简透明网速/CPU/内存悬浮窗，不占桌面，极客一眼看穿后台占用",
        "tag": "老牌神器"
    },
    {
        "repo": "File-New-Project/EarTrumpet",
        "category": "桌面体验救火",
        "highlight": "微软欠了二十年的音量合成器，独立拉每个软件的音量条，游戏太吵一秒压下去",
        "tag": "游戏开黑必备"
    }
]

def init_db():
    os.makedirs(ARTICLES_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS practical_tools (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            repo_name TEXT UNIQUE,
            html_url TEXT,
            stars INTEGER,
            category TEXT,
            pain_point TEXT,
            why_better TEXT,
            article_title TEXT,
            article_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def is_repo_analyzed(repo_name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM practical_tools WHERE repo_name = ?", (repo_name,))
    row = cursor.fetchone()
    conn.close()
    return row is not None

def fetch_repo_meta(repo_name):
    url = f"https://api.github.com/repos/{repo_name}"
    headers = {"User-Agent": "Hermes-Tool-Scout/1.0", "Accept": "application/vnd.github.v3+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=12) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"[-] 获取项目元数据失败 [{repo_name}]: {e}")
        return None

def fetch_readme_text(repo_name):
    branches = ["HEAD", "main", "master"]
    headers = {"User-Agent": "Hermes-Tool-Scout/1.0"}
    for b in branches:
        url = f"https://raw.githubusercontent.com/{repo_name}/{b}/README.md"
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=8) as resp:
                text = resp.read().decode("utf-8", errors="ignore")
                if len(text.strip()) > 50:
                    return text[:4500]
        except Exception:
            continue
    return ""

def write_article_with_llm(seed, repo_meta, readme_text):
    repo_name = seed["repo"]
    stars = repo_meta.get("stargazers_count", 0) if repo_meta else "数万"
    desc = repo_meta.get("description", "") if repo_meta else seed["highlight"]
    cat = seed["category"]
    highlight = seed["highlight"]

    prompt = f"""你是一位深谙玩家心声、行文极其接地气、幽默犀利、痛恨一切流氓套路的小黑盒/知乎顶流数码游戏博主。
你写文章的原则是：
1. 【拒绝假大空】：绝对禁止出现“总的来说”、“综上所述”、“值得一提的是”、“不仅如此”、“极大地提升了”等毫无信息量的 AI 烂套话！
2. 【痛点直球】：直接把平时用电脑/打游戏时被恶心到的真实场景讲出来（比如弹窗、限速、抠显示器按键、微信压图）；
3. 【讲透怎么爽】：小白解压怎么用、跟大厂恶心软件比它香在哪里；
4. 【加入专属表情】：在关键情感爆点自然带上小黑盒表情（如 [cube_吐血], [cube_点赞], [cube_挑衅], [cube_酷], [cube_干杯], [cube_思考]）。

现在请为开源神器【{repo_name}】撰写一篇深度、生动、可以直接拿去发帖的【神仙工具安利长文】（Markdown 格式）：

【项目信息】
- 仓库名称: {repo_name} (GitHub: https://github.com/{repo_name})
- 星标热度: {stars} Stars | 所属分类: {cat}
- 核心招牌亮点: {highlight}
- 官方描述: {desc}
- README 核心节选:
{readme_text[:3000] if readme_text else "(无详细 README，请基于亮点与项目核心功能展开)"}

【文章结构要求】
# 标题：起一个吸引眼球、直戳痛点但绝不低俗的标题（如：被Windows折磨了十年的痛，终于被这个几兆的小工具给治好了！）

> 一句直球导语：点明这是什么神器、适合谁、老哥一句话终审。

### 1. 痛点暴击：到底什么反人类设计把人逼疯了？
- 形象描绘日常使用电脑时的恶心场景，直击读者共鸣。

### 2. 神仙亮相：这玩意如何一秒治好精神内耗？
- 用大白话讲清楚它是怎么工作的、核心体验有多丝滑。

### 3. 降维打击：跟同类大厂/商业流氓软件比，它香在何处？
- 列一个直观的对比清单（从“体积/广告/收费/后台常驻/隐私权限”等维度降维吊打大厂全家桶）。

### 4. 保姆级上手：小白 30 秒开箱指南与隐藏神仙功能
- 怎么下载解压、核心设置开关怎么点、有什么只有老手才知道的进阶骚操作。

### 5. 老哥总结与自取
- 软件获取建议（Release 下载提示）、避坑点、呼吁评论区交流。
"""

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.35
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
        print(f"[-] 文章生成出错 [{repo_name}]: {e}")
        return None, 0, 0

def save_article_and_db(seed, repo_meta, article_md):
    repo_name = seed["repo"]
    clean_name = repo_name.replace("/", "_")
    stars = repo_meta.get("stargazers_count", 0) if repo_meta else 0
    html_url = f"https://github.com/{repo_name}"

    out_path = os.path.join(ARTICLES_DIR, f"{clean_name}.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(article_md)

    # 提取标题
    lines = [l.strip() for l in article_md.split("\n") if l.strip()]
    title = lines[0].replace("#", "").strip() if lines else repo_name

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO practical_tools (
            repo_name, html_url, stars, category, pain_point, why_better, article_title, article_path, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        repo_name, html_url, stars, seed["category"], seed["highlight"],
        "单文件无广告免安装开源", title, out_path, datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()
    conn.close()
    return out_path, title

def generate_consolidated_collection():
    """生成小黑盒大合辑汇总推文"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT repo_name, html_url, stars, category, pain_point, article_title, article_path
        FROM practical_tools
        ORDER BY id ASC
    """)
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return

    col_md = """# 电脑里别再装那些流氓全家桶了！这几个神仙级小工具让你用电脑爽上天

兄弟们好，我是老张！[cube_点赞]

平常用电脑或者打游戏，最烦的就是各种反人类的小毛病：想调个显示器亮度得去抠屏幕屁股后面的塑料烂按键；想剪个 30 秒游戏录屏非得开大软件渲染半天还压糊画质；点个右键卡两秒全是流氓软件加的垃圾选项；传个照片被微信压缩得全是马赛克...[cube_吐血]

今天老哥把我私藏已久的 **几款亲民神仙级小工具** 端出来！**全都是单文件/绿色免安装、体积只有几兆到几十兆、无广告、纯本地、开箱即用**，每一个都能把你从精神内耗里拯救出来！[cube_挑衅]

---

"""
    for idx, r in enumerate(rows, 1):
        col_md += f"## {idx}. [{r[0]}]({r[1]}) —— {r[3]}\n"
        col_md += f"- **当前热度**: `{r[2]}★` | **核心解决**: {r[4]}\n"
        col_md += f"- **专栏深度详评**: 详见文章《{r[5]}》\n\n"
        col_md += "---\n\n"

    col_md += """
### 老哥自取与总结
所有工具全部开源在 GitHub，可以直接去对应仓库的 **Releases** 页面下载最新绿色版，解压即用，不写注册表不弹广告！[cube_酷]

你们平时还有什么“不用不知道，一用根本离不开”的亲民神仙工具？评论区甩出来造福兄弟们！[cube_干杯]
"""
    col_path = os.path.join(REPORTS_DIR, "xiaoheihe_practical_tools_collection.md")
    with open(col_path, "w", encoding="utf-8") as f:
        f.write(col_md)
    print(f"[+] 大合辑推文已生成: {col_path}")

def run_scout_and_articles(limit=5):
    init_db()
    seeds = [s for s in CURATED_SEEDS if not is_repo_analyzed(s["repo"])]
    if limit:
        seeds = seeds[:limit]

    total = len(seeds)
    if total == 0:
        print("[*] 所有精选亲民神仙工具已全部撰写完毕！")
        generate_consolidated_collection()
        return

    print(f"[*] 🚀 启动亲民神仙级实用工具雷达与推文生成工厂 (计划撰写: {total} 篇独立深度推文)")
    accum_tokens = 0

    for idx, seed in enumerate(seeds, 1):
        repo_name = seed["repo"]
        print(f"\n[{idx}/{total}] 🔍 正在检索并剖析亲民工具: [{repo_name}] ({seed['category']}) ...")

        meta = fetch_repo_meta(repo_name)
        readme = fetch_readme_text(repo_name)

        print(f"    ✍️ 正在通过 {MODEL_NAME} 撰写直球老哥风格深度安利长文 ...")
        article_md, tokens, elapsed = write_article_with_llm(seed, meta, readme)

        if article_md:
            accum_tokens += tokens
            out_path, title = save_article_and_db(seed, meta, article_md)
            print(f"    [+] 深度长文已保存: {out_path} (耗时: {elapsed:.1f}s | 消耗 Token: {tokens})")
            print(f"        文章标题: 《{title}》")
        else:
            print(f"    [-] 生成失败，跳过。")
        time.sleep(2)

    generate_consolidated_collection()
    print(f"\n🎉 亲民工具文章批次完成！累计消耗 Token: {accum_tokens}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Practical Tool Scout & Article Synthesizer")
    parser.add_argument("--limit", type=int, default=6, help="本次撰写文章数量")
    args = parser.parse_args()
    run_scout_and_articles(limit=args.limit)
