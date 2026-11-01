# -*- coding: utf-8 -*-
"""
Hermes 采图任务派发器 (dispatch_to_hermes.py)
==============================================
职责边界（用户拍板）：
- 本脚本【只做管理】：从赛道稿提取仓库清单 -> 生成任务包 -> 派发给 Hermes
- 采图本身由 Hermes（Docker :8642 agent）执行，本脚本不抓图
- 图回来后用 vision_auditor 质检（--audit 模式）

工作流：
  1) python tools/dispatch_to_hermes.py --scan
     扫 reports/xiaoheihe_articles/track_*.md，提取每篇的 仓库/星数 清单，
     生成 reports/hermes_output/image_tasks/track_xxx_task.json
  2) 把任务包内容发给 Hermes（8642 chat/completions，它自己会跑 CDP/脚本采图），
     或人工把任务包丢给 Hermes 会话
  3) Hermes 把图存到 reports/hermes_output/image_tasks/<track>/<repo>/
  4) python tools/dispatch_to_hermes.py --audit
     对每篇稿件的图目录跑 vision_auditor 质检，输出配对结果

用法：
    python tools/dispatch_to_hermes.py --scan            # 生成任务包
    python tools/dispatch_to_hermes.py --send            # 通过 8642 网关把任务发给 Hermes
    python tools/dispatch_to_hermes.py --status          # 查看各赛道采图进度
    python tools/dispatch_to_hermes.py --audit           # 质检已回图的赛道
"""

import sys
import os
import re
import json
import time
import glob
import argparse
import urllib.request

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "services"))
from config_lib import HERMES_API_URL, HERMES_API_KEY  # noqa: F401

ARTICLE_GLOB = os.path.join(BASE_DIR, "reports", "xiaoheihe_articles", "track_*_20261031.md")
TASK_DIR = os.path.join(BASE_DIR, "reports", "hermes_output", "image_tasks")

# 采图要求（发给 Hermes 的正文模板）
TASK_TEMPLATE = """【任务：为小黑盒帖子采集仓库实机截图】
赛道：{track}
稿子：{article_path}

对下面每个仓库，采集 2~4 张"实机运行截图或 README 演示图"（优先 UI 截图，拒绝 badge/logo/二维码/社交卡片），
存到：{out_dir}/<owner>_<repo>/img_01.png ...
图保存为 png/jpg，单张 >10KB（过滤占位图）。

仓库清单（星数为 2026-10-31 数据）：
{repo_list}

完成后回一份清单：每个仓库几张图、路径。质量存疑的标出来。"""


def extract_repos_from_article(path):
    """从赛道稿提取 (owner/repo, stars) 清单——兼容数字星数、中文"万星"、标题式引用三种写法"""
    text = open(path, encoding="utf-8").read()
    pairs = []
    seen = set()

    def _add(repo, stars, allow_bare=False):
        repo = repo.strip("*：:（）() ，,。 ")
        if repo.count("/") == 1 and repo not in seen and 100 <= stars <= 500000:
            if not re.match(r'^\d+\.', repo) and not any(c in repo for c in "，。！？"):
                pairs.append({"repo": repo, "stars": stars})
                seen.add(repo)
        elif allow_bare and "/" not in repo and repo not in seen and 100 <= stars <= 500000:
            # 标题式裸名：先占位，后面经 namemap 解析为全名
            pairs.append({"repo": repo, "stars": stars, "bare": True})
            seen.add(repo)

    # 模式1: repo（42824 星） / repo 42824星 / repo｜26531星
    for m in re.finditer(r'([A-Za-z0-9_\-\.]+/[A-Za-z0-9_\-\.]+)[^\n]{0,20}?(\d{3,7})\s*星', text):
        _add(m.group(1), int(m.group(2)))
    # 模式2: repo，33 万星 / repo，11 万星（中文"万"单位）
    for m in re.finditer(r'([A-Za-z0-9_\-\.]+/[A-Za-z0-9_\-\.]+)[，,]\s*(\d+(?:\.\d+)?)\s*万\s*星', text):
        _add(m.group(1), int(float(m.group(2)) * 10000))
    # 模式3: 标题式引用 ## PCSX2（15958 星，C++）——裸项目名无 owner/
    for m in re.finditer(r'##\s*([A-Za-z0-9_\-]+)[^\n]{0,10}?(\d{3,7})\s*星', text):
        _add(m.group(1), int(m.group(2)), allow_bare=True)
    # 裸名（无 owner/）经 GitHub search 解析为全名，缓存于 <track>_namemap.json
    if any("/" not in p["repo"] for p in pairs):
        namemap = _load_namemap(path)
        for entry in pairs:
            if "/" not in entry["repo"] and entry["repo"] in namemap:
                entry["repo"] = namemap[entry["repo"]]["full_name"]
                entry.pop("bare", None)
        pairs = [p for p in pairs if not p.get("bare")]  # 解析失败的裸名剔除
    return pairs


