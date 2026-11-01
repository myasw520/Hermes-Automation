import sys, time
sys.path.append(r'C:\Users\zzx05\Hermes-Automation\services')
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        r'C:\Users\zzx05\.gemini\antigravity\scratch\bot_chrome_profile',
        channel='chrome',
        headless=True,
        viewport={'width': 1280, 'height': 850},
        args=['--no-first-run', '--no-default-browser-check']
    )
    page = browser.pages[0] if browser.pages else browser.new_page()
    page.goto('https://chatanywhere.tech/console/settings', wait_until='domcontentloaded')
    time.sleep(3)
    
    # Close any existing modal
    close_btn = page.locator('.p-dialog-close-button, button:has-text("关闭")').first
    if close_btn.is_visible():
        close_btn.click()
        time.sleep(1)
        
    bind_btn = page.locator('button:has-text("绑定 GitHub")').first
    print("Clicking 绑定 GitHub...")
    bind_btn.click()
    
    # Wait for navigation to github.com
    print("Waiting for GitHub OAuth URL...")
    page.wait_for_url(lambda u: "github.com" in u, timeout=15000)
    print("Reached GitHub OAuth page:", page.url)
    time.sleep(3)
    page.screenshot(path='C:/Users/zzx05/Hermes-Automation/reports/real_github_oauth.png')
    
    # Check if needs sign in or authorize
    auth_btn = page.locator('button:has-text("Authorize"), input[value*="Authorize"], button[name="authorize"]').first
    if auth_btn.is_visible():
        print("Clicking Authorize button on GitHub...")
        auth_btn.click()
        time.sleep(6)
        print("Redirected after Authorize to:", page.url)
        page.screenshot(path='C:/Users/zzx05/Hermes-Automation/reports/real_github_redirect.png')
    else:
        print("Authorize button not visible directly. Page title:", page.title())
        print("Body text snippet:", page.inner_text("body")[:300])
        # Maybe login required on GitHub?
        if page.locator('input[name="login"]').is_visible():
            print("GitHub login required! Autofilling credentials...")
            page.locator('input[name="login"]').fill("myasw520")
            import os
            page.locator('input[name="password"]').fill(os.environ.get("REGISTER_PASSWORD",""))  # 从 .env 读取
            page.locator('input[type="submit"]').click()
            time.sleep(5)
            page.screenshot(path='C:/Users/zzx05/Hermes-Automation/reports/github_after_login.png')
            # Look for authorize again
            auth_btn2 = page.locator('button:has-text("Authorize"), input[value*="Authorize"]').first
            if auth_btn2.is_visible():
                auth_btn2.click()
                time.sleep(6)
                
    # Final check on ChatAnywhere overview
    time.sleep(3)
    page.goto('https://chatanywhere.tech/console/overview', wait_until='domcontentloaded')
    time.sleep(3)
    page.screenshot(path='C:/Users/zzx05/Hermes-Automation/reports/overview_success_bound.png')
    
    browser.close()
    print("Done!")
