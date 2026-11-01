# -*- coding: utf-8 -*-
"""小黑盒文章编辑器：批量插图 + WPS 式图文排版 + 封面与发布设置（一键构建长文）

支持两种模式：
1. 结构化区块模式（推荐，排版最精细，支持 h2/h3 标题与原生图片题注）：
   python xhh_build.py --title "微信压画质右键卡两秒？这3个良心开源工具直接封神" \
       --article-json article_blocks.json \
       --cover "小黑盒封面.png" \
       --plan-article \
       --declare-ai \
       --save-draft

   article_blocks.json 格式：
   [
     {"type": "html", "content": "<p>导语...</p><h2>一、LocalSend</h2><p>...</p><h3>【实测体验】...</h3>"},
     {"type": "img", "path": "images/01.png", "alt": "LocalSend 电脑端主界面"},
     {"type": "html", "content": "<p>▲ 描述文字...</p>"}
   ]

2. 传统目录与条目模式（按 --layout 选 caption 或 gallery）：
   python xhh_build.py --layout caption \
       --title "标题 20 字内" \
       --intro intro.txt --outro outro.txt \
       --items items.json --hashtags "#AI #程序员" \
       --cover "封面.png" \
       --plan-article --declare-ai \
       --save-draft \
       "D:\图片目录"

   items.json 格式：
   [{"name": "01 WorkBuddy", "desc": "按 token 折积分……", "alt": "WorkBuddy 面板"}, ...]

前置：9223 Chrome 已启动并登录（双击 scripts/start_chrome.bat）。
"""
from __future__ import annotations

import argparse
import asyncio
import glob
import json
import os
import sys
from pathlib import Path

try:
    from playwright.async_api import async_playwright
except ImportError:
    from patchright.async_api import async_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
from xhh_common import (  # noqa: E402
    EDITOR_ARTICLE,
    EDITOR_TITLE,
    connect,
    find_editor_page,
    log,
    print_config,
    require_login,
)


def collect(paths):
    out = []
    for p in paths:
        p = Path(p)
        if p.is_dir():
            patterns = ["*.png", "*.jpg", "*.jpeg", "*.webp", "*.gif"]
            files = []
            for pat in patterns:
                files.extend(glob.glob(str(p / pat)))
                files.extend(glob.glob(str(p / pat.upper())))
            out.extend(sorted(set(files)))
        elif p.exists():
            out.append(str(p))
        else:
            log("[warn] 不存在，跳过: %s" % p)
    return out


async def wait_editor(page, timeout_s=40):
    for _ in range(timeout_s):
        if await page.locator(EDITOR_ARTICLE).count():
            return True
        await page.wait_for_timeout(1000)
    return False


async def get_editor_img_count(page):
    """获取当前编辑器内真实存在的图片数量"""
    return await page.evaluate(
        "() => document.querySelectorAll('div.article__edit-content--inner .article__image-box img').length"
    )


async def paste_html(page, html: str):
    """通过剪贴板事件向 ProseMirror 干净地注入 HTML 片段，保留 h2/h3/b 等语义排版"""
    await page.evaluate("""html => {
        const dt = new DataTransfer();
        dt.setData('text/html', html);
        dt.setData('text/plain', html.replace(/<[^>]+>/g, ''));
        const ev = new ClipboardEvent('paste', {
            clipboardData: dt,
            bubbles: true,
            cancelable: true
        });
        const ed = document.querySelector('div.article__edit-content--inner .ProseMirror');
        if (ed) ed.dispatchEvent(ev);
    }""", html)
    await page.wait_for_timeout(300)


