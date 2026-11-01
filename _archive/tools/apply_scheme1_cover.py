# -*- coding: utf-8 -*-
import asyncio
from playwright.async_api import async_playwright
import sys
from pathlib import Path

sys.path.insert(0, r"c:\Users\zzx05\Hermes-Automation\.agents\skills\post-xiaoheihe\scripts")
from xhh_common import connect, find_editor_page, log

NEW_COVER = str(Path(r"c:\Users\zzx05\Hermes-Automation\小黑盒封面_轻杂志漫风_推荐.png").resolve())

async def update_cover():
    async with async_playwright() as p:
        browser, ctx = await connect(p)
        page = find_editor_page(ctx)
        if not page:
            log("No editor page found")
            return
            
        log("Updating cover to Scheme 1 (Magazine style)...")
        # Check if drawer is open
        edit_cover = page.locator("text=修改封面")
        if not await edit_cover.count():
            # Click 发布 to open drawer
            pub_btn = page.locator("button")
            for i in range(await pub_btn.count()):
                b = pub_btn.nth(i)
                if (await b.text_content() or "").strip() == "发布":
                    await b.click()
                    await asyncio.sleep(2)
                    break
        
        edit_cover = page.locator("text=修改封面")
        if await edit_cover.count():
            await edit_cover.first.click()
            await asyncio.sleep(1)
            
            upload_box = page.locator(".editor-model__thumb-upload").first
            async with page.expect_file_chooser(timeout=10000) as fc_info:
                await upload_box.click()
            file_chooser = await fc_info.value
            await file_chooser.set_files(NEW_COVER)
            log("Uploaded Scheme 1 cover: " + NEW_COVER)
            await asyncio.sleep(2)
            
            confirm_btn = page.locator(".hb-color__btn--confirm")
            if await confirm_btn.count():
                await confirm_btn.click()
                log("Confirmed cover crop!")
                await asyncio.sleep(2)
                
            # Click 保存草稿
            save_btn = page.locator("button:has-text('保存草稿')")
            if await save_btn.count():
                await save_btn.first.click()
                log("Saved draft with Scheme 1 cover successfully!")
                await asyncio.sleep(4)

asyncio.run(update_cover())
