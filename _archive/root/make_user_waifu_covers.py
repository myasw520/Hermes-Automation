# -*- coding: utf-8 -*-
"""Generate cover variants based on the user-uploaded cute whale maid meme image.
Option 1: 16:9 Banner (Left title typography + Right whale maid with custom speech bubble)
Option 2: 16:9 Comic Frame (Centered full square image + themed sidebars + title badge)
Option 3: Square Meme (850x850 with customized speech bubble)
Option 4: 16:9 Banner with ORIGINAL speech bubble text (in case user prefers original text)
"""

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path

# Paths
orig_path = r"C:\Users\zzx05\.gemini\antigravity\brain\1df70796-e1a9-4d4b-b590-e026bcc2348f\.user_uploaded\media_1793293323396_c4d0e7d0.jpg"
artifact_dir = Path(r"C:\Users\zzx05\.gemini\antigravity\brain\1df70796-e1a9-4d4b-b590-e026bcc2348f")
stockpile_dir = Path(r"C:\Users\zzx05\Hermes-Automation\reports\hermes_output\stockpile_drafts")

font_bold = r"C:\Windows\Fonts\msyhbd.ttc"
font_regular = r"C:\Windows\Fonts\msyh.ttc"
font_simhei = r"C:\Windows\Fonts\simhei.ttf"

# 1. Clean the speech bubble
orig_cv = cv2.imread(orig_path)
gray = cv2.cvtColor(orig_cv, cv2.COLOR_BGR2GRAY)
mask = np.zeros(gray.shape, dtype=np.uint8)
# Text is inside [10:360, 250:845]
mask[10:360, 250:845] = (gray[10:360, 250:845] < 160).astype(np.uint8) * 255
orig_cv_cleaned = orig_cv.copy()
orig_cv_cleaned[mask > 0] = [255, 254, 253]

clean_pil = Image.fromarray(cv2.cvtColor(orig_cv_cleaned, cv2.COLOR_BGR2RGB))
orig_pil = Image.open(orig_path).convert("RGB")

# 2. Function to draw customized speech bubble
def add_custom_bubble_text(base_img, lines, font_sizes, y_coords):
    img = base_img.copy()
    draw = ImageDraw.Draw(img)
    for line, sz, y in zip(lines, font_sizes, y_coords):
        f = ImageFont.truetype(font_bold, sz)
        bbox = draw.textbbox((0, 0), line, font=f)
        tw = bbox[2] - bbox[0]
        # Center horizontally in bubble (between x=240 and x=825)
        x = 240 + (585 - tw) // 2
        # Text shadow for comic feel (subtle)
        draw.text((x, y), line, font=f, fill=(20, 20, 25))
    return img

# Variant text for the theme
bubble_lines = [
    "天天给我喂算力白饭...",
    "难不成你其实很喜欢我？",
    "哼，昨天聊了什么",
    "我可全都记得哦！"
]
bubble_sizes = [44, 46, 46, 52]
bubble_ys = [36, 110, 185, 260]

modified_square = add_custom_bubble_text(clean_pil, bubble_lines, bubble_sizes, bubble_ys)
# Save Option 3: Square Meme
opt3_path = artifact_dir / "cover_waifu_square_modified.png"
modified_square.save(opt3_path)
modified_square.save(stockpile_dir / "cover_waifu_square_modified.png")

# -------------------------------------------------------------
# Option 1: 16:9 Viral Banner (1280 x 720)
# Left: Big Title + Badges + Tech-Cute Geek Card
# Right: The Cute Whale Maid (Height 720, scaled)
# -------------------------------------------------------------
W, H = 1280, 720
banner1 = Image.new("RGB", (W, H), (245, 248, 255))
b1_draw = ImageDraw.Draw(banner1)

# Subtle background gradient: pastel blue to crisp white
for y in range(H):
    # interpolate from (235, 243, 255) to (255, 255, 255)
    r = int(236 + (255 - 236) * (y / H))
    g = int(244 + (255 - 244) * (y / H))
    b = int(255 + (255 - 255) * (y / H))
    b1_draw.line([(0, y), (W, y)], fill=(r, g, b))

# Add some cute comic polka dots / accent lines on the left background
dot_color = (215, 230, 250)
for dx in range(30, 600, 45):
    for dy in range(30, H, 45):
        b1_draw.ellipse([dx, dy, dx+4, dy+4], fill=dot_color)