async def insert_img_block(page, img_path: str, alt_text: str = ""):
    """插入单张图片并键入原生图片描述（data-description）"""
    ed = page.locator(EDITOR_ARTICLE).first
    await ed.click()
    await page.keyboard.press("Control+End")
    await page.wait_for_timeout(250)

    await page.locator(".editor-menu-image").first.click()
    await page.wait_for_timeout(800)

    resolved_path = str(Path(img_path).resolve())
    async with page.expect_file_chooser(timeout=15000) as fc_info:
        await page.locator(".editor-image-wrapper__box.upload").first.click()
    file_chooser = await fc_info.value
    await file_chooser.set_files(resolved_path)

    for _ in range(35):
        await page.wait_for_timeout(600)
        ready = await page.evaluate("""() => {
            const imgs = document.querySelectorAll('.editor-image-wrapper__box-image img');
            if (!imgs.length) return false;
            const last = imgs[imgs.length - 1];
            return last.complete && last.naturalWidth > 0;
        }""")
        if ready:
            break

    await page.get_by_text("确定", exact=True).first.click()
    await page.wait_for_timeout(1500)

    # 填入原生 hover 描述
    if alt_text:
        inputs = page.locator(".article__image-desc-input")
        cnt = await inputs.count()
        if cnt > 0:
            inp = inputs.nth(cnt - 1)
            await inp.focus()
            await page.wait_for_timeout(200)
            is_active = await page.evaluate("() => document.activeElement.classList.contains('article__image-desc-input')")
            if is_active:
                await page.keyboard.type(alt_text, delay=15)
                log(f"  [alt filled] '{alt_text}'")
            else:
                log(f"  [alt warn] 焦点不在输入框，跳过以避免泄露到正文")

    # 光标重新定位到图片后方
    boxes = page.locator("div.article__edit-content--inner .article__image-box")
    n = await boxes.count()
    if n > 0:
        await boxes.nth(n - 1).click()
        await page.wait_for_timeout(200)
        await page.keyboard.press("ArrowRight")
        await page.keyboard.press("Enter")
        await page.wait_for_timeout(200)


async def insert_one(page, img, expected_index=None, max_retries=3):
    """在当前光标处插入一张图，带严格前置/后置计数校验与自动重试"""
    before_count = await get_editor_img_count(page)
    if expected_index is not None and before_count != expected_index:
        raise RuntimeError(
            f"[FATAL] 图片数量状态异常！准备插入第 {expected_index + 1} 张图，"
            f"但当前编辑器内已有 {before_count} 张图（预期为 {expected_index} 张）！"
        )

    for attempt in range(1, max_retries + 1):
        try:
            await page.locator(".editor-menu-image").first.click()
            await page.wait_for_timeout(1000)

            chooser_task = asyncio.create_task(page.wait_for_event("filechooser", timeout=20000))
            await page.locator(".editor-image-wrapper__box.upload").first.click()
            chooser = await chooser_task
            await chooser.set_files([img])

            ready = False
            for _ in range(40):
                await page.wait_for_timeout(800)
                thumbs = await page.evaluate(
                    """() => {
                        const imgs = document.querySelectorAll('.editor-image-wrapper__box-image img');
                        if (imgs.length === 0) return 0;
                        const last = imgs[imgs.length - 1];
                        return (last.complete && last.naturalWidth > 0) ? imgs.length : 0;
                    }"""
                )
                if thumbs > 0:
                    ready = True
                    break

            if not ready:
                log(f"  [retry] 第 {before_count + 1} 张图缩略图上传未就绪（第 {attempt} 次）")
                await page.keyboard.press("Escape")
                await page.wait_for_timeout(1200)
                continue

            await page.get_by_text("确定", exact=True).first.click()
            await page.wait_for_timeout(2000)

            inserted = False
            for _ in range(25):
                after_count = await get_editor_img_count(page)
                if after_count == before_count + 1:
                    inserted = True
                    break
                await page.wait_for_timeout(400)

            if inserted:
                log(f"  [OK] 第 {before_count + 1} 张图插入成功并确认")
                return True

            log(f"  [retry] 点击确定后图片数未增加（当前仍为 {await get_editor_img_count(page)}"
                f"，预期 {before_count + 1}），重试第 {attempt} 次...")
            await page.keyboard.press("Escape")
            await page.wait_for_timeout(1500)

        except Exception as e:
            log(f"  [retry] 插入异常（第 {attempt} 次）: {e}")
            try:
                await page.keyboard.press("Escape")
            except Exception:
                pass
            await page.wait_for_timeout(1500)

    raise RuntimeError(
        f"[FATAL] 第 {before_count + 1} 张图 [{img}] 连续 {max_retries} 次插入失败！"
    )


