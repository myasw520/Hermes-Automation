import sys, io, time, os, re, json, requests
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.append(r'C:\Users\zzx05\Hermes-Automation\services')
sys.path.append(r'C:\Users\zzx05\Hermes-Automation\tools')

from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth
from wool_radar import send_telegram_photo, send_telegram_text, TOPIC_WOOL_ID

KEYS_POOL_FILE = r"C:\Users\zzx05\Hermes-Automation\config\keys_pool.json"
REPORTS_DIR = r"C:\Users\zzx05\Hermes-Automation\reports"
PROFILE_DIR = r"C:\Users\zzx05\.gemini\antigravity\scratch\bot_chrome_profile"

USERNAME = f"hermes{int(time.time()) % 1000000}"
PASSWORD = "Hermes2026Pass#!"

def save_key(site_url, api_key, site_name="FlushAPI", note=""):
    pool = []
    if os.path.exists(KEYS_POOL_FILE):
        try:
            with open(KEYS_POOL_FILE, "r", encoding="utf-8") as f:
                pool = json.load(f)
        except Exception:
            pool = []
            
    for item in pool:
        if item.get("api_key") == api_key:
            print(f"[!] Key 已在池中: {api_key[:10]}...")
            return
            
    pool.append({
        "site": site_url,
        "name": site_name,
        "base_url": f"{site_url.rstrip('/')}/v1",
        "api_key": api_key,
        "note": note,
        "collected_at": time.strftime("%Y-%m-%d %H:%M:%S")
    })
    
    with open(KEYS_POOL_FILE, "w", encoding="utf-8") as f:
        json.dump(pool, f, ensure_ascii=False, indent=2)
    print(f"[+] Key 成功保存至: {KEYS_POOL_FILE}")

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(
        PROFILE_DIR,
        channel="chrome",
        headless=True,
        args=["--disable-blink-features=AutomationControlled"]
    )
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    Stealth().apply_stealth_sync(page)
    
    screenshot_file = os.path.join(REPORTS_DIR, "flushapi_harvest_success.png")
    extracted_keys = []
    
    def on_res(r):
        if ('token' in r.url.lower() or 'key' in r.url.lower()) and r.status == 200:
            try:
                text = r.text()
                keys = re.findall(r'sk-[a-zA-Z0-9_\-]{20,64}', text)
                for k in keys:
                    if k not in extracted_keys:
                        extracted_keys.append(k)
            except Exception: pass
    page.on('response', on_res)
    
    print(f"[*] 访问 FlushAPI 注册: 用户名 {USERNAME} ...")
    page.goto("https://flushapi.fun/sign-up?aff=WBF3", wait_until="networkidle")
    time.sleep(1)
    
    # 填充用户名和密码
    page.locator('input[name="username"]').fill(USERNAME)
    page.locator('input[name="password"]').fill(PASSWORD)
    page.locator('input[name="confirmPassword"]').fill(PASSWORD)
    
    # 勾选条款 (直接通过 JS 勾选避免视口遮挡)
    page.evaluate('() => { const el = document.getElementById("legal-consent"); if (el) { el.checked = true; el.dispatchEvent(new Event("change", { bubbles: true })); } }')
        
    print("[*] 正在点击【Create account】...")
    create_btn = page.locator('button:has-text("Create account")').first
    create_btn.click()
    time.sleep(4)
    
    print(f"[+] 注册后页面 URL: {page.url} | 标题: {page.title()}")
    print("    页面正文前 300 字:", page.locator("body").inner_text()[:300].replace("\n", " "))
    
    # 前往令牌 / API Key 管理页
    token_urls = ["https://flushapi.fun/tokens", "https://flushapi.fun/token", "https://flushapi.fun/console/token", "https://flushapi.fun/dashboard"]
    for tu in token_urls:
        try:
            page.goto(tu, timeout=10000, wait_until="domcontentloaded")
            time.sleep(2)
            if "login" not in page.url and "sign-up" not in page.url:
                print(f"[+] 成功进入管理页: {page.url}")
                break
        except Exception: pass
        
    # 检查新建令牌按钮
    add_btn = page.locator('button:has-text("Create"), button:has-text("Add"), button:has-text("添加")').first
    if add_btn.is_visible():
        print("[+] 发现添加令牌按钮，正在点击...")
        add_btn.click()
        time.sleep(1)
        name_in = page.locator('input[placeholder*="name"], input[placeholder*="名称"]').first
        if name_in.is_visible():
            name_in.fill("Hermes-Key")
        sub = page.locator('button:has-text("Submit"), button:has-text("Create"), button:has-text("提交")').last
        if sub.is_visible():
            sub.click()
            time.sleep(2)
            
    # 复制按钮
    copy_btns = page.locator('button:has-text("Copy"), button:has-text("复制")').all()
    for cb in copy_btns:
        try: cb.click(); time.sleep(0.5)
        except Exception: pass
        
    time.sleep(2)
    page_text = page.content()
    body_keys = re.findall(r'sk-[a-zA-Z0-9_\-]{20,64}', page_text)
    all_keys = list(set(extracted_keys + body_keys))
    
    page.screenshot(path=screenshot_file)
    print(f"[+] 捕获到的 Keys: {all_keys}")
    
    if all_keys:
        key = all_keys[0]
        print(f"\n🎉🎉🎉 成功攻破 FlushAPI 并获取 Key: 【 {key} 】 🎉🎉🎉\n")
        save_key("https://flushapi.fun", key, "FlushAPI", "用户名免邮箱秒注册")
        
        caption = (
            f"💎 *【全自动收割 FlushAPI Key 大捷】*\n\n"
            f"🏷 站点: *FlushAPI*\n"
            f"🌐 域名: `https://flushapi.fun`\n"
            f"🔑 API Key: `{key}`\n"
            f"📡 接口: `https://flushapi.fun/v1`\n"
            f"👤 账号: `{USERNAME}`\n\n"
            f"已自动存入 keys_pool.json，随时可供 Hermes 调用！"
        )
        send_telegram_photo(TOPIC_WOOL_ID, caption, screenshot_file)
        print("[+] 成果已推送到 Telegram 话题 3！")
    else:
        print("[-] 未在页面找到明文 Key")
        
    ctx.close()
