# -*- coding: utf-8 -*-
import asyncio
import sys
from pathlib import Path
from playwright.async_api import async_playwright

sys.path.insert(0, r"c:\Users\zzx05\Hermes-Automation\.agents\skills\post-xiaoheihe\scripts")
from xhh_common import connect, find_editor_page, log

COVER_PATH = str(Path("reports/practical_tools/drafts_ready/custom_anime_cover_final.png").resolve())

async def upload_cover():
    async with async_playwright() as p:
        browser, ctx = await connect(p)
        page = find_editor_page(ctx)
        if not page:
            log("No editor found")
            return
            
        log("Uploading custom cover...")
        
        # Check if "点击上传" or .editor-model__thumb-upload is present
        upload_box = page.locator(".editor-model__thumb-upload")
        if not await upload_box.count():
            # If modal is not open, click 修改封面
            edit_cover = page.locator("text=修改封面")
            if await edit_cover.count():
                await edit_cover.first.click()
                await asyncio.sleep(1)
        
        upload_box = page.locator(".editor-model__thumb-upload").first
        async with page.expect_file_chooser(timeout=10000) as fc_info:
            await upload_box.click()
            log("Clicked upload box, waiting for file chooser...")
        file_chooser = await fc_info.value
        await file_chooser.set_files(COVER_PATH)
        log(f"Set cover file: {COVER_PATH}")
        await asyncio.sleep(3)
        
        # Click 确定 in the crop modal
        confirm_btn = page.locator("button:has-text('确定'), button:has-text('完成'), button:has-text('保存')")
        if await confirm_btn.count():
            for i in range(await confirm_btn.count()):
                b = confirm_btn.nth(i)
                if await b.is_visible():
                    await b.click()
                    log(f"Clicked confirm button #{i}")
                    break
        await asyncio.sleep(2)
        log("Cover upload complete!")

asyncio.run(upload_cover())
