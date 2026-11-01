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

TARGET_URL = "https://agentrouter.org/register?aff=szt3"

def save_key(site_url, api_key, site_name="AgentRouter", balance="$175"):
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
        "note": f"AgentRouter 满血攻破 (额度 {balance})",
        "collected_at": time.strftime("%Y-%m-%d %H:%M:%S")
    })
    
    with open(KEYS_POOL_FILE, "w", encoding="utf-8") as f:
        json.dump(pool, f, ensure_ascii=False, indent=2)
    print(f"[+] Key 成功保存至: {KEYS_POOL_FILE}")

def run():
    print("=" * 60)
    print("🚀 启动 AgentRouter ($175 刀) 全自动攻坚收割流水线...")
    print("=" * 60)
    
    screenshot_file = os.path.join(REPORTS_DIR, "agentrouter_harvest_success.png")
    extracted_keys = []
    user_info = {}
    
    def on_response(resp):
        nonlocal user_info
        try:
            if "self" in resp.url and resp.status == 200:
                user_info = resp.json().get("data", {})
            if "token" in resp.url.lower() and resp.status == 200:
                text = resp.text()
                keys = re.findall(r'sk-[a-zA-Z0-9_\-]{20,64}', text)
                for k in keys:
                    if k not in extracted_keys:
                        extracted_keys.append(k)
        except Exception:
            pass

    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            PROFILE_DIR,
            channel="chrome",
            headless=True,
            permissions=["clipboard-read", "clipboard-write"],
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        Stealth().apply_stealth_sync(page)
        page.on("response", on_response)
        
        # 1. 访问邀请注册页
        print(f"[1] 访问注册入口: {TARGET_URL} ...")
        page.goto(TARGET_URL, wait_until="networkidle")
        time.sleep(2)
        
        # 2. 点击 GitHub 授权登录
        gh_btn = page.locator('button:has-text("GitHub")').first
        print("[2] 点击【使用 GitHub 继续】...")
        
        popup = None
        try:
            with page.expect_popup(timeout=8000) as popup_info:
                gh_btn.click()
            popup = popup_info.value
        except Exception as e:
            print("[-] 未直接捕获弹窗:", e)
            
        if popup:
            print(f"[+] 捕获到 OAuth 弹窗: {popup.url}")
            popup.wait_for_load_state("domcontentloaded")
            time.sleep(2)
            
            auth_btn = popup.locator('button[name="authorize"], button:has-text("Authorize")').first
            if auth_btn.is_visible():
                print("[*] 发现 Authorize 按钮，正在确认授权...")
                auth_btn.click()
                time.sleep(4)
                
            print(f"[*] 授权后弹窗 URL: {popup.url if not popup.is_closed() else 'CLOSED'}")
            
        time.sleep(4)
        
        # 3. 检查主页面是否进入控制台
        print(f"[3] 检查主页面会话状态: {page.url} | 标题: {page.title()}")
        if "console" not in page.url and "token" not in page.url:
            print("[*] 前往控制台页面...")
            page.goto("https://agentrouter.org/console", wait_until="networkidle")
            time.sleep(3)
            
        print(f"[+] 当前所在页面: {page.url} | 标题: {page.title()}")
        toasts = [t.inner_text() for t in page.locator('.semi-toast, .ant-message, [role="alert"]').all()]
        if toasts:
            print("    页面提示:", toasts)
            
        # 4. 触发每日签到领额外赠额
        try:
            checkin = page.locator('text="签到"').or_(page.locator('text="每日签到"')).first
            if checkin.is_visible():
                checkin.click()
                print("[+] 已成功触发每日签到！")
                time.sleep(1)
        except Exception:
            pass
            
        # 5. 前往令牌页面
        token_urls = ["https://agentrouter.org/console/token", "https://agentrouter.org/token"]
        for tu in token_urls:
            page.goto(tu, wait_until="networkidle")
            time.sleep(2)
            if "token" in page.url:
                break
                
        print(f"[4] 进入令牌管理页: {page.url}")
        
        # 检查是否需要新建令牌
        add_btn = page.locator('button:has-text("添加令牌"), button:has-text("添加新的令牌"), .semi-button-primary.semi-button-with-icon-only').first
        if add_btn.is_visible():
            print("[+] 点击添加新令牌...")
            add_btn.click()
            time.sleep(1)
            name_in = page.locator('input[placeholder*="名称"], input[name="name"]').first
            if name_in.is_visible():
                name_in.fill("Hermes-AgentKey")
            unlimited = page.locator('text="设为无限额度"').first
            if unlimited.is_visible():
                unlimited.click()
            sub = page.locator('button:has-text("提交"), button:has-text("Submit")').first
            if sub.is_visible():
                sub.click()
                time.sleep(2)
                print("[+] 提交新建令牌成功！")
                
        # 点击所有复制按钮
        copy_btns = page.locator('button:has-text("复制"), tbody tr button').all()
        for cb in copy_btns:
            try:
                cb.click()
                time.sleep(0.3)
                clip = page.evaluate('navigator.clipboard.readText()')
                if clip and clip.startswith('sk-'):
                    extracted_keys.append(clip)
            except Exception:
                pass
                
        time.sleep(2)
        page_text = page.content()
        body_keys = re.findall(r'sk-[a-zA-Z0-9_\-]{20,64}', page_text)
        all_keys = list(set(extracted_keys + body_keys))
        
        page.screenshot(path=screenshot_file)
        
        quota_display = "$175 (新用户活动)"
        if user_info:
            q = user_info.get("quota", 0)
            if q:
                quota_display = f"${q / 500000:.2f}"
        print(f"[+] 账户可用额度: {quota_display}")
        print(f"[+] 捕获到的 Keys: {all_keys}")
        
        if all_keys:
            key = all_keys[0]
            print(f"\n🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉")
            print(f"🎉 成功拿下 AgentRouter Key: 【 {key} 】")
            print(f"🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉\n")
            save_key("https://agentrouter.org", key, "AgentRouter", quota_display)
            
            # 实测公网模型调用
            model_info = "验活中..."
            try:
                r = requests.post(
                    "https://agentrouter.org/v1/chat/completions",
                    headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                    json={"model": "gpt-4o-mini", "messages": [{"role": "user", "content": "hi"}], "max_tokens": 5},
                    proxies={"http": "http://127.0.0.1:7897", "https": "http://127.0.0.1:7897"},
                    timeout=12
                )
                if r.status_code == 200:
                    model_info = f"✅ HTTP 200 活态可用！响应: {r.json()['choices'][0]['message']['content'].strip()}"
                else:
                    model_info = f"HTTP {r.status_code}: {r.text[:80]}"
            except Exception as e:
                model_info = f"测试异常: {e}"
                
            caption = (
                f"💎 *【全自动收割 AgentRouter $175 刀 Key 大捷】*\n\n"
                f"🏷 站点: *AgentRouter*\n"
                f"🌐 域名: `https://agentrouter.org/v1`\n"
                f"🔑 API Key: `{key}`\n"
                f"💰 账户可用额度: *{quota_display}*\n"
                f"🩺 实测调用: {model_info}\n\n"
                f"已自动持久化存入 keys_pool.json，Hermes 可随时调用！"
            )
            send_telegram_photo(TOPIC_WOOL_ID, caption, screenshot_file)
            print("[+] 喜报与截图已推送到 Telegram 话题 3！")
            ctx.close()
            return True
        else:
            print("[-] 未在页面提取到明文 Key，查看页面可见内容:")
            print(page.locator("body").inner_text()[:400].replace("\n", " "))
            ctx.close()
            return False

if __name__ == "__main__":
    run()
