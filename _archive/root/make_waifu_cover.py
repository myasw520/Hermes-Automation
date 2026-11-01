# -*- coding: utf-8 -*-
"""
Generate custom 16:9 cover for "让大肥鱼记住吃白饭的人"
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path

W, H = 1600, 900

# Try raw_3 or raw_5
src_path = Path("reports/hermes_output/stockpile_drafts/dsh_pet/raw_3.png")
if not src_path.exists():
    src_path = Path("reports/hermes_output/stockpile_drafts/dsh_pet/raw_5.png")

raw_img = Image.open(src_path).convert("RGBA")

# Crop to 16:9
target_ratio = W / H
src_ratio = raw_img.width / raw_img.height

if src_ratio > target_ratio:
    new_w = int(raw_img.height * target_ratio)
    left = (raw_img.width - new_w) // 2
    cropped = raw_img.crop((left, 0, left + new_w, raw_img.height))
else:
    new_h = int(raw_img.width / target_ratio)
    top = (raw_img.height - new_h) // 2
    cropped = raw_img.crop((0, top, raw_img.width, top + new_h))

bg = cropped.resize((W, H), Image.Resampling.LANCZOS)

# Gradient overlay
overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
odraw = ImageDraw.Draw(overlay)

# Dark navy gradient from left (solid) to right (transparent)
for x in range(W):
    if x < 480:
        alpha = 235
    elif x < 1080:
        factor = (x - 480) / 600
        alpha = int(235 * (1 - factor))
    else:
        alpha = 0
    odraw.line([(x, 0), (x, H)], fill=(11, 19, 43, alpha))

# Vignette top and bottom
for y in range(120):
    alpha = int(120 * (1 - y/120))
    odraw.line([(0, y), (W, y)], fill=(11, 19, 43, alpha))
for y in range(H - 100, H):
    alpha = int(140 * ((y - (H - 100)) / 100))
    odraw.line([(0, y), (W, y)], fill=(11, 19, 43, alpha))

canvas = Image.alpha_composite(bg, overlay)
draw = ImageDraw.Draw(canvas)

# Fonts
font_bold = "C:/Windows/Fonts/msyhbd.ttc"
font_reg = "C:/Windows/Fonts/msyh.ttc"

badge_font = ImageFont.truetype(font_bold, 24)
title_font = ImageFont.truetype(font_bold, 58)
sub_font = ImageFont.truetype(font_bold, 30)
tag_font = ImageFont.truetype(font_bold, 20)
footer_font = ImageFont.truetype(font_reg, 22)

# Helper: pill
def draw_pill(x, y, text, bg_col, text_col, font, pad_x=22, pad_y=10):
    bb = draw.textbbox((0, 0), text, font=font)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    pw, ph = tw + pad_x * 2, th + pad_y * 2
    draw.rounded_rectangle([x, y, x + pw, y + ph], radius=ph // 2, fill=bg_col)
    draw.text((x + pad_x, y + pad_y - 2), text, fill=text_col, font=font)
    return pw, ph

# Typography Layout
tx = 90
ty = 110

# Category Tag
draw_pill(tx, ty, "🐳  DeepSeek 进阶 · 伴侣与记忆特辑", (30, 58, 138, 220), (147, 197, 253), badge_font)

# Main Title: 2 lines
line1 = "怎么让大肥鱼"
line2 = "记住吃白饭的人？"

# Soft drop shadow
draw.text((tx + 3, ty + 73), line1, fill=(0, 0, 0, 180), font=title_font)
draw.text((tx, ty + 70), line1, fill=(255, 255, 255), font=title_font)

draw.text((tx + 3, ty + 153), line2, fill=(0, 0, 0, 180), font=title_font)
draw.text((tx, ty + 150), line2, fill=(56, 189, 248), font=title_font) # Sky blue highlight

# Subtitle
sub_text = "⚡ 6 款开源记忆与拟人插件 · 给她完整一生"
draw.text((tx + 2, ty + 252), sub_text, fill=(0, 0, 0, 180), font=sub_font)
draw.text((tx, ty + 250), sub_text, fill=(241, 245, 249), font=sub_font)

# Feature Tags
tags_y = ty + 330
tags = ["灵魂记忆档案", "第一视角日记", "去AI味润色", "主动搭话猫娘", "Galgame对话"]
curr_x = tx
for t in tags:
    pw, ph = draw_pill(curr_x, tags_y, t, (15, 23, 42, 210), (226, 232, 240), tag_font, pad_x=16, pad_y=8)
    curr_x += pw + 12

# Card Accent Box
box_y = ty + 420
box_w = 640
box_h = 130
draw.rounded_rectangle([tx, box_y, tx + box_w, box_y + box_h], radius=16, fill=(15, 23, 42, 200), outline=(56, 189, 248, 140), width=2)

draw.text((tx + 25, box_y + 22), "📌  告别每次重启的陌生人，摆脱冷冰冰的客服腔", fill=(224, 242, 254), font=ImageFont.truetype(font_bold, 22))
draw.text((tx + 25, box_y + 60), "自分析对话日记 · 树状记忆可回滚 · 跨会话长效保留", fill=(148, 163, 184), font=ImageFont.truetype(font_reg, 19))
draw.text((tx + 25, box_y + 90), "全部 GitHub 开源 · 零后门无捆绑 · 打造真正懂你的专属伴侣", fill=(148, 163, 184), font=ImageFont.truetype(font_reg, 19))

# Bottom Left Footer Tag
draw.text((tx, H - 75), "小黑盒首发 · 极客养成专栏 · 随手点赞充电 [cube_干杯]", fill=(148, 163, 184), font=footer_font)

# Save
out1 = Path("reports/hermes_output/stockpile_drafts/cover_waifu_whale_16_9.png")
canvas_rgb = canvas.convert("RGB")
canvas_rgb.save(out1, quality=95)

out2 = Path("C:/Users/zzx05/.gemini/antigravity/brain/1df70796-e1a9-4d4b-b590-e026bcc2348f/cover_waifu_whale_16_9.png")
canvas_rgb.save(out2, quality=95)

print(f"Cover generated at {out1} and {out2}")
