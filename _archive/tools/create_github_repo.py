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
    
    print("[*] 页面标题:", page.title())
    
    # 填入仓库名
    repo_input = page.locator('input[data-testid="repository-name-input"], input[aria-label="Repository"]').first
    repo_input.fill("my-awesome-code")
    time.sleep(1)
    
    # 勾选 Add a README file
    readme_cb = page.locator('input[id*="readme"], input[type="checkbox"]:has-text("README")').first
    if readme_cb.count() > 0:
        readme_cb.check(force=True)
        time.sleep(1)
        
    # 点击 Create repository 按钮
    create_btn = page.locator('button:has-text("Create repository")').first
    print("[*] 准备点击 Create repository, disabled =", create_btn.is_disabled())
    create_btn.click()
    
    for s in range(10):
        time.sleep(1)
        print(f"[{s}s] 当前 URL: {page.url}")
        if "myasw520/my-awesome-code" in page.url:
            print("[+] 成功创建公开仓库: https://github.com/myasw520/my-awesome-code !")
            break
            
    page.screenshot(path=r"C:\Users\zzx05\Hermes-Automation\reports\github_repo_created.png")
    ctx.close()
