# -*- coding: utf-8 -*-
"""
Hermes Multi-modal Vision Quality Gate & Caption Generator
==========================================================
利用多模态视觉大模型（gpt-4o-mini）对候选图片进行人眼级质检：
1. 真实性判决：是否为真实软件运行界面（严厉淘汰 Logo、Banner、作者头像、流程图、表情包）
2. 安全与风控：是否包含微信群、QQ群、赞助打赏二维码、商业推广
3. 视觉质量：清晰度与重点可辨度（如暗色界面下小色标是否清晰）
4. 智能题注生成：基于视觉理解直接输出「真实、准确、自然」的一句话题注，彻底消除盲猜题注
"""

import os
import sys
import json
import base64
import urllib.request
from pathlib import Path
from PIL import Image

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config" / "keys_pool.json"
METADATA_CACHE_PATH = BASE_DIR / "data" / "vision_audit_cache.json"

def get_vision_client_config():
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Keys pool config not found at: {CONFIG_PATH}")
    pool = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    
    # 优先使用已验证存活且支持视觉的提供商（如 ChatAnywhere）
    chatanywhere = [x for x in pool if x.get("name") == "ChatAnywhere"]
    if chatanywhere:
        target = chatanywhere[0]
    else:
        target = pool[0]
    
    base_url = target.get("base_url", "https://api.chatanywhere.tech/v1").rstrip("/")
    api_key = target.get("api_key", "")
    model = "gpt-4o-mini"
    return base_url, api_key, model

def load_cache() -> dict:
    if METADATA_CACHE_PATH.exists():
        try:
            return json.loads(METADATA_CACHE_PATH.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}

def save_cache(cache: dict):
    METADATA_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    METADATA_CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")

def audit_image(image_path: Path | str, use_cache: bool = True) -> dict:
    image_path = Path(image_path).resolve()
    if not image_path.exists():
        return {
            "is_approved": False,
            "rejection_reason": "文件不存在",
            "suggested_caption": ""
        }

    # 检查缓存
    cache = load_cache() if use_cache else {}
    cache_key = str(image_path)
    file_mtime = str(image_path.stat().st_mtime)
    if use_cache and cache_key in cache and cache[cache_key].get("mtime") == file_mtime:
        return cache[cache_key]["result"]

    # 基础物理检查（体积 > 8MB 直接淘汰）
    sz_mb = image_path.stat().st_size / (1024 * 1024)
    if sz_mb > 8.0:
        res = {
            "is_genuine_software_ui": False,
            "contains_ad_or_qr": False,
            "visual_clarity": "low",
            "is_approved": False,
            "rejection_reason": f"文件体积超标 ({sz_mb:.2f}MB > 8MB)",
            "actual_feature_detected": "超大体积文件",
            "suggested_caption": ""
        }
        cache[cache_key] = {"mtime": file_mtime, "result": res}
        save_cache(cache)
        return res

    # 压缩为适合视觉审核的小图（若太大缩放到 1280px 以内，减少 token 消耗）
    try:
        with Image.open(image_path) as im:
            fmt = im.format if im.format in ["PNG", "JPEG", "WEBP"] else "PNG"
            # 如果是极端正方形且极小
            w, h = im.size
            if (w < 320 and h < 240) or (abs(w - h) < 15 and w <= 300):
                res = {
                    "is_genuine_software_ui": False,
                    "contains_ad_or_qr": False,
                    "visual_clarity": "low",
                    "is_approved": False,
                    "rejection_reason": f"微型图标或作者头像 ({w}x{h})",
                    "actual_feature_detected": "Logo/图标",
                    "suggested_caption": ""
                }
                cache[cache_key] = {"mtime": file_mtime, "result": res}
                save_cache(cache)
                return res

            # 读取原始字节
            raw_bytes = image_path.read_bytes()
            b64_img = base64.b64encode(raw_bytes).decode("utf-8")
            mime_type = f"image/{fmt.lower()}" if fmt.lower() in ["png", "jpeg", "webp", "gif"] else "image/png"
    except Exception as e:
        return {
            "is_approved": False,
            "rejection_reason": f"图像解析损坏: {e}",
            "suggested_caption": ""
        }

    # 调用 OpenAI 兼容多模态接口
    base_url, api_key, model = get_vision_client_config()
    prompt = """你是一个极其严苛的技术文章配图审核员。请审查这张图片，并以严格的 JSON 格式输出：
{
  "is_genuine_software_ui": true/false, // 必须是真实电脑/手机软件运行中的操作界面、设置面板或终端窗口。如果这只是一张宣传横幅(Banner)、软件Logo图标、作者头像、流程架构图、纯文字告示、海报，一律判定为 false！
  "contains_ad_or_qr": true/false,     // 画面任何角落是否包含微信群、QQ群二维码、打赏赞助码、公众号引流或商业广告？有则必须判定为 true！
  "visual_clarity": "high/medium/low", // 画面是否清晰可辨？如果界面太暗、过小或者根本看不清核心特征，判为 low。
  "actual_feature_detected": "从画面实际看到的具体软件界面或功能，15字内",
  "suggested_caption": "用于文章插图的原生自然题注，格式为'图：......'，必须严格描述图中看到的真实界面与功能，不可盲猜，20字内",
  "rejection_reason": "若淘汰请说明具体原因（如'纯宣传Banner无UI'、'包含QQ群二维码'、'正方形Logo图标'等）；合格则为 null"
}
只输出纯 JSON，绝对不要输出任何 markdown 格式标记、前缀或额外文字。"""

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{b64_img}"}}
                ]
            }
        ],
        "max_tokens": 260,
        "temperature": 0.1
    }

    url = f"{base_url}/chat/completions"
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=18) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            content = data["choices"][0]["message"]["content"].strip()
            # 清除可能包裹的 ```json
            if content.startswith("```"):
                content = content.strip("`").replace("json\n", "").strip()
            result = json.loads(content)
            
            # 综合判定
            is_ui = result.get("is_genuine_software_ui", False)
            has_ad = result.get("contains_ad_or_qr", False)
            clarity = result.get("visual_clarity", "medium")
            
            is_approved = is_ui and not has_ad and clarity != "low"
            result["is_approved"] = is_approved
            
            cache[cache_key] = {"mtime": file_mtime, "result": result}
            save_cache(cache)
            return result
    except Exception as e:
        print(f"  [AI 视觉审核异常] {image_path.name}: {e}")
        return {
            "is_approved": False,
            "rejection_reason": f"API调用失败: {e}",
            "suggested_caption": ""
        }

