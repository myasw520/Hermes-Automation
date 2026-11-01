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
        
        # Scroll drawer down
        await page.evaluate('''() => {
            const drawers = document.querySelectorAll('.ant-drawer-body, [class*="drawer"]');
            drawers.forEach(d => d.scrollTop = d.scrollHeight);
        }''')
        await asyncio.sleep(1)
        
        texts = await page.evaluate('''() => {
            return Array.from(document.querySelectorAll('div, label, span, p'))
                .map(el => (el.innerText || '').trim())
                .filter(t => t.length > 0 && t.length < 40);
        }''')
        for t in list(set(texts)):
            if any(k in t for k in ['AI', 'ai', '智能', '生成', '声明', '辅助', '创作']):
                log("FOUND: " + t)

asyncio.run(check())
