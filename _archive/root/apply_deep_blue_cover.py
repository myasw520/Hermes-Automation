# -*- coding: utf-8 -*-
"""Color-correct hair to exact anime deep navy blue (matching reference image),
render crisp typography and speech bubble, and save final cover.
"""
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

# Paths
base_img_path = r"C:\Users\zzx05\.gemini\antigravity\brain\1df70796-e1a9-4d4b-b590-e026bcc2348f\whale_maid_article_cover_1793295948630.jpg"
artifact_dir = Path(r"C:\Users\zzx05\.gemini\antigravity\brain\1df70796-e1a9-4d4b-b590-e026bcc2348f")
stockpile_dir = Path(r"C:\Users\zzx05\Hermes-Automation\reports\hermes_output\stockpile_drafts")

font_bold = r"C:\Windows\Fonts\msyhbd.ttc"
font_regular = r"C:\Windows\Fonts\msyh.ttc"

# 1. Color correct hair
img_bgr = cv2.imread(base_img_path)
hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV).astype(np.float32)

char_mask = np.zeros(img_bgr.shape[:2], dtype=bool)
char_mask[:, 800:] = True

h_chan = hsv[:, :, 0]
s_chan = hsv[:, :, 1]
v_chan = hsv[:, :, 2]

# Target teal/cyan/greenish hair (Hue 70 to 108)
hair_mask = char_mask & (h_chan >= 68) & (h_chan <= 108) & (s_chan > 30) & (v_chan > 30)

# Shift to deep royal navy blue (median ~ 116)
hsv[:, :, 0][hair_mask] = np.clip(hsv[:, :, 0][hair_mask] + 16, 0, 179)
hsv[:, :, 1][hair_mask] = np.clip(hsv[:, :, 1][hair_mask] * 1.18, 0, 255)
hsv[:, :, 2][hair_mask] = np.clip(hsv[:, :, 2][hair_mask] * 0.88, 0, 255)

hsv = hsv.astype(np.uint8)
corrected_bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
corrected_rgb = cv2.cvtColor(corrected_bgr, cv2.COLOR_BGR2RGB)

# 2. Render typography with Pillow
img_pil = Image.fromarray(corrected_rgb)
W, H = img_pil.size
draw = ImageDraw.Draw(img_pil)

# Speech bubble text (centered at x=702, y=105)
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
    draw.text((tx, ty), text, font=f, fill=(25, 25, 30))

# Left Side Headline & Badges
# Top Category Pill
pill_x, pill_y = 50, 75
pill_w, pill_h = 390, 48
draw.rounded_rectangle([pill_x, pill_y, pill_x + pill_w, pill_y + pill_h], radius=24, fill=(15, 60, 160))
f_pill = ImageFont.truetype(font_bold, 22)
draw.text((pill_x + 22, pill_y + 11), "🐳 DeepSeek 进阶 · 伴侣与记忆特辑", font=f_pill, fill=(255, 255, 255))

# Main Title Line 1
f_title = ImageFont.truetype(font_bold, 66)
draw.text((54, 154), "怎么让大肥鱼", font=f_title, fill=(200, 215, 240))
draw.text((50, 150), "怎么让大肥鱼", font=f_title, fill=(20, 25, 45))

# Main Title Line 2
draw.rounded_rectangle([45, 245, 45 + 535, 245 + 86], radius=16, fill=(255, 85, 75))
draw.text((55, 250), "记住吃白饭的人？", font=f_title, fill=(255, 255, 255))

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

out_art = artifact_dir / "cover_deep_blue_whale_16_9.png"
out_stk = stockpile_dir / "cover_deep_blue_whale_16_9.png"

img_pil.save(out_art)
img_pil.save(out_stk)
print(f"Deep blue cover successfully saved to:\n  {out_art}\n  {out_stk}")
