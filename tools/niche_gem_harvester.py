# -*- coding: utf-8 -*-
"""
Niche Open-Source Gem Harvester & Asset Vault (小众低星宝藏开源项目与实机图采集工厂)
=============================================================================
专为小黑盒技术老哥打造的“反套路/反刷星”低星神级开源工具挖掘机：
1. 专注两大题材：
   - Track A（系统极客）：Windows 原生/单文件/免安装/无全家桶的底层效率神器（50~2000 Star）
   - Track B（本地离线 AI）：轻量级纯本地小模型、无网极客终端黑科技、离线玩具（50~2000 Star）
2. 挖掘高 Star 痛点并提炼“拉踩对比点”（抨击刷星、全家桶、商业化臃肿）
3. 自动抓取并下载 README 中的实机高清截图与演示动图（过滤徽章与图标，真实留存）
4. 输出完整的可直接用于小黑盒写稿的题材库与素材包
"""

import os
import re
import sys
import json
import time
import sqlite3
import argparse
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime

# Windows 终端编码保护
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import functools
import cv2
import numpy as np
from PIL import Image
import io
print = functools.partial(print, flush=True)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
REPORTS_DIR = PROJECT_ROOT / "reports" / "niche_gems"
ASSETS_DIR = REPORTS_DIR / "assets"
DB_PATH = DATA_DIR / "niche_gems.db"

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")

# 垃圾/课件/大杂烩过滤词
JUNK_KEYWORDS = [
    "awesome", "course", "homework", "curriculum", "interview", "leetcode", 
    "resume", "roadmap", "cheatsheet", "collection", "book", "tutorial", 
    "learn-", "study", "notes", "assignment", "guide", "syllabus", "exam",
    "paper", "list", "resources"
]

TRACK_CONFIGS = {
    "track_a_windows": {
        "title": "Windows 原生/单文件硬核治流氓与效率神器",
        "queries": [
            "topic:windows+topic:tool+stars:50..2000+fork:false",
            "topic:windows+topic:productivity+stars:50..1800+fork:false",
            "topic:windows+language:rust+stars:60..2000+fork:false",
            "topic:context-menu+stars:50..1500+fork:false",
            "topic:windows+topic:system+stars:60..2000+fork:false",
            "topic:system-tray+stars:50..1500+fork:false"
        ]
    },
    "track_b_local_ai": {
        "title": "轻量级纯本地离线 AI 与极客终端玩具",
        "queries": [
            "topic:local-ai+stars:50..2000+fork:false",
            "topic:offline-ai+stars:50..2000+fork:false",
            "topic:tui+topic:ai+stars:40..1500+fork:false",
            "topic:cli+topic:llm+language:rust+stars:50..2000+fork:false",
            "topic:onnx+topic:tool+stars:50..1800+fork:false",
            "topic:whisper+topic:desktop+stars:50..2000+fork:false"
        ]
    }
}

def init_db():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS niche_repos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            track TEXT,
            full_name TEXT UNIQUE,
            name TEXT,
            owner TEXT,
            html_url TEXT,
            description TEXT,
            stars INTEGER,
            forks INTEGER,
            language TEXT,
            pushed_at TEXT,
            default_branch TEXT,
            downloaded_images TEXT,
            image_count INTEGER DEFAULT 0,
            roast_angle TEXT,
            status TEXT DEFAULT 'raw',
            created_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

def github_api_get(url: str) -> dict | list | None:
    headers = {
        "User-Agent": "NicheGemScout/2.0",
        "Accept": "application/vnd.github.v3+json"
    }
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"

    req = urllib.request.Request(url, headers=headers)
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 403:
                reset_time = int(e.headers.get("X-RateLimit-Reset", time.time() + 60))
                wait_sec = max(reset_time - int(time.time()), 10)
                print(f"  [API Rate Limit] 触发 GitHub 限频，等待 {wait_sec} 秒...")
                time.sleep(min(wait_sec, 60))
            elif e.code == 404:
                return None
            else:
                print(f"  [API Error {e.code}] URL: {url}")
                time.sleep(2)
        except Exception as ex:
            time.sleep(2)
    return None

