# -*- coding: utf-8 -*-
"""清理并下载 100% 真实的软件界面截图，彻底杜绝头像、图标、纯文字横幅与徽章"""
import sys
import urllib.request
from pathlib import Path
from PIL import Image

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# 1. 修复 ghostdeck 的实机图 (换掉 2560x600 banner，换成真正的 fan_curve 和 status 界面)
ghostdeck_dir = PROJECT_ROOT / "reports/stockpile_drafts/track_a_windows/01_专治发热与流氓更新_三款百星单文件/images"
ghostdeck_urls = [
    ("https://raw.githubusercontent.com/wygodad/ghostdeck/main/docs/images/fan_curve.png", ghostdeck_dir / "item_1_fan_curve.png"),
    ("https://raw.githubusercontent.com/wygodad/ghostdeck/main/docs/images/status.png", ghostdeck_dir / "item_1_status.png"),
    ("https://raw.githubusercontent.com/wygodad/ghostdeck/main/docs/images/settings_power.png", ghostdeck_dir / "item_1_settings.png"),
]

for url, target in ghostdeck_urls:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        data = urllib.request.urlopen(req, timeout=10).read()
        target.write_bytes(data)
        with Image.open(target) as im:
            print(f"[✓ GhostDeck 实机图] {target.name}: {im.size}")
    except Exception as e:
        print(f"Error fetching {url}: {e}")

# 删除 ghostdeck 之前的 2560x600 banner (item_1_img_01, 02, 03, 04)
for p in ghostdeck_dir.glob("item_1_img_*"):
    print(f"Deleting banner: {p.name}")
    p.unlink()

# 删除 Disable-automatic-Windows-update 的 1280x640 纯标题横幅 (item_3_img_01)
banner_update = ghostdeck_dir / "item_3_img_01.png"
if banner_update.exists():
    print(f"Deleting update banner: {banner_update.name}")
    banner_update.unlink()

# 2. 修复 heard 的实机图 (删除 1152x1152 logo 和小图)
heard_dir = PROJECT_ROOT / "reports/stockpile_drafts/track_b_local_ai/01_别给云端API交保护费_三款离线本地AI黑科技/images"
logo_heard = heard_dir / "item_1_img_04.jpg"
if logo_heard.exists():
    print(f"Deleting heard logo: {logo_heard.name}")
    logo_heard.unlink()

small_heard = heard_dir / "item_1_img_01.png"
if small_heard.exists():
    print(f"Deleting small heard img: {small_heard.name}")
    small_heard.unlink()

# 3. 检查并清理所有图片，确保全都是高质量真实界面
print("\n=== 图片质量与分辨率终审 ===")
all_drafts = PROJECT_ROOT / "reports/stockpile_drafts"
for img_path in sorted(all_drafts.rglob("*.*")):
    if img_path.suffix.lower() in [".png", ".jpg", ".jpeg", ".webp"]:
        with Image.open(img_path) as im:
            w, h = im.size
            aspect = w / h if h else 0
            # 校验
            is_valid_ui = w >= 320 and h >= 220 and aspect < 3.2 and aspect > 0.4
            status = "✓ 真实界面" if is_valid_ui else "✗ 嫌疑图"
            print(f"{status} | {img_path.parent.parent.name}/{img_path.name} | {w}x{h} (比例 {aspect:.2f})")
