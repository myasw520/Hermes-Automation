# -*- coding: utf-8 -*-
"""
小黑盒封面图自动生成器 (cover_generator.py)
============================================
替代已淘汰的 PIL 排版方案与手工 Gemini 网页版。双端点 fallback：
1. ZeroGate 内网中转（优先，零成本）：POST /v1/images/generations
   模型 gptgemini/gpt-image-2.5（上游账号池 503 时自动降级）
2. 智谱 BigModel GLM-Image（兜底，0.1 元/张）：POST /api/paas/v4/images/generations
   原生 16:9 (1728x960)，官方主打"海报/社交媒体图文 + 中文精准渲染"

产出：16:9 封面 png 落指定路径。凭证统一走 config_lib / keys_pool，不硬编码。
用法：
    python tools/cover_generator.py --prompt "轻日漫杂志风，..." --out cover.png
    python tools/cover_generator.py --style game --title "..." --out cover.png
调研依据：docs/RESEARCH-image-gen.md（2026-10-31 实抓）
"""

import sys
import os
import json
import time
import base64
import argparse
import urllib.request

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "services"))
from config_lib import GATEWAY_URL, GATEWAY_KEY, GITHUB_TOKEN  # noqa: F401

# 智谱 key 从 keys_pool 拿（ZCode-BigModel 节点）
def _load_pool():
    p = os.path.join(BASE_DIR, "config", "keys_pool.json")
    try:
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def get_bigmodel_key():
    for node in _load_pool():
        if "bigmodel" in (node.get("name") or "").lower() or "bigmodel" in (node.get("base_url") or ""):
            if node.get("is_alive", True):
                return node.get("api_key"), node.get("base_url") or "https://open.bigmodel.cn/api/paas/v4"
    return None, None

# ---------- 风格提示词模板（对应 xhh-style-bible 的封面规范） ----------
STYLE_PROMPTS = {
    # 轻日漫杂志风：track_windows_tools / track_game 都要求的 Hero Banner 规范
    "anime": (
        "16:9 horizontal magazine-style anime illustration cover, clean composition, "
        "soft cel shading, pastel light palette with one strong accent color, "
        "cozy desk / gaming setup atmosphere, subtle halftone texture, "
        "large negative space on the right third for title overlay, no text, no watermark, "
        "high detail, trending pixiv style"
    ),
    "game": (
        "16:9 horizontal gaming magazine cover illustration, dynamic anime style, "
        "vibrant energy, dramatic lighting, game controller / pixel motifs, "
        "clean right-side space for title, no text, no watermark"
    ),
}

ZEROIMAGE_MODEL = "gptgemini/gpt-image-2.5"


def gen_zerogate(prompt, size="1792x1024"):
    """ZeroGate /v1/images/generations（OpenAI images 协议，b64 或 URL 均兼容）"""
    url = f"{GATEWAY_URL.rstrip('/')}/images/generations"
    payload = json.dumps({"model": ZEROIMAGE_MODEL, "prompt": prompt, "size": size, "n": 1}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, method="POST", headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GATEWAY_KEY}",
    })
    with urllib.request.urlopen(req, timeout=180) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    item = data["data"][0]
    if item.get("b64_json"):
        return base64.b64decode(item["b64_json"]), ZEROIMAGE_MODEL
    if item.get("url"):
        with urllib.request.urlopen(item["url"], timeout=60) as r:
            return r.read(), ZEROIMAGE_MODEL
    raise RuntimeError(f"ZeroGate 响应无图片字段: {list(item.keys())}")


def gen_bigmodel(prompt, size="1728x960"):
    """智谱 GLM-Image /api/paas/v4/images/generations（返回 URL 需二次下载）"""
    key, base = get_bigmodel_key()
    if not key:
        raise RuntimeError("keys_pool 无 ZCode-BigModel 节点")
    url = f"{base.rstrip('/')}/images/generations"
    payload = json.dumps({"model": "glm-image", "prompt": prompt, "size": size}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, method="POST", headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {key}",
    })
    with urllib.request.urlopen(req, timeout=180) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    item = data["data"][0]
    if item.get("b64_json"):
        return base64.b64decode(item["b64_json"]), "glm-image"
    if item.get("url"):
        with urllib.request.urlopen(item["url"], timeout=60) as r:
            return r.read(), "glm-image"
    raise RuntimeError(f"BigModel 响应无图片字段: {list(item.keys())}")


def main():
    ap = argparse.ArgumentParser(description="小黑盒 16:9 封面自动生成（ZeroGate→GLM-Image fallback）")
    ap.add_argument("--prompt", help="完整生图提示词（英文效果更稳）")
    ap.add_argument("--style", choices=list(STYLE_PROMPTS.keys()), help="内置风格模板")
    ap.add_argument("--extra", default="", help="追加到风格模板后的补充描述")
    ap.add_argument("--out", required=True, help="输出 png 路径")
    ap.add_argument("--skip-zerogate", action="store_true", help="跳过 ZeroGate 直接走 GLM-Image")
    args = ap.parse_args()

    if args.prompt:
        prompt = args.prompt
    elif args.style:
        prompt = STYLE_PROMPTS[args.style] + (f", {args.extra}" if args.extra else "")
    else:
        ap.error("需要 --prompt 或 --style")

    attempts = []
    if not args.skip_zerogate:
        attempts.append(("ZeroGate", gen_zerogate))
    attempts.append(("GLM-Image", gen_bigmodel))

    for name, fn in attempts:
        t0 = time.time()
        try:
            img, model = fn(prompt)
            out = args.out if args.out.lower().endswith(".png") else args.out + ".png"
            os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
            with open(out, "wb") as f:
                f.write(img)
            print(f"[+] {name}({model}) 出图成功: {out} ({len(img)//1024}KB, {time.time()-t0:.1f}s)")
            print(f"    prompt: {prompt[:120]}...")
            return 0
        except Exception as e:
            print(f"[-] {name} 失败({time.time()-t0:.1f}s): {e}")
    print("[X] 全部端点失败")
    return 1


if __name__ == "__main__":
    sys.exit(main())