def fetch_raw_readme(owner: str, repo: str, default_branch: str = "main") -> str:
    branches = [default_branch, "main", "master"]
    readme_names = ["README.md", "readme.md", "README.rst", "README"]

    for b in set(branches):
        for rname in readme_names:
            url = f"https://raw.githubusercontent.com/{owner}/{repo}/{b}/{rname}"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            try:
                with urllib.request.urlopen(req, timeout=10) as resp:
                    return resp.read().decode("utf-8", errors="ignore")
            except Exception:
                continue
    return ""

def is_badge_url(url: str) -> bool:
    badge_domains = [
        "shields.io", "badge.fury.io", "travis-ci.org", "travis-ci.com",
        "github.com/workflows", "codecov.io", "badge", "license",
        "goreportcard.com", "crates.io/badges", "pepy.tech", "img.shields.io",
        "github/stars", "sonarcloud.io"
    ]
    low = url.lower()
    return any(bd in low for bd in badge_domains) or low.endswith(".svg")

def extract_image_urls(readme_text: str, owner: str, repo: str, branch: str = "main") -> list[str]:
    urls = []
    # 1. Markdown 语法: ![alt](url)
    md_matches = re.findall(r'!\[.*?\]\((.*?)\)', readme_text)
    for m in md_matches:
        # 去掉可能的标题或空格: (url "title")
        raw_url = m.split()[0].strip().strip('"').strip("'")
        if raw_url and not is_badge_url(raw_url):
            urls.append(raw_url)

    # 2. HTML 语法: <img src="url">
    html_matches = re.findall(r'<img[^>]+src=["\'](.*?)["\']', readme_text, re.IGNORECASE)
    for h in html_matches:
        h = h.strip()
        if h and not is_badge_url(h):
            urls.append(h)

    # 3. 规范化为绝对 URL
    resolved_urls = []
    for u in urls:
        if u.startswith("http://") or u.startswith("https://"):
            # 如果是 github.com/.../blob/... 换成 raw.githubusercontent.com/...
            if "github.com/" in u and "/blob/" in u:
                u = u.replace("github.com/", "raw.githubusercontent.com/").replace("/blob/", "/")
            resolved_urls.append(u)
        elif not u.startswith("#") and not u.startswith("mailto:"):
            # 相对路径转 raw 地址
            clean_path = u.lstrip("./")
            abs_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{clean_path}"
            resolved_urls.append(abs_url)

    # 去重
    unique_urls = []
    seen = set()
    for u in resolved_urls:
        if u not in seen:
            seen.add(u)
            unique_urls.append(u)
    return unique_urls

