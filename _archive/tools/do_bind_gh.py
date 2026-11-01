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
    
    bind_btn = page.locator('button:has-text("绑定 GitHub")').first
    print("Clicking 绑定 GitHub...")
    bind_btn.click()
    time.sleep(6)
    
    # Check all open pages
    print("Open pages count:", len(browser.pages))
    active_page = browser.pages[-1]
    print("Active page URL:", active_page.url)
    active_page.screenshot(path='C:/Users/zzx05/Hermes-Automation/reports/github_oauth_page.png')
    
    if "github.com" in active_page.url:
        print("Detected GitHub OAuth page! Looking for Authorize button...")
        # Check if already authorized or needs click
        auth_btn = active_page.locator('button[name="authorize"], input[value*="Authorize"], button:has-text("Authorize")').first
        if auth_btn.is_visible():
            print("Clicking Authorize chatanywhere on GitHub...")
            auth_btn.click()
            time.sleep(8)
            print("After auth URL:", active_page.url)
            active_page.screenshot(path='C:/Users/zzx05/Hermes-Automation/reports/after_auth_redirect.png')
        else:
            print("Authorize button not found or already redirected. Body:", active_page.inner_text("body")[:200])
            
    # Check back on settings page or overview page
    page.goto('https://chatanywhere.tech/console/overview', wait_until='domcontentloaded')
    time.sleep(3)
    page.screenshot(path='C:/Users/zzx05/Hermes-Automation/reports/overview_after_bind.png')
    print("Overview URL:", page.url)
    
    browser.close()
    print("Finished binding workflow!")
