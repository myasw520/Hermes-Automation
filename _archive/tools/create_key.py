import sys, time, re
sys.path.append(r'C:\Users\zzx05\Hermes-Automation\services')
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        r'C:\Users\zzx05\.gemini\antigravity\scratch\bot_chrome_profile',
        channel='chrome',
        headless=True,
        viewport={'width': 1280, 'height': 850},
        proxy={'server': 'http://127.0.0.1:7897'},
        args=['--no-first-run', '--no-default-browser-check']
    )
    page = browser.pages[0] if browser.pages else browser.new_page()
    page.goto('https://chatanywhere.tech/console/apikeys', wait_until='domcontentloaded')
    time.sleep(3)
    
    print('Clicking + 新增 Key...')
    page.locator('button:has-text("新增 Key")').first.click()
    time.sleep(2)
    
    page.screenshot(path='C:/Users/zzx05/Hermes-Automation/reports/create_key_modal.png')
    
    # Let's inspect the modal
    modal = page.locator('div[role="dialog"], .p-dialog').last
    print('Modal visible:', modal.is_visible())
    if modal.is_visible():
        print('Modal text:', repr(modal.inner_text()[:300]))
        # Fill name if there is an input
        inps = modal.locator('input').all()
        print(f'Inputs in modal: {len(inps)}')
        if inps:
            inps[0].fill('Wool-Bot-Hermes')
            time.sleep(0.5)
        # Look for confirm / save button
        save_btn = modal.locator('button:has-text("确定"), button:has-text("创建"), button:has-text("保存")').first
        if save_btn.is_visible():
            print('Clicking save button:', save_btn.inner_text())
            save_btn.click()
            time.sleep(3)
            
    page.screenshot(path='C:/Users/zzx05/Hermes-Automation/reports/after_create_key.png')
    content = page.content()
    keys = re.findall(r'sk-[a-zA-Z0-9]{32,64}', content)
    print('Keys after creation:', keys)
    browser.close()
