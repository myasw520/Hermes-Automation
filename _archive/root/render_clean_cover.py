# -*- coding: utf-8 -*-
"""Render clean, high-impact Xiaoheihe 16:9 cover on top of the newly generated clean illustration.
No inpainting, no leftover text, 100% clean vectors and crisp typography.
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

# Input image
gen_path = r"C:\Users\zzx05\.gemini\antigravity\brain\1df70796-e1a9-4d4b-b590-e026bcc2348f\whale_maid_article_cover_1793295948630.jpg"
artifact_dir = Path(r"C:\Users\zzx05\.gemini\antigravity\brain\1df70796-e1a9-4d4b-b590-e026bcc2348f")
stockpile_dir = Path(r"C:\Users\zzx05\Hermes-Automation\reports\hermes_output\stockpile_drafts")

font_bold = r"C:\Windows\Fonts\msyhbd.ttc"
font_regular = r"C:\Windows\Fonts\msyh.ttc"

# Load base illustration
img = Image.open(gen_path).convert("RGB")
W, H = img.size # 1376 x 768
draw = ImageDraw.Draw(img)

# ---------------------------------------------------------
# 1. Typography inside the speech bubble (x: 530..875, y: 55..335)
# Bubble center x is ~ 700, center y is ~ 190
# ---------------------------------------------------------
bubble_cx = 702
bubble_lines = [
    ("天天给我喂白饭...", 26),
    ("难不成你其实很喜欢我？", 26),
    ("放心吧，昨天聊了什么", 26),
    ("我可全记在日记里啦！", 28)
]

start_y = 105
line_spacing = 42

for i, (text, sz) in enumerate(bubble_lines):
    f = ImageFont.truetype(font_bold, sz)
    bbox = draw.textbbox((0, 0), text, font=f)
    tw = bbox[2] - bbox[0]
    tx = bubble_cx - tw // 2
    ty = start_y + i * line_spacing
    # Crisp comic dark text
    draw.text((tx, ty), text, font=f, fill=(25, 25, 30))

# ---------------------------------------------------------
# 2. Left Side Headline & Cards (x: 50..500)
# ---------------------------------------------------------
# Category Pill
pill_x, pill_y = 50, 75
pill_w, pill_h = 390, 48
draw.rounded_rectangle([pill_x, pill_y, pill_x + pill_w, pill_y + pill_h], radius=24, fill=(15, 60, 160))
f_pill = ImageFont.truetype(font_bold, 22)
draw.text((pill_x + 22, pill_y + 11), "🐳 DeepSeek 进阶 · 伴侣与记忆特辑", font=f_pill, fill=(255, 255, 255))

# Main Title Line 1
f_title = ImageFont.truetype(font_bold, 66)
# Drop shadow for readability
draw.text((54, 154), "怎么让大肥鱼", font=f_title, fill=(200, 215, 240))
draw.text((50, 150), "怎么让大肥鱼", font=f_title, fill=(20, 25, 45))

# Main Title Line 2 (Highlighted coral badge)
line2_text = "记住吃白饭的人？"
draw.rounded_rectangle([45, 245, 45 + 535, 245 + 86], radius=16, fill=(255, 85, 75))
draw.text((55, 250), line2_text, font=f_title, fill=(255, 255, 255))

# Subtitle Card
card_x, card_y = 50, 365
card_w, card_h = 475, 82
draw.rounded_rectangle([card_x, card_y, card_x + card_w, card_y + card_h], radius=16, fill=(255, 255, 255), outline=(200, 220, 245), width=2)
f_sub = ImageFont.truetype(font_bold, 24)
draw.text((card_x + 18, card_y + 15), "⚡ 6 款开源记忆与拟人插件实测", font=f_sub, fill=(25, 35, 60))
f_sub2 = ImageFont.truetype(font_regular, 19)
draw.text((card_x + 18, card_y + 48), "灵魂日记 · 可回滚记忆树 · 主动搭话猫娘", font=f_sub2, fill=(100, 115, 140))

# Tool Feature Chips
chips = ["★ Soul of Waifu", "★ nocturne_memory", "★ N.E.K.O"]
cx = 50
cy = 480
f_chip = ImageFont.truetype(font_bold, 18)
for chip in chips:
    bbox = draw.textbbox((0, 0), chip, font=f_chip)
    cw = bbox[2] - bbox[0] + 28
    draw.rounded_rectangle([cx, cy, cx + cw, cy + 38], radius=12, fill=(230, 240, 255), outline=(180, 210, 250), width=1)
    draw.text((cx + 14, cy + 8), chip, font=f_chip, fill=(20, 70, 170))
    cx += cw + 14

# Bottom quote
f_quote = ImageFont.truetype(font_bold, 20)
draw.text((52, 550), "“一重启全忘光？给她一个完整一生”", font=f_quote, fill=(80, 95, 120))

# Bottom edge accent
draw.rectangle([0, H - 10, W, H], fill=(15, 60, 160))

# Save outputs
out_art = artifact_dir / "cover_clean_whale_16_9.png"
out_stk = stockpile_dir / "cover_clean_whale_16_9.png"

img.save(out_art)
img.save(out_stk)
print(f"Cover successfully saved to {out_art} and {out_stk}")