def _load_namemap(article_path):
    """把标题式裸名解析为 GitHub 全名并缓存（每个裸名一次 search API）"""
    import urllib.request, urllib.parse, time
    base = os.path.splitext(article_path)[0]
    os.makedirs(TASK_DIR, exist_ok=True)
    cache = os.path.join(TASK_DIR, os.path.basename(base) + "_namemap.json")
    if os.path.exists(cache):
        return json.load(open(cache, encoding="utf-8"))
    token = None
    for line in open(os.path.join(BASE_DIR, ".env"), encoding="utf-8"):
        if line.startswith("GITHUB_TOKEN="):
            token = line.split("=", 1)[1].strip()
    text = open(article_path, encoding="utf-8").read()
    bare = {m.group(1) for m in re.finditer(r'##\s*([A-Za-z0-9_\-]+)[^\n]{0,10}?(\d{3,7})\s*星', text)
            if "/" not in m.group(1)}
    namemap = {}
    for name in sorted(bare):
        try:
            req = urllib.request.Request(
                f"https://api.github.com/search/repositories?q={urllib.parse.quote(name)}&sort=stars&per_page=1",
                headers={"Authorization": f"token {token}", "User-Agent": "hermes"})
            d = json.loads(urllib.request.urlopen(req, timeout=15).read())
            if d["items"]:
                namemap[name] = {"full_name": d["items"][0]["full_name"],
                                 "stars_now": d["items"][0]["stargazers_count"]}
                print(f"    [namemap] {name} -> {namemap[name]['full_name']}")
            time.sleep(1)
        except Exception as e:
            print(f"    [namemap] {name} 解析失败: {e}")
    json.dump(namemap, open(cache, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return namemap


def cmd_scan():
    os.makedirs(TASK_DIR, exist_ok=True)
    for art in sorted(glob.glob(ARTICLE_GLOB)):
        track = os.path.basename(art).split("track_")[1].split("_20261031")[0]
        repos = extract_repos_from_article(art)
        if not repos:
            print(f"[!] {track}: 未提取到仓库，跳过")
            continue
        task = {
            "track": track,
            "article": art,
            "out_dir": os.path.join(TASK_DIR, track),
            "repos": repos,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "status": "pending",
        }
        out = os.path.join(TASK_DIR, f"{track}_task.json")
        json.dump(task, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"[+] {track}: {len(repos)} 个仓库 -> {out}")
        for r in repos:
            print(f"      {r['repo']}  {r['stars']}★")


def _hermes_chat(prompt, timeout=60):
    url = HERMES_API_URL
    payload = json.dumps({
        "model": "hermes-agent",
        "messages": [{"role": "user", "content": prompt}],
    }).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {HERMES_API_KEY}",
    })
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def cmd_send():
    files = sorted(glob.glob(os.path.join(TASK_DIR, "*_task.json")))
    if not files:
        print("[!] 没有 pending 的任务包，先跑 --scan")
        return
    for f in files:
        task = json.load(open(f, encoding="utf-8"))
        if task.get("status") not in ("pending", "retry"):
            print(f"[skip] {task['track']}: status={task['status']}")
            continue
        repo_list = "\n".join(f"- {r['repo']}（{r['stars']} 星）" for r in task["repos"])
        prompt = TASK_TEMPLATE.format(
            track=task["track"], article_path=task["article"],
            out_dir=task["out_dir"], repo_list=repo_list)
        # Hermes 是同步 agent：HTTP 响应 = 干完。整赛道 10min+，同步等必超时。
        # 策略：超时放宽到 30min（干完能拿到它的完工报告）；HTTP 层断开不影响它继续干活，
        # 状态一律标 dispatched，进度用 --status / --pull 查询。
        print(f"[*] 派发 {task['track']}（{len(task['repos'])} 仓库）给 Hermes（最长等 30min，可 Ctrl+C，活不会停）...")
        try:
            resp = _hermes_chat(prompt, timeout=1800)
            content = resp.get("choices", [{}])[0].get("message", {}).get("content", "")
            print(f"[+] Hermes 完工报告（前 300 字）: {content[:300]}")
        except Exception as e:
            print(f"[!] HTTP 等待结束（{e.__class__.__name__}），Hermes 可能仍在后台干活")
        task["status"] = "dispatched"
        task["dispatched_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
        json.dump(task, open(f, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        time.sleep(2)


def cmd_status():
    files = sorted(glob.glob(os.path.join(TASK_DIR, "*_task.json")))
    if not files:
        print("[!] 尚无任务包")
        return
    for f in files:
        task = json.load(open(f, encoding="utf-8"))
        track = task["track"]
        out_dir = task["out_dir"]
        have = 0
        want = len(task["repos"])
        if os.path.isdir(out_dir):
            for repo in task["repos"]:
                name = repo["repo"] if isinstance(repo, dict) else repo
                d = os.path.join(out_dir, name.replace("/", "_"))
                if os.path.isdir(d) and any(os.scandir(d)):
                    have += 1
        print(f"{track:15} | {task.get('status','?'):10} | 回图 {have}/{want} 仓库")


def cmd_audit():
    sys.path.insert(0, os.path.join(BASE_DIR, "tools"))
    from vision_auditor import audit_image  # noqa
    files = sorted(glob.glob(os.path.join(TASK_DIR, "*_task.json")))
    for f in files:
        task = json.load(open(f, encoding="utf-8"))
        track = task["track"]
        out_dir = task["out_dir"]
        if not os.path.isdir(out_dir):
            print(f"[skip] {track}: 还没回图")
            continue
        print(f"\n=== 质检 {track} ===")
        for entry in os.scandir(out_dir):
            if not entry.is_dir():
                continue
            keep, drop = 0, 0
            for img in glob.glob(os.path.join(entry.path, "*.png")) + glob.glob(os.path.join(entry.path, "*.jpg")):
                try:
                    res = audit_image(img)
                    if res.get("is_approved"):
                        keep += 1
                    else:
                        drop += 1
                        os.remove(img)
                        print(f"  [X 淘汰] {entry.name}/{os.path.basename(img)}: {res.get('rejection_reason','')[:50]}")
                except Exception as e:
                    print(f"  [!] {img}: {e}")
            print(f"  {entry.name}: 保留 {keep} / 淘汰 {drop}")


HERMES_CONTAINER = "hermes"
HERMES_DATA_IN_CONTAINER = "/opt/data"  # 容器内工作根（镜像挂载卷 /opt/data）


def cmd_pull():
    """把 Hermes 采好的图从容器卷 docker cp 回宿主任务目录"""
    import subprocess
    files = sorted(glob.glob(os.path.join(TASK_DIR, "*_task.json")))
    if not files:
        print("[!] 没有任务包")
        return
    total = 0
    for f in files:
        task = json.load(open(f, encoding="utf-8"))
        track = task["track"]
        # 容器内对应路径：宿主 reports/hermes_output/image_tasks/<track> 与
        # 容器 /opt/data/reports/hermes_output/image_tasks/<track> 一一对应
        rel = f"reports/hermes_output/image_tasks/{track}"
        src = f"{HERMES_CONTAINER}:{HERMES_DATA_IN_CONTAINER}/{rel}"
        dst = os.path.join(TASK_DIR, track)
        r = subprocess.run(["docker", "cp", src, dst], capture_output=True, text=True)
        if r.returncode == 0:
            n = sum(len(glob.glob(os.path.join(dst, d, "*.p*"))) for d in os.listdir(dst) if os.path.isdir(os.path.join(dst, d)))
            print(f"[+] {track}: 已拉回 {n} 张")
            total += n
        else:
            print(f"[skip] {track}: 容器内暂无 ({r.stderr.strip()[:60]})")
    print(f"共拉回 {total} 张")


def main():
    ap = argparse.ArgumentParser(description="Hermes 采图任务派发与质检管理")
    ap.add_argument("--scan", action="store_true", help="从赛道稿提取仓库清单，生成任务包")
    ap.add_argument("--send", action="store_true", help="把任务包派发给 Hermes（8642）")
    ap.add_argument("--pull", action="store_true", help="docker cp 把容器内采好的图拉回宿主")
    ap.add_argument("--status", action="store_true", help="查看各赛道回图进度")
    ap.add_argument("--audit", action="store_true", help="vision_auditor 质检回图")
    args = ap.parse_args()
    if args.scan: cmd_scan()
    elif args.send: cmd_send()
    elif args.pull: cmd_pull()
    elif args.status: cmd_status()
    elif args.audit: cmd_audit()
    else: ap.print_help()


if __name__ == "__main__":
    main()