async def fill_alt(page, text, index=-1):
    """填图片 hover 描述（data-description）。必须用键盘输入。"""
    if not text:
        return True
    inputs = page.locator(".article__image-desc-input")
    n = await inputs.count()
    if n == 0:
        return False
    inp = inputs.nth(n + index if index < 0 else index)
    for attempt in range(4):
        try:
            await inp.scroll_into_view_if_needed(timeout=3000)
            await inp.click(timeout=5000)
        except Exception:
            log("  [retry] 图注输入框点不到（第 %d 次）" % (attempt + 1))
            await page.wait_for_timeout(600)
            continue
        await page.wait_for_timeout(250)
        try:
            await inp.fill("")
        except Exception:
            pass
        await page.wait_for_timeout(120)
        await page.keyboard.type(text, delay=12)
        await page.wait_for_timeout(400)
        val = await inp.input_value()
        if val.strip() == text.strip():
            return True
        log("  [retry] 图注未写入（第 %d 次），当前值=%r" % (attempt + 1, val))
        await page.wait_for_timeout(500)
    return False


async def fill_pending_alts(page, pending):
    """补填之前挂起的题注"""
    done = []
    for idx, text in pending:
        if await fill_alt(page, text, index=idx):
            done.append(idx)
        else:
            log("  [warn] 第 %d 张图的 hover 题注仍失败" % (idx + 1))
    return done


async def type_after_last_image(page, lines):
    """在最后一张图之后插入若干段落（每行一段）"""
    boxes = page.locator("div.article__edit-content--inner .article__image-box")
    n = await boxes.count()
    await boxes.nth(n - 1).click()
    await page.wait_for_timeout(250)
    await page.keyboard.press("ArrowRight")
    await page.wait_for_timeout(180)
    for line in lines:
        await page.keyboard.press("Enter")
        await page.wait_for_timeout(200)
        await page.keyboard.insert_text(line)
        await page.wait_for_timeout(250)


async def insert_gallery(page, images):
    """所有图一次传完，连排"""
    ed = page.locator(EDITOR_ARTICLE).first
    await ed.click()
    await page.keyboard.press("Control+End")
    await page.wait_for_timeout(300)

    await page.locator(".editor-menu-image").first.click()
    await page.wait_for_timeout(1200)
    chooser_task = asyncio.create_task(page.wait_for_event("filechooser", timeout=20000))
    await page.locator(".editor-image-wrapper__box.upload").first.click()
    chooser = await chooser_task
    await chooser.set_files(images)
    log("[gallery] 已提交 %d 张，等缩略图..." % len(images))

    for _ in range(90):
        await page.wait_for_timeout(2000)
        thumbs = await page.evaluate(
            "() => document.querySelectorAll('.editor-image-wrapper__box-image img').length"
        )
        if thumbs >= len(images):
            break
    await page.get_by_text("确定", exact=True).first.click()
    await page.wait_for_timeout(4000)
    await ed.click()
    st = await page.evaluate(
        """() => {
            const c = document.querySelector('div.article__edit-content--inner .ProseMirror');
            return {imgs: c.querySelectorAll('img').length, blocks: c.children.length};
        }"""
    )
    log("[gallery] 正文图 %d 张，块数 %d" % (st["imgs"], st["blocks"]))


