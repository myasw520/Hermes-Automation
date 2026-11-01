# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path

BASE_IMG = Path(r"C:\Users\zzx05\.gemini\antigravity\brain\1df70796-e1a9-4d4b-b590-e026bcc2348f\tech_anime_cover_1792907009828.jpg")
OUT_DIR = Path("reports/practical_tools/drafts_ready")
OUT_IMG = OUT_DIR / "custom_anime_cover_final.png"

im = Image.open(BASE_IMG).convert("RGBA")
W, H = im.size

# Create an overlay layer for typography
overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
draw = ImageDraw.Draw(overlay)

# Fonts
font_bold = r"C:\Windows\Fonts\msyhbd.ttc"
font_regular = r"C:\Windows\Fonts\msyh.ttc"

f_badge = ImageFont.truetype(font_bold, 28)
f_title = ImageFont.truetype(font_bold, 68)
f_subtitle = ImageFont.truetype(font_regular, 32)
f_pill = ImageFont.truetype(font_bold, 26)

# Add a stylish gradient / frosted dark vignette on the left/top-left where text sits
# so text has 100% contrast against the bright sky
vignette = Image.new("RGBA", (W, H), (0, 0, 0, 0))
v_draw = ImageDraw.Draw(vignette)
for x in range(int(W * 0.7)):
    alpha = int(140 * (1.0 - (x / (W * 0.7)) ** 1.5))
    v_draw.line([(x, 0), (x, H)], fill=(10, 20, 35, alpha))

im = Image.alpha_composite(im, vignette)
draw = ImageDraw.Draw(im)

# 1. Top Category Pill / Badge
badge_x, badge_y = 60, 60
badge_text = "  OPEN SOURCE TOOLKIT  ·  VOL.01  "
bbox = draw.textbbox((badge_x, badge_y), badge_text, font=f_badge)
pad_x, pad_y = 16, 8
draw.rounded_rectangle(
    [bbox[0] - pad_x, bbox[1] - pad_y, bbox[2] + pad_x, bbox[3] + pad_y],
    radius=16,
    fill=(15, 30, 60, 210),
    outline=(0, 210, 255, 230),
    width=2
)
draw.text((badge_x, badge_y), badge_text, font=f_badge, fill=(0, 230, 255, 255))

# 2. Main Title: 告别电脑精神内耗
title_x, title_y = 60, 140
title_text = "告别电脑精神内耗！"
# Shadow
draw.text((title_x + 3, title_y + 4), title_text, font=f_title, fill=(0, 0, 0, 180))
draw.text((title_x, title_y), title_text, font=f_title, fill=(255, 255, 255, 255))

# 3. Subtitle
sub_x, sub_y = 62, 235
sub_text = "右键卡顿 · 微信压画质 · 查文件抓狂 一网打尽"
draw.text((sub_x + 2, sub_y + 2), sub_text, font=f_subtitle, fill=(0, 0, 0, 160))
draw.text((sub_x, sub_y), sub_text, font=f_subtitle, fill=(220, 235, 255, 255))

# 4. Tool Pill Badges
pills = [
    ("⚡ LocalSend", (30, 144, 255), "满速隔空投送"),
    ("🛡️ ContextMenu", (46, 204, 113), "右键菜单净化"),
    ("👁️ QuickLook", (243, 156, 18), "空格秒速预览"),
]

cur_x = 60
pill_y = 310
for name, color, tag in pills:
    pill_text = f" {name} "
    p_box = draw.textbbox((cur_x, pill_y), pill_text, font=f_pill)
    pw = p_box[2] - p_box[0] + 24
    ph = p_box[3] - p_box[1] + 16
    
    # Pill background
    draw.rounded_rectangle(
        [cur_x, pill_y, cur_x + pw, pill_y + ph],
        radius=12,
        fill=(20, 30, 50, 220),
        outline=color,
        width=2
    )
    draw.text((cur_x + 12, pill_y + 6), pill_text, font=f_pill, fill=(255, 255, 255, 255))
    cur_x += pw + 18

# Bottom Tag
bot_x, bot_y = 62, H - 70
bot_text = "★ 100% 开源免费 · 无弹窗 · 单文件体验"
draw.text((bot_x + 2, bot_y + 2), bot_text, font=ImageFont.truetype(font_bold, 24), fill=(0, 0, 0, 160))
draw.text((bot_x, bot_y), bot_text, font=ImageFont.truetype(font_bold, 24), fill=(255, 220, 100, 255))

# Save
im_rgb = im.convert("RGB")
im_rgb.save(OUT_IMG, quality=95)
print(f"Cover generated successfully -> {OUT_IMG} ({im_rgb.size})")