def audit_directory(dir_path: Path | str, auto_delete_bad: bool = True) -> list:
    dir_path = Path(dir_path).resolve()
    print(f"\n=======================================================")
    print(f"  AI 视觉质检主编启动: {dir_path.name}")
    print(f"=======================================================")
    
    valid_extensions = [".png", ".jpg", ".jpeg", ".webp", ".gif"]
    images = [f for f in dir_path.glob("**/*.*") if f.suffix.lower() in valid_extensions and "hero" not in f.name.lower() and "cover" not in f.name.lower()]
    
    print(f"发现待质检图片: {len(images)} 张")
    approved_list = []
    rejected_count = 0

    for idx, img in enumerate(images):
        print(f"\n[{idx+1}/{len(images)}] 审核: {img.name} ...")
        res = audit_image(img)
        if res.get("is_approved"):
            feature = res.get("actual_feature_detected", "实操界面")
            caption = res.get("suggested_caption", f"图：{feature}")
            print(f"   [✓ 通过] 识别界面: {feature}")
            print(f"   --> 智能题注: {caption}")
            approved_list.append({
                "path": str(img),
                "feature": feature,
                "caption": caption
            })
        else:
            reason = res.get("rejection_reason", "不符合实机UI标准")
            print(f"   [✗ 淘汰] 原因: {reason}")
            rejected_count += 1
            if auto_delete_bad:
                try:
                    img.unlink()
                    print(f"   --> 已物理粉碎坏图: {img.name}")
                except Exception as e:
                    print(f"   --> 删除失败: {e}")

    print(f"\n=======================================================")
    print(f"  质检完成: 通过 {len(approved_list)} 张 | 淘汰 {rejected_count} 张")
    print(f"=======================================================\n")
    return approved_list

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="多模态 AI 配图审查与题注生成器")
    parser.add_argument("target_dir", nargs="?", default="reports/niche_gems/assets", help="待审查目录")
    parser.add_argument("--no-delete", action="store_true", help="不自动删除坏图")
    args = parser.parse_args()
    
    audit_directory(args.target_dir, auto_delete_bad=not args.no_delete)