async def configure_publish_settings(page, cover_path: str = None, plan_article: bool = False, declare_ai: bool = False):
    """设置创作计划、上传并裁剪封面、设置 AI 辅助创作声明"""
    log("[settings] 正在配置右侧发布选项与封面...")

    # 1. 创作计划 -> 参与
    if plan_article or cover_path:
        plan_btn = page.locator(".creation-plan-join .switch__button").first
        for _ in range(5):
            is_active = await page.locator(".creation-plan-join .switch__true-label.active").count()
            if is_active:
                break
            await plan_btn.scroll_into_view_if_needed()
            await plan_btn.click()
            await page.wait_for_timeout(1000)
        log("  [✓] 创作计划已勾选【参与】")

        if plan_article:
            article_plan = page.locator(".creation-plan-select__radio:has-text('文章计划')").first
            if await article_plan.count():
                await article_plan.click()
                await page.wait_for_timeout(600)
                log("  [✓] 已选【文章计划】")

    # 2. 上传封面（等待 .form-thumb 渲染）
    if cover_path:
        cp = Path(cover_path).resolve()
        if not cp.exists():
            log(f"  [warn] 封面文件不存在，跳过上传: {cover_path}")
        else:
            try:
                await page.locator(".form-thumb").wait_for(timeout=6000)
                # 必须优先且精确定位到 .thumb-card__corner 并强制触发点击打开弹窗
                thumb_btn = page.locator(".form-thumb .thumb-card__corner").first
                if not await thumb_btn.count():
                    thumb_btn = page.locator(".form-thumb .creator-editor__thumb-card, .form-thumb .thumb-card__right").first
                await thumb_btn.scroll_into_view_if_needed()
                await thumb_btn.click(force=True)
                await page.wait_for_timeout(1500)

                # 等待上传弹窗就绪
                await page.locator(".editor__model-frame").wait_for(timeout=5000)
                upload_trigger = page.locator(".editor-model__thumb-upload, .editor-model__thumb-clip-intro--btn, button:has-text('重新上传')").first
                log(f"  正在上传封面: {cp}")
                async with page.expect_file_chooser(timeout=15000) as fc_info:
                    await upload_trigger.click(force=True)
                fc = await fc_info.value
                await fc.set_files(str(cp))
                await page.wait_for_timeout(3000)

                # 确认裁剪 (16:9) 并提交
                confirm_btn = page.locator(".editor__model-frame button.hb-color__btn--confirm, .editor__model-frame button:has-text('确定')").first
                if await confirm_btn.count():
                    await confirm_btn.click(force=True)
                    await page.wait_for_timeout(3000)

                card_img = page.locator(".form-thumb img.hb-cpt__image-elem")
                src = await card_img.get_attribute("src") if await card_img.count() else ""
                if src:
                    log(f"  [✓] 封面上传与裁剪绑定完成！CDN: {src[:60]}...")
                else:
                    log("  [warn] 封面绑定后未检测到 CDN src")
            except Exception as e:
                log(f"  [warn] 封面上传配置异常: {e}")

    # 3. 其他声明 -> 包含AI辅助创作
    if declare_ai:
        try:
            decl_box = page.locator(".article-transshipment .selector__box").first
            await decl_box.scroll_into_view_if_needed()
            await decl_box.click()
            await page.wait_for_timeout(500)
            ai_opt = page.locator(".article-transshipment .selector__pull-list-item:has-text('包含AI辅助创作')").first
            await ai_opt.click()
            await page.wait_for_timeout(500)
            decl_val = await page.locator(".article-transshipment .selector__active").inner_text()
            log(f"  [✓] 其他声明已选【{decl_val}】")
        except Exception as e:
            log(f"  [warn] 其他声明设置异常: {e}")


