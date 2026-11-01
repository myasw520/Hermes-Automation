import sys, io, time, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth

PROFILE_DIR = r"C:\Users\zzx05\.gemini\antigravity\scratch\bot_chrome_profile"

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(PROFILE_DIR, channel="chrome", headless=True)
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    Stealth().apply_stealth_sync(page)
    
    print("[*] 访问 FlushAPI 注册页...", flush=True)
    page.goto('https://flushapi.fun/sign-up', wait_until='networkidle')
    time.sleep(2)
    
    # 关弹窗
    btn_later = page.locator('button:has-text("Maybe later")')
    if btn_later.count() > 0 and btn_later.is_visible():
        btn_later.click()
        time.sleep(1)
        
    cb = page.locator('[role="checkbox"]')
    cb.click()
    time.sleep(1)
    
    gh_btn = page.locator('button:has-text("Continue with GitHub")')
    print("[*] 点击 Continue with GitHub 触发跳转...", flush=True)
    gh_btn.click()
    
    # 等待 GitHub 授权页出现并点击授权
    for s in range(15):
        time.sleep(1)
        print(f"[{s}s] 当前 URL: {page.url}", flush=True)
        if "github.com/login/oauth/authorize" in page.url:
            auth_btn = page.locator('button:has-text("Authorize")')
            if auth_btn.count() > 0:
                print(f"[+] 找到 GitHub 授权按钮: '{auth_btn.first.inner_text()}'，立即点击！", flush=True)
                auth_btn.first.click()
                break
                
    # 等待回到 FlushAPI
    print("[*] 等待授权回调完成...", flush=True)
    for s in range(20):
        time.sleep(1)
        print(f"[{s}s 回调等待] URL: {page.url}", flush=True)
        if "flushapi.fun" in page.url and "sign-up" not in page.url and "oauth" not in page.url:
            print("[+] 成功登录进入 FlushAPI 平台！", flush=True)
            break
            
    time.sleep(3)
    print("\n[*] 平台当前 URL:", page.url)
    print("[*] 页面标题:", page.title())
    print("[*] 页面内容前 500 字:\n", page.locator("body").inner_text()[:500], flush=True)
    page.screenshot(path=r"C:\Users\zzx05\Hermes-Automation\reports\flushapi_logged_in.png")
    
    ctx.close()