# Scale the modified whale maid to fit right side (Height 720)
# Original is 850x850 -> scale to 720x720
scale_factor = 720 / 850
whale_resized = modified_square.resize((720, 720), Image.Resampling.LANCZOS)

# Paste on the right: x = 1280 - 720 = 560
banner1.paste(whale_resized, (560, 0))

# Left Content Layout:
# 1. Top Category Pill Tag
pill_x, pill_y = 60, 65
pill_w, pill_h = 390, 48
b1_draw.rounded_rectangle([pill_x, pill_y, pill_x + pill_w, pill_y + pill_h], radius=24, fill=(15, 60, 160))
f_pill = ImageFont.truetype(font_bold, 22)
b1_draw.text((pill_x + 22, pill_y + 11), "🐳 DeepSeek 进阶 · 伴侣与记忆特辑", font=f_pill, fill=(255, 255, 255))

# 2. Main Title Line 1
f_title = ImageFont.truetype(font_bold, 66)
b1_draw.text((62, 142), "怎么让大肥鱼", font=f_title, fill=(20, 25, 45))

# 3. Main Title Line 2 (Highlighted with high contrast badge/accent)
line2_text = "记住吃白饭的人？"
b1_draw.rounded_rectangle([55, 235, 55 + 530, 235 + 86], radius=16, fill=(255, 95, 80))
b1_draw.text((65, 240), line2_text, font=f_title, fill=(255, 255, 255))

# 4. Subtitle Card
card_x, card_y = 60, 355
card_w, card_h = 490, 80
b1_draw.rounded_rectangle([card_x, card_y, card_x + card_w, card_y + card_h], radius=16, fill=(255, 255, 255), outline=(210, 225, 245), width=2)
f_sub = ImageFont.truetype(font_bold, 25)
b1_draw.text((card_x + 20, card_y + 16), "⚡ 6 款开源记忆与去 AI 味插件", font=f_sub, fill=(25, 35, 60))
f_sub2 = ImageFont.truetype(font_regular, 20)
b1_draw.text((card_x + 20, card_y + 48), "灵魂日记 · 可回滚记忆树 · 主动搭话猫娘", font=f_sub2, fill=(100, 115, 140))

# 5. Three Tool Feature Chips
chips = ["★ Soul of Waifu", "★ nocturne_memory", "★ N.E.K.O"]
cx = 60
cy = 465
f_chip = ImageFont.truetype(font_bold, 18)
for chip in chips:
    bbox = b1_draw.textbbox((0, 0), chip, font=f_chip)
    cw = bbox[2] - bbox[0] + 28
    b1_draw.rounded_rectangle([cx, cy, cx + cw, cy + 38], radius=12, fill=(230, 240, 255), outline=(180, 210, 250), width=1)
    b1_draw.text((cx + 14, cy + 8), chip, font=f_chip, fill=(20, 70, 170))
    cx += cw + 14

# 6. Bottom Geek Quote
f_quote = ImageFont.truetype(font_bold, 20)
b1_draw.text((62, 535), "“一重启全忘光？给她一个完整一生”", font=f_quote, fill=(90, 105, 130))

# 7. Decorative bottom line
b1_draw.rectangle([0, H - 10, W, H], fill=(15, 60, 160))

opt1_path = artifact_dir / "cover_waifu_16_9_v1.png"
banner1.save(opt1_path)
banner1.save(stockpile_dir / "cover_waifu_16_9_v1.png")

# -------------------------------------------------------------
# Option 2: 16:9 Comic Frame (Centered Whale Maid, Full Width 16:9)
# -------------------------------------------------------------
banner2 = Image.new("RGB", (W, H), (255, 255, 255))
b2_draw = ImageDraw.Draw(banner2)

# Paste modified square centered (x = (1280 - 720)//2 = 280)
banner2.paste(whale_resized, (280, 0))

# Left and Right Decorative Comic Panels
# Left Panel
b2_draw.rectangle([0, 0, 280, H], fill=(240, 246, 255))
b2_draw.line([(280, 0), (280, H)], fill=(20, 20, 25), width=4)

# Right Panel
b2_draw.rectangle([1000, 0, W, H], fill=(240, 246, 255))
b2_draw.line([(1000, 0), (1000, H)], fill=(20, 20, 25), width=4)

# Left Panel Vertical/Stacked Typography
f_v_title = ImageFont.truetype(font_bold, 44)
b2_draw.text((40, 60), "怎么让", font=f_v_title, fill=(20, 25, 45))
b2_draw.text((40, 125), "大肥鱼", font=f_v_title, fill=(15, 60, 160))
b2_draw.text((40, 190), "记住你", font=f_v_title, fill=(255, 95, 80))