async def main():
    ap = argparse.ArgumentParser(description="小黑盒全自动排版与草稿生成工具")
    ap.add_argument("paths", nargs="*", default=[], help="图片文件或目录（传统模式）")
    ap.add_argument("--article-json", default="", help="结构化排版 JSON 文件路径（包含 html 与 img 区块，推荐）")
    ap.add_argument("--layout", choices=["caption", "gallery"], default="caption", help="传统模式图文版式")
    ap.add_argument("--title", default="", help="文章标题")
    ap.add_argument("--cover", default="", help="16:9 封面图片路径")
    ap.add_argument("--plan-article", action="store_true", help="自动勾选创作者激励【文章计划】")
    ap.add_argument("--declare-ai", action="store_true", help="自动声明【包含AI辅助创作】")
    ap.add_argument("--auto-open", action="store_true", help="若无空白编辑器则自动打开文章编辑器")
    ap.add_argument("--intro", default="", help="导语文本文件（传统模式）")
    ap.add_argument("--outro", default="", help="收尾文本文件（传统模式）")
    ap.add_argument("--items", default="", help="条目 JSON: [{name, desc, alt}]（传统模式）")
    ap.add_argument("--hashtags", default="", help="结尾话题标签，如 '#AI #程序员'")
    ap.add_argument("--save-draft", action="store_true", help="排版完成后自动点击「保存草稿」")
    args = ap.parse_args()

    print_config()

    async with async_playwright() as p:
        browser, ctx = await connect(p)
        page = find_editor_page(ctx)

        if page is None or args.auto_open:
            if page is None:
                log("[info] 未发现活动编辑器标签页，正在新开文章编辑器...")
                page = await ctx.new_page()
            await page.goto("https://creator.xiaoheihe.cn/creator/editor/draft/article")
            await page.wait_for_timeout(3500)
        else:
            if "/creator/editor/edit/" in page.url:
                log("[warn] 当前是已保存草稿的编辑页，该页不会回填旧正文。")
                log("       建议点「新建创作 → 发布文章」开一个空白编辑器。")
            await page.bring_to_front()
            await page.wait_for_timeout(800)

        log("[0] 目标编辑器: %s" % page.url[:90])

        if not await wait_editor(page):
            log("[FATAL] 编辑器未渲染（多半是登录态过期或未扫码）")
            await require_login(page)
            await browser.close()
            return 1

        if not await require_login(page):
            await browser.close()
            return 1

        # 安全防线：编辑器内已有内容时防止误覆盖
        existing = await page.evaluate(
            """() => {
                const c = document.querySelector('div.article__edit-content--inner .ProseMirror');
                const t = document.querySelector('div.editor-title__container .ProseMirror');
                return {
                    imgs: c ? c.querySelectorAll('img').length : 0,
                    len: c ? (c.innerText || '').trim().length : 0,
                    title: t ? (t.innerText || '').trim() : ''
                };
            }"""
        )
        if existing["imgs"] or existing["len"] > 1 or existing["title"]:
            log("[FATAL] 目标编辑器已有内容，为防覆盖已停止：")
            log("       标题=%r 图=%d 字=%d" % (existing["title"][:30], existing["imgs"], existing["len"]))
            log("       请新建一个空白「发布文章」编辑器再运行。")
            await browser.close()
            return 2

        # 1. 填写标题
        if args.title:
            title_to_type = args.title.strip()
            if len(title_to_type) > 30:
                log(f"  [warn] 标题超过小黑盒 30 字硬性上限（当前 {len(title_to_type)} 字），自动截断至 30 字以防锁死保存按钮！")
                title_to_type = title_to_type[:30]
            t = page.locator(EDITOR_TITLE).first
            await t.click()
            await page.keyboard.type(title_to_type, delay=8)
            await page.wait_for_timeout(500)
            log(f"[1] 标题已填: {title_to_type} ({len(title_to_type)}/30)")

        # 2. 正文生成
        if args.article_json:
            # 模式 A：现代语义区块生成
            p_json = Path(args.article_json)
            if not p_json.exists():
                log(f"[FATAL] 找不到指定的 article_json: {args.article_json}")
                await browser.close()
                return 1
            blocks = json.loads(p_json.read_text(encoding="utf-8"))
            log(f"[blocks] 正在加载结构化区块（共 {len(blocks)} 个）...")

            for idx, blk in enumerate(blocks):
                btype = blk.get("type")
                if btype == "html":
                    chunk = blk.get("content", "").strip()
                    if chunk.startswith("<h2>"):
                        await page.keyboard.press("Enter")
                        await page.wait_for_timeout(150)
                    await paste_html(page, chunk)
                elif btype == "img":
                    ipath = blk.get("path")
                    alt = blk.get("alt", "")
                    log(f"  [img {idx+1}/{len(blocks)}] 插入图片: {ipath}")
                    await insert_img_block(page, ipath, alt)
            await page.wait_for_timeout(800)
            log("[2] 结构化区块全部注入完成")

        else:
            # 模式 B：传统图片列表生成
            images = collect(args.paths)
            if not images:
                log("[FATAL] 没找到图片（未指定图片路径且未传入 --article-json）")
                await browser.close()
                return 1

            items = []
            if args.items:
                items = json.loads(Path(args.items).read_text(encoding="utf-8"))
            intro = Path(args.intro).read_text(encoding="utf-8").strip() if args.intro else ""
            outro = Path(args.outro).read_text(encoding="utf-8").strip() if args.outro else ""

            ed = page.locator(EDITOR_ARTICLE).first
            if intro:
                await ed.click()
                await page.keyboard.insert_text(intro)
                await page.wait_for_timeout(600)

            if args.layout == "gallery":
                await ed.click()
                await page.keyboard.press("Control+End")
                await page.keyboard.press("Enter")
                await page.wait_for_timeout(300)
                await insert_gallery(page, images)
                if items:
                    await ed.click()
                    await page.keyboard.press("Control+End")
                    await page.wait_for_timeout(300)
                    await page.keyboard.press("Enter")
                    await page.wait_for_timeout(200)
                    block = "\n".join(
                        ("%s：%s" % (it["name"], it["desc"])) if it.get("desc") else it["name"]
                        for it in items
                    )
                    await page.keyboard.insert_text(block)
                    await page.wait_for_timeout(1000)
                    log("[2] 文案列表已填")
            else:
                pending_alts = []
                for idx, img in enumerate(images):
                    await ed.click()
                    await page.keyboard.press("Control+End")
                    await page.wait_for_timeout(250)
                    await page.keyboard.press("Enter")
                    await page.wait_for_timeout(200)

                    await insert_one(page, img, expected_index=idx)

                    current_imgs = await get_editor_img_count(page)
                    if current_imgs != idx + 1:
                        raise RuntimeError(
                            f"[FATAL] 图片与文案索引错位！第 {idx + 1} 项文案即将录入，"
                            f"但检测到编辑器中只有 {current_imgs} 张图（预期为 {idx + 1} 张）！"
                        )

                    if items and idx < len(items):
                        it = items[idx]
                        if it.get("alt"):
                            pending_alts.append((idx, it["alt"]))
                        lines = [it["name"]] if it.get("name") else []
                        if it.get("desc"):
                            lines.append(it["desc"])
                        if lines:
                            await type_after_last_image(page, lines)

                if pending_alts:
                    log("[alt] 补填 %d 条图片题注..." % len(pending_alts))
                    await fill_pending_alts(page, pending_alts)

            if outro or args.hashtags:
                await ed.click()
                await page.keyboard.press("Control+End")
                await page.wait_for_timeout(300)
                for chunk in [outro, args.hashtags]:
                    if chunk:
                        await page.keyboard.press("Enter")
                        await page.keyboard.press("Enter")
                        await page.wait_for_timeout(200)
                        await page.keyboard.insert_text(chunk)
                        await page.wait_for_timeout(400)

        # 3. 配置发布设置（封面、激励计划、声明）
        if args.cover or args.plan_article or args.declare_ai:
            await configure_publish_settings(
                page,
                cover_path=args.cover,
                plan_article=args.plan_article,
                declare_ai=args.declare_ai
            )
            await page.wait_for_timeout(1000)

        # 4. 终局状态校验
        st = await page.evaluate(
            """() => {
                const c = document.querySelector('div.article__edit-content--inner .ProseMirror');
                return {imgs: c ? c.querySelectorAll('img').length : 0,
                        blocks: c ? c.children.length : 0,
                        len: c ? c.innerText.length : 0,
                        alts: [...document.querySelectorAll('.article__image-desc-input')].map(i=>i.value).filter(Boolean).length};
            }"""
        )
        log("[N] 终局状态: " + json.dumps(st, ensure_ascii=False))

        # 5. 保存草稿
        if args.save_draft:
            log("正在确认所有图片 CDN 状态就绪...")
            for _ in range(15):
                pending = await page.evaluate("""() => {
                    const imgs = document.querySelectorAll('div.article__edit-content--inner img');
                    return [...imgs].filter(im => !im.src || im.src.startsWith('blob:')).length;
                }""")
                if pending == 0:
                    break
                await page.wait_for_timeout(1000)
            await page.wait_for_timeout(2000)

            save_btn = page.locator("button.editor-publish__save-draft, button:has-text('保存草稿')").first
            if await save_btn.count():
                await save_btn.scroll_into_view_if_needed()
                # 等待按钮解除 disabled
                for _ in range(10):
                    if not await save_btn.is_disabled():
                        break
                    await page.wait_for_timeout(500)
                await save_btn.click()
                await page.wait_for_timeout(8000)
                log("[S] 已点击「保存草稿」！草稿已就绪，可随时在手机 App 确认发布。")

        await browser.close()
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
