# -*- coding: utf-8 -*-
"""Generate both Version A (with clean speech bubble) and Version B (pure pristine artwork, no bubble)
using the user's authentic reference image.
"""
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

# Paths
ref_path = r"C:\Users\zzx05\.gemini\antigravity\brain\1df70796-e1a9-4d4b-b590-e026bcc2348f\.user_uploaded\media_1793298433401_09c24c49.jpg"
artifact_dir = Path(r"C:\Users\zzx05\.gemini\antigravity\brain\1df70796-e1a9-4d4b-b590-e026bcc2348f")
stockpile_dir = Path(r"C:\Users\zzx05\Hermes-Automation\reports\hermes_output\stockpile_drafts")

font_bold = r"C:\Windows\Fonts\msyhbd.ttc"
font_regular = r"C:\Windows\Fonts\msyh.ttc"

# Load and clean original reference image
ref_cv = cv2.imread(ref_path)
ref_cv[:6, :] = [255, 255, 255]
ref_cv[:14, :340] = [255, 255, 255]
ref_cv[:14, 600:] = [255, 255, 255]

ref_rgb = cv2.cvtColor(ref_cv, cv2.COLOR_BGR2RGB)
char_pil = Image.fromarray(ref_rgb)

W, H = 1280, 720
target_h = 680
target_w = int(1024 * (target_h / 861)) # ~ 808
char_scaled = char_pil.resize((target_w, target_h), Image.Resampling.LANCZOS)
char_x = W - target_w + 35
char_y = H - target_h + 15

def render_base_canvas():
    canvas = Image.new("RGB", (W, H), (255, 255, 255))
    draw = ImageDraw.Draw(canvas)
    for y in range(H):
        r = int(238 + (255 - 238) * (y / H))
        g = int(245 + (255 - 245) * (y / H))
        b = int(255 + (255 - 255) * (y / H))
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    for dx in range(35, 540, 45):
        for dy in range(35, H, 45):
            draw.ellipse([dx, dy, dx+4, dy+4], fill=(215, 230, 250))

    canvas.paste(char_scaled, (char_x, char_y))

    # Left Side Typography
    pill_x, pill_y = 50, 65
    pill_w, pill_h = 390, 48
    draw.rounded_rectangle([pill_x, pill_y, pill_x + pill_w, pill_y + pill_h], radius=24, fill=(15, 60, 160))
    f_pill = ImageFont.truetype(font_bold, 22)
    draw.text((pill_x + 22, pill_y + 11), "🐳 DeepSeek 进阶 · 伴侣与记忆特辑", font=f_pill, fill=(255, 255, 255))

    f_title = ImageFont.truetype(font_bold, 64)
    draw.text((54, 144), "怎么让大肥鱼", font=f_title, fill=(200, 215, 240))
    draw.text((50, 140), "怎么让大肥鱼", font=f_title, fill=(20, 25, 45))

    draw.rounded_rectangle([45, 235, 45 + 520, 235 + 84], radius=16, fill=(255, 85, 75))
    draw.text((55, 240), "记住吃白饭的人？", font=f_title, fill=(255, 255, 255))

    card_x, card_y = 50, 355
    card_w, card_h = 460, 82
    draw.rounded_rectangle([card_x, card_y, card_x + card_w, card_y + card_h], radius=16, fill=(255, 255, 255), outline=(200, 220, 245), width=2)
    f_sub = ImageFont.truetype(font_bold, 24)
    draw.text((card_x + 18, card_y + 15), "⚡ 6 款开源记忆与拟人插件实测", font=f_sub, fill=(25, 35, 60))
    f_sub2 = ImageFont.truetype(font_regular, 19)
    draw.text((card_x + 18, card_y + 48), "灵魂日记 · 可回滚记忆树 · 主动搭话猫娘", font=f_sub2, fill=(100, 115, 140))

    chips = ["★ Soul of Waifu", "★ nocturne_memory", "★ N.E.K.O"]
    cx = 50
    cy = 470
    f_chip = ImageFont.truetype(font_bold, 18)
    for chip in chips:
        bbox = draw.textbbox((0, 0), chip, font=f_chip)
        cw = bbox[2] - bbox[0] + 28
        draw.rounded_rectangle([cx, cy, cx + cw, cy + 38], radius=12, fill=(230, 240, 255), outline=(180, 210, 250), width=1)
        draw.text((cx + 14, cy + 8), chip, font=f_chip, fill=(20, 70, 170))
        cx += cw + 14

    f_quote = ImageFont.truetype(font_bold, 20)
    draw.text((52, 540), "“一重启全忘光？给她一个完整一生”", font=f_quote, fill=(80, 95, 120))
    draw.rectangle([0, H - 10, W, H], fill=(15, 60, 160))

    return canvas, draw

# --- Version A: With Speech Bubble ---
canvas_a, draw_a = render_base_canvas()
bx0, by0, bx1, by1 = 515, 45, 875, 215
draw_a.rounded_rectangle([bx0, by0, bx1, by1], radius=24, fill=(255, 255, 255), outline=(30, 35, 55), width=3)
tail_pts = [(740, 214), (770, 214), (795, 265)]
draw_a.polygon(tail_pts, fill=(255, 255, 255))
draw_a.line([(740, 214), (795, 265)], fill=(30, 35, 55), width=3)
draw_a.line([(770, 214), (795, 265)], fill=(30, 35, 55), width=3)
draw_a.line([(742, 214), (768, 214)], fill=(255, 255, 255), width=5)

bubble_lines = [
    ("天天给我喂白饭...", 24),
    ("难不成你其实很喜欢我？", 24),
    ("放心吧，昨天聊了什么", 24),
    ("我可全都记得哦！", 26)
]
bcx = (bx0 + bx1) // 2
bsy = by0 + 22
for i, (text, sz) in enumerate(bubble_lines):
    f = ImageFont.truetype(font_bold, sz)
    bbox = draw_a.textbbox((0, 0), text, font=f)
    tw = bbox[2] - bbox[0]
    draw_a.text((bcx - tw // 2, bsy + i * 36), text, font=f, fill=(25, 30, 45))

path_a_art = artifact_dir / "cover_perfect_whale_with_bubble.png"
path_a_stk = stockpile_dir / "cover_perfect_whale_with_bubble.png"
canvas_a.save(path_a_art)
canvas_a.save(path_a_stk)

# --- Version B: Pure Pristine Art (No Bubble) ---
canvas_b, draw_b = render_base_canvas()
path_b_art = artifact_dir / "cover_perfect_whale_clean_art.png"
path_b_stk = stockpile_dir / "cover_perfect_whale_clean_art.png"
canvas_b.save(path_b_art)
canvas_b.save(path_b_stk)

print("Both Version A (with bubble) and Version B (clean art) successfully generated!")
