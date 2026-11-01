import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
        ctx = b.contexts[0]
        # 找到已有页面或新建
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()
        await page.bring_to_front()
        if not "/creator/editor" in page.url:
            await page.goto("https://creator.xiaoheihe.cn/creator/home")
            await page.wait_for_timeout(2000)
            
        btn = page.locator("text='发布文章'").first
        if await btn.count():
            await btn.click()
            await page.wait_for_timeout(3000)
            print("Opened editor, URL:", page.url)
        else:
            print("Could not find 发布文章 button, trying direct selector")
            btn2 = page.locator(".creator-aside__nav-item:has-text('发布文章')").first
            if await btn2.count():
                await btn2.click()
                await page.wait_for_timeout(3000)
                print("Opened editor via nav item, URL:", page.url)

asyncio.run(main())
