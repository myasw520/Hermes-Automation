import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
        ctx = b.contexts[0]
        page = ctx.pages[-1]
        print("Page URL:", page.url)

        async def on_resp(resp):
            if any(k in resp.url for k in ['post', 'draft', 'link', 'article']):
                print(f"NET: {resp.status} {resp.url[:100]}")
                try:
                    text = await resp.text()
                    print(f"RESP: {text[:300]}")
                except Exception as e:
                    print("RESP ERR:", e)

        page.on('response', on_resp)

        # 检查封面
        cov = page.locator(".form-thumb .thumb-card__image img")
        cov_src = await cov.get_attribute("src") if await cov.count() else "none"
        print("Cover src:", cov_src[:60] if cov_src else "none")

        # 检查是否已有标题
        t = page.locator("div.editor-title__container .ProseMirror").first
        t_val = await t.inner_text() if await t.count() else ""
        print("Title val:", repr(t_val))

        save_btn = page.locator(".editor-publish__save-draft, button:has-text('保存草稿')").first
        if await save_btn.count():
            print("Clicking save draft...")
            await save_btn.click()
            await page.wait_for_timeout(8000)
            print("After save, URL:", page.url)
        else:
            print("Save draft button not found!")

asyncio.run(main())
