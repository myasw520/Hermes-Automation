import asyncio
import json
import sys
from pathlib import Path
from playwright.async_api import async_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent.parent

async def main():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
        ctx = b.contexts[0]
        page = await ctx.new_page()
        await page.goto("https://creator.xiaoheihe.cn/creator/home")
        await page.wait_for_timeout(2000)
        btn = page.locator("text='发布文章'").first
        await btn.click()
        await page.wait_for_timeout(3000)
        print("Opened clean editor:", page.url)

        # 监听网络请求
        async def on_resp(resp):
            if any(k in resp.url for k in ['link/post', 'drafts']):
                print(f"[NET {resp.status}] {resp.url[:85]}")
                try:
                    text = await resp.text()
                    print(f"  --> {text[:280]}")
                except Exception as e:
                    print(f"  --> text err: {e}")
        page.on("response", on_resp)

        # 1. 填标题 (严格 26 字，小于 30 字硬性上限)
        title = "盘15款冷门神仙开源工具：零后台专治流氓（附47图）"
        t = page.locator("div.editor-title__container .ProseMirror").first
        await t.click()
        await page.keyboard.type(title, delay=10)
        await page.wait_for_timeout(500)
        print(f"[1] 标题已填: {title} ({len(title)}/30)")

        # 2. 注入区块
        blocks_dir = BASE_DIR / "reports" / "stockpile_drafts" / "track_a_windows" / "03_15款神仙开源工具全家桶_50张实操截图糊脸"
        blocks_p = blocks_dir / "article_blocks.json"
        blocks = json.loads(blocks_p.read_text(encoding="utf-8"))
        print(f"[2] 加载 {len(blocks)} 个区块，开始注入全量 15 款工具及 47 张图...")

        ed = page.locator("div.article__edit-content--inner .ProseMirror").first
        await ed.click()

        img_counter = 0
        for idx, blk in enumerate(blocks):
            btype = blk.get("type")
            if btype == "html":
                chunk = blk.get("content", "").strip()
                if chunk.startswith("<h2>"):
                    await page.keyboard.press("Enter")
                    await page.wait_for_timeout(100)
                await page.evaluate("""html => {
                    const dt = new DataTransfer();
                    dt.setData('text/html', html);
                    dt.setData('text/plain', html.replace(/<[^>]+>/g, ''));
                    const ev = new ClipboardEvent('paste', { clipboardData: dt, bubbles: true, cancelable: true });
                    document.querySelector('div.article__edit-content--inner .ProseMirror').dispatchEvent(ev);
                }""", chunk)
                await page.wait_for_timeout(200)
            elif btype == "img":
                img_counter += 1
                ipath = blk.get("path")
                alt = blk.get("alt", "")
                await ed.click()
                await page.keyboard.press("Control+End")
                await page.wait_for_timeout(200)
                await page.locator(".editor-menu-image").first.click()
                await page.wait_for_timeout(800)
                async with page.expect_file_chooser(timeout=15000) as fc_info:
                    await page.locator(".editor-image-wrapper__box.upload").first.click()
                fc = await fc_info.value
                await fc.set_files(ipath)
                # 等待缩略图加载完成
                for _ in range(40):
                    await page.wait_for_timeout(500)
                    ready = await page.evaluate("""() => {
                        const imgs = document.querySelectorAll('.editor-image-wrapper__box-image img');
                        if (!imgs.length) return false;
                        const last = imgs[imgs.length - 1];
                        return last.complete && last.naturalWidth > 0;
                    }""")
                    if ready:
                        break
                await page.get_by_text("确定", exact=True).first.click()
                await page.wait_for_timeout(1200)

                # 填 hover 描述
                if alt:
                    inputs = page.locator(".article__image-desc-input")
                    cnt = await inputs.count()
                    if cnt > 0:
                        inp = inputs.nth(cnt - 1)
                        await inp.focus()
                        await page.wait_for_timeout(100)
                        await page.keyboard.type(alt, delay=8)

                # 定位到图后
                boxes = page.locator("div.article__edit-content--inner .article__image-box")
                n = await boxes.count()
                if n > 0:
                    await boxes.nth(n - 1).click()
                    await page.wait_for_timeout(150)
                    await page.keyboard.press("ArrowRight")
                    await page.keyboard.press("Enter")
                    await page.wait_for_timeout(150)

                print(f"  [图片 {img_counter}/47] 已注入: {Path(ipath).name}")

            print(f"  [block {idx+1}/{len(blocks)}] 完成")

        print("所有区块注入完毕，正在等待全网 CDN 状态同步...")
        for attempt in range(30):
            res = await page.evaluate("""() => {
                const ed = document.querySelector('div.article__edit-content--inner .ProseMirror');
                if (!ed) return { pending: 99 };
                const imgs = Array.from(ed.querySelectorAll('img'));
                const pending = imgs.filter(im => !im.src || im.src.startsWith('blob:') || im.getAttribute('data-original') === 'uploading').length;
                return { total: imgs.length, pending: pending };
            }""")
            print(f"  CDN 审计进度: 总图 {res['total']}, 待同步 {res['pending']} (第 {attempt+1} 次)")
            if res['pending'] == 0:
                print("  [✓] 全量图片已 100% 同步至 CDN！")
                break
            await page.wait_for_timeout(2000)

        # 3. 封面配置
        cover_p = blocks_dir / "cover_16_9.png"
        print("正在配置 16:9 封面...")
        thumb_btn = page.locator(".form-thumb .thumb-card__right, .form-thumb .thumb-card__corner, .form-thumb .creator-editor__thumb-card").first
        await thumb_btn.scroll_into_view_if_needed()
        await thumb_btn.click()
        await page.wait_for_timeout(1000)

        upload_box = page.locator(".editor-model__thumb-upload").first
        if await upload_box.count() and await upload_box.is_visible():
            async with page.expect_file_chooser(timeout=15000) as fc_info:
                await upload_box.click()
            fc = await fc_info.value
            await fc.set_files(str(cover_p))
            await page.wait_for_timeout(3500)
        else:
            reupload = page.locator(".hb-cpt__mask-wrapper button:has-text('重新上传'), .hb-cpt__mask-wrapper .upload-btn").first
            if await reupload.count():
                async with page.expect_file_chooser(timeout=15000) as fc_info:
                    await reupload.click()
                fc = await fc_info.value
                await fc.set_files(str(cover_p))
                await page.wait_for_timeout(3500)

        mask = page.locator(".hb-cpt__mask-wrapper")
        confirm_btn = mask.locator(".hb-color__btn--confirm").first
        if await confirm_btn.count():
            await confirm_btn.click()
            await page.wait_for_timeout(2500)
            print("  [✓] 16:9 封面已确认裁剪绑定！")

        # 4. 勾选激励计划与 AI 声明
        plan = page.locator(".creation-plan-select__radio:has-text('文章计划')").first
        if await plan.count():
            await plan.click()
            await page.wait_for_timeout(500)
            print("  [✓] 已选【文章计划】")

        decl_box = page.locator(".article-transshipment .selector__box").first
        if await decl_box.count():
            await decl_box.click()
            await page.wait_for_timeout(300)
            opt = page.locator(".article-transshipment .selector__pull-list-item:has-text('包含AI辅助创作')").first
            if await opt.count():
                await opt.click()
                await page.wait_for_timeout(300)
                print("  [✓] 已选【包含AI辅助创作】")

        # 5. 点击保存草稿
        save_btn = page.locator("button.editor-publish__save-draft, button:has-text('保存草稿')").first
        for _ in range(15):
            if not await save_btn.is_disabled():
                break
            await page.wait_for_timeout(500)
        print("点击保存草稿按钮...")
        await save_btn.click()
        await page.wait_for_timeout(10000)
        print("最终页面 URL:", page.url)

asyncio.run(main())
