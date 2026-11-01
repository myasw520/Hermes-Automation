import sys, io, time, os, re, json, email, imaplib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.append(r'C:\Users\zzx05\Hermes-Automation\services')
sys.path.append(r'C:\Users\zzx05\Hermes-Automation\tools')

from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth
from wool_radar import send_telegram_photo, send_telegram_text, TOPIC_WOOL_ID

KEYS_POOL_FILE = r"C:\Users\zzx05\Hermes-Automation\config\keys_pool.json"
REPORTS_DIR = r"C:\Users\zzx05\Hermes-Automation\reports"
PROFILE_DIR = r"C:\Users\zzx05\.gemini\antigravity\scratch\bot_chrome_profile"

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "services"))
from config_lib import QQ_USER, QQ_PASS, REGISTER_PASSWORD as TARGET_PWD
QQ_HOST = "imap.qq.com"

TARGET_EMAIL = "3159772887@qq.com"
# TARGET_PWD 从 config_lib (.env REGISTER_PASSWORD) 引入
TARGET_USER = "zzx3159772"

def get_email_code(since_timestamp, max_wait=45):
    """通过 QQ IMAP 自动监听并抓取最新收到的 6 位验证码"""
    print(f"[*] 正在监听 QQ 邮箱验证码 (时间基准: {time.strftime('%H:%M:%S', time.localtime(since_timestamp))})...")
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        mail = None
        try:
            mail = imaplib.IMAP4_SSL(QQ_HOST, 993)
            mail.login(QQ_USER, QQ_PASS)
            mail.select("INBOX")
            
            status, data = mail.search(None, "ALL")
            if status == "OK" and data[0]:
                ids = data[0].split()
                for eid in reversed(ids[-5:]):
                    _, msg_data = mail.fetch(eid, "(RFC822)")
                    if not msg_data or not msg_data[0]:
                        continue
                    msg = email.message_from_bytes(msg_data[0][1])
                    
                    # 检查时间戳
                    date_tuple = email.utils.parsedate_tz(msg.get("Date"))
                    if date_tuple:
                        email_ts = email.utils.mktime_tz(date_tuple)
                        if email_ts < since_timestamp - 10:
                            continue
                            
                    # 解析正文
                    body_text = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() in ["text/plain", "text/html"]:
                                try:
                                    payload = part.get_payload(decode=True)
                                    if payload:
                                        body_text += payload.decode('utf-8', errors='ignore')
                                except Exception:
                                    pass
                    else:
                        payload = msg.get_payload(decode=True)
                        if payload:
                            body_text = payload.decode('utf-8', errors='ignore')
                            
                    # 剔除 CSS 颜色代码等干扰项
                    cleaned = re.sub(r'#[0-9a-fA-F]{6}', '', body_text)
                    cleaned = re.sub(r'#[0-9a-fA-F]{3}', '', cleaned)
                    
                    codes = re.findall(r'\b\d{6}\b', cleaned)
                    if codes:
                        code = codes[0]
                        print(f"🎉🎉 成功拦截到验证码: 【 {code} 】 (来自: {msg.get('From')})")
                        mail.logout()
                        return code
            mail.logout()
        except Exception as e:
            if mail:
                try: mail.logout()
                except Exception: pass
                
        time.sleep(2)
        print(f"    [等待收件...] 耗时 {int(time.time() - start_time)}s")
        
    print("[-] 接收验证码超时")
    return None

def save_key(site_url, api_key, site_name="DoCode", balance="300 刀"):
    pool = []
    if os.path.exists(KEYS_POOL_FILE):
        try:
            with open(KEYS_POOL_FILE, "r", encoding="utf-8") as f:
                pool = json.load(f)
        except Exception:
            pool = []
            
    pool.append({
        "site": site_url,
        "name": site_name,
        "base_url": f"{site_url.rstrip('/')}/v1",
        "api_key": api_key,
        "note": f"首日赠额 {balance}",
        "collected_at": time.strftime("%Y-%m-%d %H:%M:%S")
    })
    
    with open(KEYS_POOL_FILE, "w", encoding="utf-8") as f:
        json.dump(pool, f, ensure_ascii=False, indent=2)
    print(f"[+] Key 成功保存至: {KEYS_POOL_FILE}")