def download_images(image_urls: list[str], repo_slug: str, max_images: int = 5) -> list[str]:
    repo_asset_dir = ASSETS_DIR / repo_slug.replace("/", "_")
    repo_asset_dir.mkdir(parents=True, exist_ok=True)

    saved_files = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    qr_detector = cv2.QRCodeDetector()

    for idx, url in enumerate(image_urls):
        if len(saved_files) >= max_images:
            break

        ext = Path(url.split("?")[0]).suffix.lower()
        if ext not in [".png", ".jpg", ".jpeg", ".webp", ".gif"]:
            ext = ".png"

        target_name = f"img_{idx+1:02d}{ext}"
        target_path = repo_asset_dir / target_name

        if target_path.exists() and target_path.stat().st_size > 5000:
            # 同样对已有文件进行快速校验
            saved_files.append(str(target_path.relative_to(PROJECT_ROOT)))
            continue

        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=12) as resp:
                data = resp.read()
                
                # 1. 体积过滤：小于 8KB 或大于 8MB (防止小黑盒 10MB 报错)
                if len(data) < 8000 or len(data) > 8 * 1024 * 1024:
                    continue

                # 2. 图像解析与尺寸过滤 (排除图标/头像/横条徽章)
                try:
                    with Image.open(io.BytesIO(data)) as im:
                        w, h = im.size
                        # 排除小图
                        if w < 380 or h < 240:
                            continue
                        # 排除正方形图标/Logo/头像 (128x128, 256x256, 512x512)
                        if abs(w - h) < 15 and w <= 512:
                            continue
                        # 排除极细横条 Badge/Banner
                        if w / h > 4.5 or h / w > 3.0:
                            continue
                except Exception:
                    continue

                # 3. 二维码检测 (彻底拦截微信群/QQ群/赞赏码)
                try:
                    nparr = np.frombuffer(data, np.uint8)
                    cv_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    if cv_img is not None:
                        qr_data, _, _ = qr_detector.detectAndDecode(cv_img)
                        if qr_data:
                            print(f"      [X 拦截二维码] 跳过包含群/收款码的图片: {url[:60]}")
                            continue
                except Exception:
                    pass

                target_path.write_bytes(data)

                # 4. 多模态 AI 视觉质检 (一票否决假截图、二维码、广告，并生成真题注)
                from vision_auditor import audit_image
                audit_res = audit_image(target_path)
                if not audit_res.get("is_approved"):
                    reason = audit_res.get("rejection_reason", "不符合真机UI标准")
                    print(f"      [X AI 视觉淘汰] {reason}")
                    try:
                        target_path.unlink()
                    except Exception:
                        pass
                    continue

                feature = audit_res.get("actual_feature_detected", "实操界面")
                caption = audit_res.get("suggested_caption", f"图：{feature}")
                saved_files.append(str(target_path.relative_to(PROJECT_ROOT)))
                print(f"      [✓ AI 视觉通过] {feature} --> {caption} ({w}x{h}, {len(data)//1024} KB)")
        except Exception:
            continue

    return saved_files

def generate_roast_angle(track: str, repo_info: dict) -> str:
    name = repo_info["name"]
    desc = repo_info["description"] or ""
    stars = repo_info["stars"]
    
    if track == "track_a_windows":
        return f"抨击高 Star 全家桶（动辄几个 G、开机自启、弹窗广告），拉踩那些刷出来的所谓主流优化工具；主打 {name} 仅 {stars} Star，纯单文件绿色无后台，把细分痛点干到极致。"
    else:
        return f"抨击商业云端大模型 API 割韭菜与依赖网络的臃肿应用；主打 {name}（{stars} Star）纯本地免断网运行，几十 MB 极客玩具，零隐私泄露、完全白嫖。"

