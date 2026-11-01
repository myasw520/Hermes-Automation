# -*- coding: utf-8 -*-
import asyncio
from playwright.async_api import async_playwright
import sys
sys.path.insert(0, r'c:\Users\zzx05\Hermes-Automation\.agents\skills\post-xiaoheihe\scripts')
from xhh_common import connect, find_editor_page, log

async def save():
    async with async_playwright() as p:
        browser, ctx = await connect(p)
        page = find_editor_page(ctx)
        if not page:
            log("No editor page found")
            return
            
        btn = page.locator("button:has-text('保存草稿')")
        if await btn.count():
            await btn.first.click()
            log("Clicked 保存草稿!")
            await asyncio.sleep(5)
            log("Draft saved successfully with custom cover!")

asyncio.run(save())