def run_harvest():
    print("=" * 60)
    print(f"🚀 开始全自动攻破 DoCode (300 刀) 目标邮箱: {TARGET_EMAIL}")
    print("=" * 60)
    
    screenshot_file = os.path.join(REPORTS_DIR, "docode_harvest_success.png")
    extracted_keys = []
    
    def on_response(resp):
        try:
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
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        Stealth().apply_stealth_sync(page)
        page.on("response", on_response)
        
        # 1. 访问注册页
        print("[1] 导航至注册页面...")
        page.goto("https://docode.cc/register?aff=zMRe", wait_until="networkidle")
        time.sleep(2)
        
        # 2. 装填表单
        print(f"[2] 自动装填用户名: {TARGET_USER}, 邮箱: {TARGET_EMAIL} ...")
        page.locator('input[name="username"]').fill(TARGET_USER)
        page.locator('input[name="password"]').fill(TARGET_PWD)
        page.locator('input[name="password2"]').fill(TARGET_PWD)
        page.locator('input[name="email"]').fill(TARGET_EMAIL)
        page.locator('input[name="aff_code"]').fill("zMRe")
        
        # 3. 点击获取验证码
        since_ts = time.time()
        print("[3] 正在点击【获取验证码】按钮...")
        send_code_btn = page.locator('button:has-text("获取验证码")').first
        send_code_btn.click()
        time.sleep(2)
        
        # 检查页面是否有报错提示
        toasts = [t.inner_text() for t in page.locator('.semi-toast, .ant-message, [role="alert"]').all()]
        if toasts:
            print("    页面提示:", toasts)
            
        # 4. 自动监听 QQ 邮箱提取验证码
        code = get_email_code(since_ts, max_wait=45)
        if not code:
            print("[-] 未能收到验证码邮件，保存现场截图")
            page.screenshot(path=screenshot_file)
            ctx.close()
            return False
            
        # 5. 填入验证码并点击注册
        print(f"[4] 将验证码 【{code}】 填入页面并提交注册...")
        page.locator('input[name="verification_code"]').fill(code)
        time.sleep(1)
        
        submit_reg_btn = page.locator('button:has-text("注册")').last
        submit_reg_btn.click()
        time.sleep(4)
        
        # 检查是否注册成功并登录
        print(f"[5] 当前页面 URL: {page.url} | 标题: {page.title()}")
        toasts = [t.inner_text() for t in page.locator('.semi-toast, .ant-message, [role="alert"]').all()]
        if toasts:
            print("    注册结果提示:", toasts)
            
        # 6. 如果在登录页，自动登录
        if "login" in page.url:
            print("[*] 正在执行自动登录...")
            page.locator('input[name="username"]').fill(TARGET_USER)
            page.locator('input[name="password"]').fill(TARGET_PWD)
            page.locator('button:has-text("登录")').last.click()
            time.sleep(3)
            
        # 7. 进入令牌页面创建并提取 Key
        print("[6] 正在前往 /token 页面提取 Key...")
        page.goto("https://docode.cc/token", wait_until="networkidle")
        time.sleep(2)
        
        # 检查是否有每日签到
        try:
            checkin = page.locator('text="签到"').or_(page.locator('text="每日签到"')).first
            if checkin.is_visible():
                checkin.click()
                print("[+] 已顺手触发每日签到！")
                time.sleep(1)
        except Exception:
            pass
            
        # 点击“添加新的令牌”
        add_btn = page.locator('button:has-text("添加新的令牌")').or_(page.locator('button:has-text("添加令牌")')).first
        if add_btn.is_visible():
            print("[+] 点击添加新的令牌...")
            add_btn.click()
            time.sleep(1)
            name_input = page.locator('input[placeholder*="名称"]').or_(page.locator('input[name="name"]')).first
            if name_input.is_visible():
                name_input.fill("Hermes-DoCode")
            unlimited = page.locator('text="设为无限额度"').first
            if unlimited.is_visible():
                unlimited.click()
            submit_btn = page.locator('button:has-text("提交")').or_(page.locator('button:has-text("Submit")')).first
            if submit_btn.is_visible():
                submit_btn.click()
                time.sleep(2)
                print("[+] 令牌提交成功！")
                
        time.sleep(2)
        page_text = page.content()
        body_keys = re.findall(r'sk-[a-zA-Z0-9_\-]{20,64}', page_text)
        all_keys = list(set(extracted_keys + body_keys))
        
        page.screenshot(path=screenshot_file)
        
        if all_keys:
            key = all_keys[0]
            print(f"\n🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉")
            print(f"🎉 成功拿下 DoCode 300 刀 Key: 【 {key} 】")
            print(f"🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉\n")
            save_key("https://docode.cc", key, "DoCode", "300 站内刀")
            
            caption = (
                f"💎 *【全自动收割 DoCode 300 刀 Key 成功】*\n\n"
                f"🏷 站点: *DoCode*\n"
                f"🌐 域名: `https://docode.cc`\n"
                f"🔑 API Key: `{key}`\n"
                f"📡 转发接口: `https://docode.cc/v1`\n"
                f"💰 额度: 300 站内刀 (已绑定专属邀请码)\n\n"
                f"已自动存入 keys_pool.json，随时可供 Hermes 低成本调用！"
            )
            send_telegram_photo(TOPIC_WOOL_ID, caption, screenshot_file)
            print("[+] 喜报与截图已推送至 Telegram 话题 3！")
            ctx.close()
            return True
        else:
            print("[-] 未在页面找到明文 Key，查看截图存证")
            ctx.close()
            return False

if __name__ == "__main__":
    run_harvest()