def scan_track(track_id: str, limit_per_query: int = 15):
    cfg = TRACK_CONFIGS[track_id]
    print(f"\n========================================================")
    print(f"  正在挖掘题材: 【{cfg['title']}】")
    print(f"========================================================")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    for q in cfg["queries"]:
        url = f"https://api.github.com/search/repositories?q={q}&sort=updated&order=desc&per_page={limit_per_query}"
        print(f"\n[Search] {q}")
        res = github_api_get(url)
        if not res or "items" not in res:
            continue

        items = res["items"]
        print(f"  -> 候选仓库数: {len(items)}")

        for it in items:
            full_name = it["full_name"]
            stars = it["stargazers_count"]
            desc = (it["description"] or "").strip()
            owner = it["owner"]["login"]
            name = it["name"]
            default_branch = it.get("default_branch", "main")
            pushed_at = it.get("pushed_at", "")

            # 垃圾过滤
            if any(k in full_name.lower() or k in desc.lower() for k in JUNK_KEYWORDS):
                continue

            # 检查是否已入库
            cur.execute("SELECT id, image_count FROM niche_repos WHERE full_name = ?", (full_name,))
            row = cur.fetchone()
            if row and row[1] > 0:
                print(f"  [跳过] 已存在且有图: {full_name} ({stars}★)")
                continue

            print(f"  -> 正在深度解析: {full_name} ({stars}★)")
            # 抓取 README
            readme = fetch_raw_readme(owner, name, default_branch)
            img_urls = extract_image_urls(readme, owner, name, default_branch) if readme else []

            # 优先筛选有演示图或截图的仓库（求精不求多）
            saved_images = []
            if img_urls:
                print(f"    找到 {len(img_urls)} 个潜在实机图，正在下载高清大图...")
                saved_images = download_images(img_urls, full_name, max_images=4)

            roast = generate_roast_angle(track_id, {
                "name": name,
                "description": desc,
                "stars": stars
            })

            cur.execute('''
                INSERT OR REPLACE INTO niche_repos (
                    track, full_name, name, owner, html_url, description,
                    stars, forks, language, pushed_at, default_branch,
                    downloaded_images, image_count, roast_angle, status, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                track_id, full_name, name, owner, it["html_url"], desc,
                stars, it["forks_count"], it.get("language", ""),
                pushed_at, default_branch, json.dumps(saved_images),
                len(saved_images), roast, "ready" if saved_images else "no_image",
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
            conn.commit()

            if saved_images:
                print(f"    [★ 精品入库] {full_name} 成功保存 {len(saved_images)} 张实机图！")
            else:
                print(f"    [无实机图入库] {full_name} (文字备选)")

            time.sleep(1)

    conn.close()

def export_dossier():
    """导出精选卡片与小黑盒选题大盘"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute('''
        SELECT track, full_name, name, html_url, stars, language, description, roast_angle, downloaded_images, image_count
        FROM niche_repos
        WHERE image_count > 0
        ORDER BY stars ASC
    ''')
    rows = cur.fetchall()
    conn.close()

    lines = [
        "# 小黑盒小众低星宝藏仓库军火库（求精·含实机图）",
        f"> 更新时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 已沉淀带实机截图的精选项目：{len(rows)} 个",
        "",
        "---",
        ""
    ]

    by_track = {}
    for r in rows:
        track = r[0]
        by_track.setdefault(track, []).append(r)

    for track, items in by_track.items():
        title = TRACK_CONFIGS.get(track, {}).get("title", track)
        lines.append(f"## 题材专区：{title}（{len(items)} 个精选仓库）\n")
        
        for idx, it in enumerate(items, 1):
            _, full_name, name, url, stars, lang, desc, roast, imgs_json, img_cnt = it
            imgs = json.loads(imgs_json) if imgs_json else []
            
            lines.append(f"### {idx:02d}. [{name}]({url}) — ★ {stars} 星 ({lang or '其它'})")
            lines.append(f"- **仓库定位**：`{full_name}`")
            lines.append(f"- **一句话痛点**：{desc or '极简无描述'}")
            lines.append(f"- **拉踩/抨击爆款切入点**：{roast}")
            lines.append(f"- **已下载实机图（共 {img_cnt} 张）**：")
            for im in imgs:
                lines.append(f"  - `file:///{PROJECT_ROOT.as_posix()}/{im}`")
            lines.append("")

    out_md = REPORTS_DIR / "niche_gems_dossier.md"
    out_md.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n[✓] 军火库大盘已生成: {out_md}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--track", choices=["track_a_windows", "track_b_local_ai", "all"], default="all")
    parser.add_argument("--export-only", action="store_true")
    args = parser.parse_args()

    init_db()

    if args.export_only:
        export_dossier()
        return

    if args.track in ["track_a_windows", "all"]:
        scan_track("track_a_windows", limit_per_query=10)

    if args.track in ["track_b_local_ai", "all"]:
        scan_track("track_b_local_ai", limit_per_query=10)

    export_dossier()

if __name__ == "__main__":
    main()
