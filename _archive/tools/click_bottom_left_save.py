import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
        ctx = b.contexts[0]
        page = [pg for pg in ctx.pages if 'local_1793017579016_y1ajc9dw' in pg.url][0]
        
        async def on_resp(resp):
            if any(k in resp.url for k in ['link/post', 'drafts']):
                print(f"[NET {resp.status}] {resp.url[:85]}")
                try:
                    text = await resp.text()
                    print(f"  --> {text[:280]}")
                except Exception as e:
                    print(f"  --> text err: {e}")
        page.on("response", on_resp)

        # 找到左下角的保存草稿按钮
        btn = page.locator("text='保存草稿'").last
        print("Clicking bottom-left 保存草稿...")
        await btn.click()
        await page.wait_for_timeout(6000)
        print("After click URL:", page.url)

asyncio.run(main())
