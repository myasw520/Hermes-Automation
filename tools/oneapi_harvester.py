import sys, io, time, os, re, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.append(r'C:\Users\zzx05\Hermes-Automation\services')
sys.path.append(r'C:\Users\zzx05\Hermes-Automation\tools')

from playwright.sync_api import sync_playwright
from wool_radar import send_telegram_photo, send_telegram_text, TOPIC_WOOL_ID

KEYS_POOL_FILE = r"C:\Users\zzx05\Hermes-Automation\config\keys_pool.json"
REPORTS_DIR = r"C:\Users\zzx05\Hermes-Automation\reports"

def save_key_to_pool(site_url, api_key, note=""):
    """将白嫖到的 Key 存入本地 Token 蓄水池"""
    pool = []
    if os.path.exists(KEYS_POOL_FILE):
        try:
            with open(KEYS_POOL_FILE, "r", encoding="utf-8") as f:
                pool = json.load(f)
        except Exception:
            pool = []
            
    pool.append({
        "site": site_url,
        "base_url": f"{site_url.rstrip('/')}/v1",
        "api_key": api_key,
        "note": note,
        "collected_at": time.strftime("%Y-%m-%d %H:%M:%S")
    })
    
    with open(KEYS_POOL_FILE, "w", encoding="utf-8") as f:
        json.dump(pool, f, ensure_ascii=False, indent=2)
    print(f"[+] Key 已安全持久化至 Token 池: {KEYS_POOL_FILE}")

def automate_one_api_harvest(target_base_url):
    """
    针对 New API / One API 模版站点的全自动提 Key 核心逻辑
    """
    print(f"\n[*] 正在启动对目标中转站的自动化收割: {target_base_url} ...")
    profile_dir = r"C:\Users\zzx05\.gemini\antigravity\scratch\bot_chrome_profile"
    screenshot_file = os.path.join(REPORTS_DIR, "oneapi_harvest_success.png")

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            profile_dir,
            channel="chrome",
            headless=True,
            viewport={"width": 1280, "height": 800},
            args=["--no-first-run", "--no-default-browser-check"]
        )
        page = context.pages[0] if context.pages else context.new_page()

        try:
            # 1. 尝试进入令牌管理页面
            token_page_url = f"{target_base_url.rstrip('/')}/token"
            page.goto(token_page_url, timeout=25000, wait_until="domcontentloaded")
            time.sleep(3)

            # 2. 如果未登录（页面在 login，或者有登录按钮）
            github_btn = page.locator('text="使用 GitHub 继续"').or_(page.locator('button:has-text("GitHub")')).or_(page.locator('a:has-text("GitHub")')).first
            if not github_btn.is_visible() and ("login" in page.url or page.locator('text="登录"').first.is_visible()):
                if not page.locator('text="添加新的令牌"').is_visible() and not page.locator('text="添加令牌"').is_visible():
                    print("[*] 处于未登录状态，前往登录页...")
                    page.goto(f"{target_base_url.rstrip('/')}/login", timeout=20000, wait_until="domcontentloaded")
                    time.sleep(2)
                    github_btn = page.locator('text="使用 GitHub 继续"').or_(page.locator('button:has-text("GitHub")')).or_(page.locator('a:has-text("GitHub")')).first

            if github_btn.is_visible():
                print("[*] 发现 GitHub 免密登录入口，正在秒级授权...")
                github_btn.click()
                time.sleep(3)
                
                # 检查是否进入了 GitHub 官方授权确认页
                if "github.com" in page.url:
                    auth_btn = page.locator('button[name="authorize"]').or_(page.locator('button:has-text("Authorize")')).first
                    if auth_btn.is_visible():
                        print("[*] 检测到初次授权页面，正在点击 Authorize 确认授权...")
                        auth_btn.click()
                        time.sleep(4)
                
                # 授权完成后确保回到 token 页面
                page.goto(token_page_url, timeout=25000, wait_until="domcontentloaded")
                time.sleep(3)
                print("[+] GitHub 一键授权成功！已攻入后台！")

            # 3. 检查是否有每日签到按钮
            try:
                checkin_btn = page.locator('text="签到"').or_(page.locator('text="每日签到"')).first
                if checkin_btn.is_visible():
                    checkin_btn.click()
                    time.sleep(1)
                    print("[+] 发现签到入口，已顺手完成今日签到领取额度！")
            except Exception:
                pass

            # 4. 点击“添加新的令牌”
            add_token_btn = page.locator('text="添加新的令牌"').or_(page.locator('text="添加令牌"')).or_(page.locator('text="Add Token"')).first
            if add_token_btn.is_visible():
                add_token_btn.click()
                time.sleep(1)
                
                # 填写令牌名称
                name_input = page.locator('input[placeholder*="名称"]').or_(page.locator('input[name="name"]')).first
                if name_input.is_visible():
                    name_input.fill("Hermes-AutoKey")

                # 点击设为无限额度 (如有勾选框)
                try:
                    unlimited_box = page.locator('text="设为无限额度"').first
                    if unlimited_box.is_visible():
                        unlimited_box.click()
                except Exception:
                    pass

                # 点击提交创建
                submit_btn = page.locator('button:has-text("提交")').or_(page.locator('button:has-text("Submit")')).first
                if submit_btn.is_visible():
                    submit_btn.click()
                    time.sleep(2)
                    print("[+] 令牌创建成功！")

            # 5. 直接在当前活跃页面提取生成的 sk- Key (无需刷新页面导致状态丢失)
            time.sleep(2)
            page_content = page.content()
            
            # 正则匹配页面上的 sk- 秘钥
            sk_keys = re.findall(r'sk-[a-zA-Z0-9_\-]{20,64}', page_content)
            
            if sk_keys:
                extracted_key = sk_keys[0]
                print(f"🎉🎉🎉 成功攻破中转站并提权拿 Key: 【 {extracted_key} 】")
                
                # 截图存证
                page.screenshot(path=screenshot_file)
                
                # 写入本地 Token 蓄水池
                save_key_to_pool(target_base_url, extracted_key, "自动化收割成功")
                
                # 推送大捷到 Telegram
                caption = f"💎 *【成功收割一枚公益中转站 Key】*\n\n🌐 站点: `{target_base_url}`\n🔑 API Key: `{extracted_key}`\n📡 转发接口: `{target_base_url.rstrip('/')}/v1`\n\n已归档至本地 keys_pool.json，随时可用于低成本跑任务！"
                send_telegram_photo(TOPIC_WOOL_ID, caption, screenshot_file)
                print("[+] 成果已推送到 Telegram 话题 3！")
                context.close()
                return True
            else:
                print("[-] 未在页面上直接发现明文 Key，需要点击复制按钮提取。")
                page.screenshot(path=screenshot_file)
                context.close()
                return False

        except Exception as e:
            print(f"[-] 收割流水线异常: {e}")
            context.close()
            return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target = sys.argv[1]
        print(f"[*] 接收到命令行收割指令，目标站点: {target}")
        automate_one_api_harvest(target)
    else:
        print("OneAPI Harvester 模块加载完毕。用法: python oneapi_harvester.py <target_url>")
