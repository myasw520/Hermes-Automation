import sys, io, time, os, re
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.append(r'C:\Users\zzx05\Hermes-Automation\services')
sys.path.append(r'C:\Users\zzx05\Hermes-Automation\tools')

from playwright.sync_api import sync_playwright
from wool_radar import send_telegram_photo, TOPIC_WOOL_ID
from harvest_github_apis import save_to_pool

profile_dir = r"C:\Users\zzx05\.gemini\antigravity\scratch\bot_chrome_profile"
proxy_config = {"server": "http://127.0.0.1:7897"}
screenshot_file = r"C:\Users\zzx05\Hermes-Automation\reports\chatanywhere_claimed.png"
url = "https://api.chatanywhere.org/#/free"

print(f"[*] 正在启动带 GitHub 登录态的 Chrome 攻入: {url} ...")
with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        profile_dir,
        channel="chrome",
        headless=True,
        viewport={"width": 1280, "height": 850},
        proxy=proxy_config,
        args=["--no-first-run", "--no-default-browser-check"]
    )
    page = context.pages[0] if context.pages else context.new_page()
    page.goto(url, timeout=30000, wait_until="domcontentloaded")
    time.sleep(3)
    
    # 查找“免费开始”或“登录获取”按钮
    print("[1] 正在寻找【免费开始】/【登录获取】入口...")
    btn = page.locator('text="免费开始"').or_(page.locator('text="登录获取 API Key"')).first
    if btn.is_visible():
        btn.click()
        time.sleep(3)
        print("[2] 已点击进入，正在观察是否弹出 GitHub 授权...")
        
        # 如果跳转到 GitHub 授权页，自动点击绿色的 Authorize 按钮
        if "github.com/login/oauth/authorize" in page.url or "github.com" in page.url:
            print("[*] 正在通过 GitHub 自动授权...")
            auth_btn = page.locator('button[name="authorize"]').or_(page.locator('button:has-text("Authorize")')).first
            if auth_btn.is_visible():
                auth_btn.click()
                time.sleep(5)
                print("[+] 已点击 GitHub 授权！")
        
        # 等待重定向回到用户后台
        time.sleep(4)
        print(f"当前跳转后页面 URL: {page.url}")
        
        # 截图存证
        page.screenshot(path=screenshot_file)
        content = page.content()
        body_text = page.inner_text("body")
        
        # 提取生成的 sk- Key
        keys = re.findall(r'sk-[a-zA-Z0-9]{32,64}', content)
        
        if keys:
            real_key = keys[0]
            print(f"🎉🎉🎉 真实公网白嫖大成功！拿到的真实免费 Key: 【 {real_key} 】")
            save_to_pool("https://api.chatanywhere.tech/v1", real_key, 120.0, "ChatAnywhere 免费开放计划领取")
            
            caption = (
                f"💎 *【公网真实白嫖大捷！免费 API Key 已领到】*\n\n"
                f"🌐 *平台*: `ChatAnywhere 免费开放计划`\n"
                f"🔑 *API Key*: `{real_key}`\n"
                f"📡 *转发地址*: `https://api.chatanywhere.tech/v1`\n"
                f"🎁 *覆盖模型*: GPT-4o / Claude / DeepSeek / Gemini\n\n"
                f"已安全入库 keys_pool.json，随时可用于跑任务！现场截图见下方！"
            )
            send_telegram_photo(TOPIC_WOOL_ID, caption, screenshot_file)
            print("[+] 战报已秒推至 Telegram 群话题 3！")
        else:
            print("[-] 未在页面找到明文 Key，可能在'令牌'或'复制'按钮下。页面摘要:")
            print(body_text[:400].replace('\n', ' '))
            
            # 即使没正则扣出，也把现场截图发给用户
            caption = f"🎯 *【ChatAnywhere 授权现场实拍】*\n\n当前已攻入后台，现场状态见截图！\n🔗 页面: {page.url}"
            send_telegram_photo(TOPIC_WOOL_ID, caption, screenshot_file)
    else:
        print("未定位到开始按钮")
        
    context.close()
