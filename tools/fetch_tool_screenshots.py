# -*- coding: utf-8 -*-
import os
import sys
import re
import json
import urllib.request
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

REPOS = {
    "JosefNemec_Playnite": "JosefNemec/Playnite",
    "mtkennerly_ludusavi": "mtkennerly/ludusavi",
    "mifi_lossless-cut": "mifi/lossless-cut",
    "emoacht_TwinkleTray": "emoacht/TwinkleTray",
    "zhongyang219_TrafficMonitor": "zhongyang219/TrafficMonitor",
}

IMG_DIR = Path("reports/practical_tools/images")

def download_file(url, out_path):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read()
            if len(content) > 1000:
                out_path.write_bytes(content)
                print(f"  [OK] Saved {len(content)} bytes -> {out_path.name}")
                return True
    except Exception as e:
        print(f"  [FAIL] {url}: {e}")
    return False

def main():
    for folder, repo in REPOS.items():
        target_dir = IMG_DIR / folder
        target_dir.mkdir(parents=True, exist_ok=True)
        print(f"\nFetching images for {repo} into {target_dir}...")
        
        # 1. Fetch README
        api_url = f"https://api.github.com/repos/{repo}/readme"
        req = urllib.request.Request(api_url, headers={"User-Agent": "Mozilla/5.0"})
        raw_text = ""
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())
                dl_url = data.get("download_url")
                with urllib.request.urlopen(dl_url, timeout=10) as cresp:
                    raw_text = cresp.read().decode("utf-8", errors="ignore")
        except Exception as e:
            print(f"  README API error: {e}")
            continue

        # Extract markdown and html images
        img_urls = []
        for m in re.finditer(r'!\[.*?\]\((https?://[^\)]+\.(?:png|jpg|jpeg|gif|webp))\)', raw_text, re.I):
            img_urls.append(m.group(1))
        for m in re.finditer(r'<img[^>]+src=["\'](https?://[^"\']+\.(?:png|jpg|jpeg|gif|webp))["\']', raw_text, re.I):
            img_urls.append(m.group(1))

        # Also find relative paths like images/foo.png or docs/bar.gif
        for m in re.finditer(r'!\[.*?\]\(((?!https?:)[^\)]+\.(?:png|jpg|jpeg|gif|webp))\)', raw_text, re.I):
            rel = m.group(1).lstrip("./")
            img_urls.append(f"https://raw.githubusercontent.com/{repo}/master/{rel}")
            img_urls.append(f"https://raw.githubusercontent.com/{repo}/main/{rel}")
        for m in re.finditer(r'<img[^>]+src=["\']((?!https?:)[^"\']+\.(?:png|jpg|jpeg|gif|webp))["\']', raw_text, re.I):
            rel = m.group(1).lstrip("./")
            img_urls.append(f"https://raw.githubusercontent.com/{repo}/master/{rel}")
            img_urls.append(f"https://raw.githubusercontent.com/{repo}/main/{rel}")

        # Deduplicate
        seen = set()
        unique_urls = []
        for u in img_urls:
            # Skip shields / badges
            if "shields.io" in u or "badge" in u or "github/license" in u or "action" in u:
                continue
            if u not in seen:
                seen.add(u)
                unique_urls.append(u)

        print(f"  Found {len(unique_urls)} valid image candidates.")
        idx = 3  # Start from 3 so we don't overwrite 1 and 2
        for u in unique_urls:
            ext = u.split("?")[0].split(".")[-1].lower()
            if ext not in ["png", "jpg", "jpeg", "gif", "webp"]:
                ext = "png"
            dest = target_dir / f"screenshot_{idx}.{ext}"
            if download_file(u, dest):
                idx += 1
            if idx > 8:
                break

if __name__ == "__main__":
    main()
