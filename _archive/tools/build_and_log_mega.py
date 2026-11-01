import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright

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
        print("Opened editor:", page.url)

        # 监听控制台和网络请求
        page.on("console", lambda msg: print(f"[CONSOLE {msg.type}] {msg.text[:120]}"))
        async def on_resp(resp):
            if any(k in resp.url for k in ['link/post', 'drafts', 'error']):
                print(f"[NET {resp.status}] {resp.url[:90]}")
                try:
                    text = await resp.text()
                    print(f"  --> {text[:300]}")
                except Exception as e:
                    print(f"  --> text err: {e}")
        page.on("response", on_resp)

        # 填标题 (严格 <= 30 字)
        title = "盘15款冷门神仙开源工具：零后台专治流氓（50图糊脸）"
        t = page.locator("div.editor-title__container .ProseMirror").first
        await t.click()
        await page.keyboard.type(title, delay=10)
        await page.wait_for_timeout(500)

        # 注入 article_blocks.json
        blocks_p = BASE_DIR / "reports" / "stockpile_drafts" / "track_a_windows" / "03_15款神仙开源工具全家桶_50张实操截图糊脸" / "article_blocks.json"
        blocks = json.loads(blocks_p.read_text(encoding="utf-8"))
        print(f"Loaded {len(blocks)} blocks. Starting insertion...")

        ed = page.locator("div.article__edit-content--inner .ProseMirror").first
        await ed.click()

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
                await page.wait_for_timeout(150)
            elif btype == "img":
                ipath = blk.get("path")
                alt = blk.get("alt", "")
                await ed.click()
                await page.keyboard.press("Control+End")
                await page.wait_for_timeout(150)
                await page.locator(".editor-menu-image").first.click()
                await page.wait_for_timeout(600)
                async with page.expect_file_chooser(timeout=15000) as fc_info:
                    await page.locator(".editor-image-wrapper__box.upload").first.click()
                fc = await fc_info.value
                await fc.set_files(ipath)
                # 等待缩略图加载
                for _ in range(25):
                    await page.wait_for_timeout(400)
                    ready = await page.evaluate("""() => {
                        const imgs = document.querySelectorAll('.editor-image-wrapper__box-image img');
                        if (!imgs.length) return false;
                        const last = imgs[imgs.length - 1];
                        return last.complete && last.naturalWidth > 0;
                    }""")
                    if ready:
                        break
                await page.get_by_text("确定", exact=True).first.click()
                await page.wait_for_timeout(1000)

                # 填 hover 描述
                if alt:
                    inputs = page.locator(".article__image-desc-input")
                    cnt = await inputs.count()
                    if cnt > 0:
                        inp = inputs.nth(cnt - 1)
                        await inp.focus()
                        await page.wait_for_timeout(100)
                        await page.keyboard.type(alt, delay=10)

                # 定位到图后
                boxes = page.locator("div.article__edit-content--inner .article__image-box")
                n = await boxes.count()
                if n > 0:
                    await boxes.nth(n - 1).click()
                    await page.wait_for_timeout(150)
                    await page.keyboard.press("ArrowRight")
                    await page.keyboard.press("Enter")
                    await page.wait_for_timeout(150)
            
            if (idx + 1) % 15 == 0:
                print(f"  Inserted {idx + 1}/{len(blocks)} blocks...")

        print("All blocks inserted! Checking CDN readiness...")
        # 等待所有 CDN 图片完全就绪
        for attempt in range(30):
            pending = await page.evaluate("""() => {
                const imgs = document.querySelectorAll('div.article__edit-content--inner img');
                return [...imgs].filter(im => !im.src || im.src.startsWith('blob:') || im.naturalWidth === 0).length;
            }""")
            print(f"  CDN pending images: {pending} (attempt {attempt+1})")
            if pending == 0:
                break
            await page.wait_for_timeout(2000)

        # 勾选激励计划
        plan = page.locator(".creation-plan-select__radio:has-text('文章计划')").first
        if await plan.count():
            await plan.click()
            await page.wait_for_timeout(500)

        # 声明
        decl_box = page.locator(".article-transshipment .selector__box").first
        if await decl_box.count():
            await decl_box.click()
            await page.wait_for_timeout(300)
            opt = page.locator(".article-transshipment .selector__pull-list-item:has-text('包含AI辅助创作')").first
            if await opt.count():
                await opt.click()
                await page.wait_for_timeout(300)

        # 检查保存按钮状态
        save_btn = page.locator("button.editor-publish__save-draft, button:has-text('保存草稿')").first
        for w in range(10):
            dis = await save_btn.is_disabled()
            print(f"Save button disabled? {dis}")
            if not dis:
                break
            await page.wait_for_timeout(1000)

        print("Clicking save draft button now...")
        await save_btn.click()
        await page.wait_for_timeout(10000)
        print("Final URL:", page.url)

asyncio.run(main())
