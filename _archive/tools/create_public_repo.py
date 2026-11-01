import sys, io, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.sync_api import sync_playwright

PROFILE_DIR = r"C:\Users\zzx05\.gemini\antigravity\scratch\bot_chrome_profile"

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(PROFILE_DIR, channel="chrome", headless=True)
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    
    print("[*] 访问 GitHub 新建仓库页面: https://github.com/new", flush=True)
    page.goto("https://github.com/new", wait_until="domcontentloaded")
    time.sleep(3)
    
    # 填充仓库名
    inp = page.locator('#repository-name-input')
    inp.fill("ai-welfare-hub")
    time.sleep(2)
    
    create_btn = page.locator('button:has-text("Create repository")').first
    print("[*] 准备点击 Create repository, disabled =", create_btn.is_disabled(), flush=True)
    create_btn.click()
    
    for s in range(10):
        time.sleep(1)
        print(f"[{s}s] 当前 URL: {page.url}", flush=True)
        if "myasw520" in page.url and "new" not in page.url:
            print("[+] 成功创建公开仓库！URL:", page.url, flush=True)
            break
            
    ctx.close()