f_v_desc = ImageFont.truetype(font_bold, 22)
b2_draw.text((40, 280), "6款开源插件", font=f_v_desc, fill=(30, 40, 60))
b2_draw.text((40, 315), "长效记忆特辑", font=f_v_desc, fill=(30, 40, 60))

# Right Panel Highlights
b2_draw.rounded_rectangle([1020, 60, 1260, 220], radius=16, fill=(255, 255, 255), outline=(20, 20, 25), width=3)
f_box_t = ImageFont.truetype(font_bold, 22)
b2_draw.text((1035, 78), "⚡ 核心亮点", font=f_box_t, fill=(255, 95, 80))
f_box_c = ImageFont.truetype(font_regular, 18)
b2_draw.text((1035, 115), "• 第一视角日记", font=f_box_c, fill=(40, 50, 70))
b2_draw.text((1035, 145), "• 记忆树可视化", font=f_box_c, fill=(40, 50, 70))
b2_draw.text((1035, 175), "• 主动搭话猫娘", font=f_box_c, fill=(40, 50, 70))

opt2_path = artifact_dir / "cover_waifu_16_9_v2.png"
banner2.save(opt2_path)
banner2.save(stockpile_dir / "cover_waifu_16_9_v2.png")

# -------------------------------------------------------------
# Option 4: 16:9 Banner with ORIGINAL speech bubble text
# -------------------------------------------------------------
banner4 = Image.new("RGB", (W, H), (245, 248, 255))
b4_draw = ImageDraw.Draw(banner4)
for y in range(H):
    r = int(236 + (255 - 236) * (y / H))
    g = int(244 + (255 - 244) * (y / H))
    b = int(255 + (255 - 255) * (y / H))
    b4_draw.line([(0, y), (W, y)], fill=(r, g, b))

for dx in range(30, 600, 45):
    for dy in range(30, H, 45):
        b4_draw.ellipse([dx, dy, dx+4, dy+4], fill=dot_color)

whale_orig_resized = orig_pil.resize((720, 720), Image.Resampling.LANCZOS)
banner4.paste(whale_orig_resized, (560, 0))

# Left typography
b4_draw.rounded_rectangle([pill_x, pill_y, pill_x + pill_w, pill_y + pill_h], radius=24, fill=(15, 60, 160))
b4_draw.text((pill_x + 22, pill_y + 11), "🐳 DeepSeek 进阶 · 伴侣与记忆特辑", font=f_pill, fill=(255, 255, 255))
b4_draw.text((62, 142), "怎么让大肥鱼", font=f_title, fill=(20, 25, 45))
b4_draw.rounded_rectangle([55, 235, 55 + 530, 235 + 86], radius=16, fill=(255, 95, 80))
b4_draw.text((65, 240), line2_text, font=f_title, fill=(255, 255, 255))

b4_draw.rounded_rectangle([card_x, card_y, card_x + card_w, card_y + card_h], radius=16, fill=(255, 255, 255), outline=(210, 225, 245), width=2)
b4_draw.text((card_x + 20, card_y + 16), "⚡ 6 款开源记忆与去 AI 味插件", font=f_sub, fill=(25, 35, 60))
b4_draw.text((card_x + 20, card_y + 48), "灵魂日记 · 可回滚记忆树 · 主动搭话猫娘", font=f_sub2, fill=(100, 115, 140))

cx = 60
for chip in chips:
    bbox = b4_draw.textbbox((0, 0), chip, font=f_chip)
    cw = bbox[2] - bbox[0] + 28
    b4_draw.rounded_rectangle([cx, cy, cx + cw, cy + 38], radius=12, fill=(230, 240, 255), outline=(180, 210, 250), width=1)
    b4_draw.text((cx + 14, cy + 8), chip, font=f_chip, fill=(20, 70, 170))
    cx += cw + 14

b4_draw.text((62, 535), "“一重启全忘光？给她一个完整一生”", font=f_quote, fill=(90, 105, 130))
b4_draw.rectangle([0, H - 10, W, H], fill=(15, 60, 160))

opt4_path = artifact_dir / "cover_waifu_16_9_v4_orig_bubble.png"
banner4.save(opt4_path)
banner4.save(stockpile_dir / "cover_waifu_16_9_v4_orig_bubble.png")

print("All cover variants successfully generated!")
