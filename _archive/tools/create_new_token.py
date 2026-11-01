import sys, io, time, json, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth

PROFILE_DIR = r"C:\Users\zzx05\.gemini\antigravity\scratch\bot_chrome_profile"

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(PROFILE_DIR, channel="chrome", headless=True)
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    Stealth().apply_stealth_sync(page)
    
    new_keys = []
    def on_res(r):
        if 'token' in r.url and r.status == 200:
            try:
                data = r.json()
                print("TOKEN RESP:", json.dumps(data, ensure_ascii=False)[:300])
                k = data.get('data', {}).get('key')
                if k and k.startswith('sk-'):
                    new_keys.append(k)
            except Exception: pass
    page.on('response', on_res)
    
    page.goto("https://docode.cc/console/token", wait_until="networkidle")
    time.sleep(2)
    
    # 查找主界面的加号按钮（通常是带有 plus 或 primary 的按钮）
    all_btns = page.locator('button').all()
    # 尝试找到带有 icon 的 primary button [6]
    plus_btn = page.locator('.semi-button-primary.semi-button-with-icon-only').first
    if plus_btn.is_visible():
        print("[+] 发现加号新建按钮，正在点击...")
        plus_btn.click()
        time.sleep(1.5)
        
        # 弹窗填写
        name_in = page.locator('input[placeholder*="名称"]').or_(page.locator('input[name="name"]')).first
        if name_in.is_visible():
            name_in.fill("Hermes-2026")
        
        unlimited = page.locator('text="设为无限额度"').first
        if unlimited.is_visible():
            unlimited.click()
            
        submit = page.locator('button:has-text("提交")').or_(page.locator('button:has-text("确定")')).or_(page.locator('button:has-text("创建")')).last
        if submit.is_visible():
            print("[+] 点击提交新建令牌...")
            submit.click()
            time.sleep(3)
            
    # 查看弹窗提示
    toasts = [t.inner_text() for t in page.locator('.semi-toast, .ant-message, [role="alert"]').all()]
    print("页面提示:", toasts)
    
    if new_keys:
        print(f"\n🎉🎉🎉 新创建的 Key: {new_keys[0]} 🎉🎉🎉\n")
    else:
        print("[-] 未在 POST 返回中拦截到新 Key，检查页面内容...")
        print(page.locator('body').inner_text()[:400].replace('\n', ' '))
        
    ctx.close()
