# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

BASE_IMG = Path(r"C:\Users\zzx05\.gemini\antigravity\brain\1df70796-e1a9-4d4b-b590-e026bcc2348f\tech_anime_cover_1792907009828.jpg")
ARTIFACT_DIR = Path(r"C:\Users\zzx05\.gemini\antigravity\brain\1df70796-e1a9-4d4b-b590-e026bcc2348f")

# 1. Version B: Pure Wallpaper Stream (Zero Clutter)
im_clean = Image.open(BASE_IMG).convert("RGB")
# Subtle minimalist corner watermark/tag in bottom right or top left
im_clean_tag = im_clean.copy()
draw_clean = ImageDraw.Draw(im_clean_tag)
f_tag = ImageFont.truetype(r"C:\Windows\Fonts\msyhbd.ttc", 22)
# Tiny aesthetic corner mark
draw_clean.text((50, 45), "DESKTOP NOTEBOOK // 01", font=f_tag, fill=(255, 255, 255))
out_clean = ARTIFACT_DIR / "cover_v2_pure_wallpaper.png"
im_clean_tag.save(out_clean, quality=95)

# 2. Version A: Light Anime Magazine Style (No tool names, just a punchy mood hook)
im_mag = Image.open(BASE_IMG).convert("RGBA")
W, H = im_mag.size

# Soft ambient vignette on upper left
vignette = Image.new("RGBA", (W, H), (0, 0, 0, 0))
v_draw = ImageDraw.Draw(vignette)
for x in range(int(W * 0.55)):
    alpha = int(120 * (1.0 - (x / (W * 0.55)) ** 1.8))
    v_draw.line([(x, 0), (x, H)], fill=(12, 22, 38, alpha))
im_mag = Image.alpha_composite(im_mag, vignette)

draw_mag = ImageDraw.Draw(im_mag)
f_small = ImageFont.truetype(r"C:\Windows\Fonts\arial.ttf", 20)
f_bold_tag = ImageFont.truetype(r"C:\Windows\Fonts\msyhbd.ttc", 22)
f_big_hook = ImageFont.truetype(r"C:\Windows\Fonts\msyhbd.ttc", 64)
f_sub_hook = ImageFont.truetype(r"C:\Windows\Fonts\msyh.ttc", 28)

# Minimalist Japanese Magazine Header
start_x, start_y = 65, 55
draw_mag.text((start_x, start_y), "ISSUE 01  /  MINIMALIST PC GUIDE", font=f_small, fill=(0, 220, 255, 230))

# Emotion Hook (Relatable, not an ad)
# Text: 「电脑终于顺手了」
hook_text = "「电脑终于顺手了」"
draw_mag.text((start_x + 3, start_y + 45), hook_text, font=f_big_hook, fill=(0, 0, 0, 160))
draw_mag.text((start_x, start_y + 42), hook_text, font=f_big_hook, fill=(255, 255, 255, 255))

# One subtle relatable sentence
sub_line = "换掉流氓软件与折磨人的反人类细节"
draw_mag.text((start_x + 2, start_y + 132), sub_line, font=f_sub_hook, fill=(0, 0, 0, 140))
draw_mag.text((start_x, start_y + 130), sub_line, font=f_sub_hook, fill=(210, 230, 255, 255))

# Subtle bottom watermark
draw_mag.text((start_x, H - 55), "FREE & OPEN SOURCE  ·  NO ADS", font=f_small, fill=(255, 255, 255, 180))

out_mag = ARTIFACT_DIR / "cover_v2_light_magazine.png"
im_mag.convert("RGB").save(out_mag, quality=95)

print(f"Generated Version A: {out_mag}")
print(f"Generated Version B: {out_clean}")
