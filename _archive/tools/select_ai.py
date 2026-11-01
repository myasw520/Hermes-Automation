# -*- coding: utf-8 -*-
import asyncio
from playwright.async_api import async_playwright
import sys
sys.path.insert(0, r'c:\Users\zzx05\Hermes-Automation\.agents\skills\post-xiaoheihe\scripts')
from xhh_common import connect, find_editor_page, log

async def check():
    async with async_playwright() as p:
        browser, ctx = await connect(p)
        page = find_editor_page(ctx)
        
        sel = page.locator("text=未选择")
        if await sel.count():
            await sel.first.click()
            await asyncio.sleep(1)
            
        opts = await page.evaluate('''() => {
            return Array.from(document.querySelectorAll('.ant-select-item-option, [role="option"], div[class*="item"]'))
                .map(el => (el.innerText || '').trim())
                .filter(t => t.length > 0 && t.length < 30);
        }''')
        log("Dropdown options: " + str(opts))
        
        ai_opt = page.locator(".ant-select-item-option:has-text('AI'), [role='option']:has-text('AI'), text=AI辅助创作, text=AI生成")
        if await ai_opt.count():
            await ai_opt.first.click()
            log("Successfully selected AI辅助创作!")
            await asyncio.sleep(1)

asyncio.run(check())
