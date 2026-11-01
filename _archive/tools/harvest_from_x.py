import sys, io, time, os, re, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.append(r'C:\Users\zzx05\Hermes-Automation\services')
sys.path.append(r'C:\Users\zzx05\Hermes-Automation\tools')

from playwright.sync_api import sync_playwright
from wool_radar import call_hermes_diagnosis, send_telegram_photo, send_telegram_text, TOPIC_WOOL_ID

profile_dir = r"C:\Users\zzx05\.gemini\antigravity\scratch\bot_chrome_profile"
proxy_config = {"server": "http://127.0.0.1:7897"}
report_dir = r"C:\Users\zzx05\Hermes-Automation\reports"

def harvest_step():
    print("==================================================")
    print("🚀 启动 X (Twitter) 中转站实战猎捕流水线...")
    print("==================================================")

    found_urls = []
    
    with sync_playwright() as p:
        print("[1] 正在启动已登录 X 账号的专用 Chrome 探路兵...")
        context = p.chromium.launch_persistent_context(
            profile_dir,
            channel="chrome",
            headless=True,
            viewport={"width": 1280, "height": 850},
            proxy=proxy_config,
            args=["--no-first-run", "--no-default-browser-check"]
        )
        page = context.pages[0] if context.pages else context.new_page()

        # 1. 访问 X 搜索推特上的最新中转站发文
        print("[2] 正在进入 X 搜寻带链接的中转站推文...")
        for attempt in range(3):
            try:
                page.goto("https://x.com/home", timeout=30000, wait_until="domcontentloaded")
                break
            except Exception as e:
                print(f"  [-] 第 {attempt+1} 次网络抖动，正在重新握手 X.com ...")
                time.sleep(2)
        
        time.sleep(3)
        
        search_input = page.wait_for_selector('input[data-testid="SearchBox_Search_Input"]', timeout=15000)
        if search_input:
            search_input.fill("中转API OR 公益API")
            search_input.press("Enter")
            time.sleep(6)
            
            # 点击“最新 (Latest)”标签页，找刚出炉的
            try:
                latest_tab = page.locator('text="最新"').or_(page.locator('text="Latest"')).first
                if latest_tab.is_visible():
                    latest_tab.click()
                    time.sleep(4)
            except Exception:
                pass
            
            # 抓取页面上的外部 URL
            content_html = page.content()
            raw_links = re.findall(r'href="(https?://t\.co/[^"]+)"', content_html)
            print(f"[3] 在推特现场捕获到 {len(raw_links)} 个推文外链！")
            
            # 还原 t.co 短链
            for short_link in raw_links[:8]:
                try:
                    p2 = context.new_page()
                    resp = p2.goto(short_link, timeout=12000)
                    real_url = p2.url
                    p2.close()
                    if "x.com" not in real_url and "twitter.com" not in real_url:
                        found_urls.append(real_url)
                        print(f"  👉 成功解析推文中转站直达地址: {real_url}")
                except Exception:
                    pass

        # 2. 如果推特上捕获到了中转站，实地攻入第一个站点！
        if found_urls:
            target_site = found_urls[0]
            print(f"\n[4] 锁定战术目标，正在实地攻入: {target_site} ...")
            try:
                page.goto(target_site, timeout=25000, wait_until="domcontentloaded")
                time.sleep(3)
                
                # 现场截图
                shot_path = os.path.join(report_dir, "x_target_site.png")
                page.screenshot(path=shot_path)
                print(f"[5] 目标现场实况已拍照: {shot_path}")
                
                body_text = page.inner_text("body")[:1500]
                
                # 检测是否为典型的 New API / One API 平台
                is_new_api = False
                if any(k in body_text for k in ["New API", "One API", "添加令牌", "系统状况", "兑换"]):
                    is_new_api = True
                    print("🔥 识别成功！该站点为标准的 New API / One API 架构！")

                # 3. 让 Hermes 给出战报
                diagnosis = call_hermes_diagnosis("X 猎捕中转站实战", f"目标网址: {target_site}", body_text)
                
                caption = f"🎯 *【X 实战捕获中转站战报】*\n\n{diagnosis}\n\n🔗 目标: {target_site}\n🛠️ 模版类型: {'New API / One API (支持全自动提Key)' if is_new_api else '通用中转'}"
                send_telegram_photo(TOPIC_WOOL_ID, caption, shot_path)
                print("[6] 🚀 战报与实况截图已秒推 Telegram 羊毛情报话题！")
                
            except Exception as e:
                print(f"[-] 攻入目标站点超时或失败: {e}")
        else:
            print("[-] 本轮推特流中暂未发现有效外链中转站，可能刚刚没有博主发推，稍后可自动重试。")
            
        context.close()

if __name__ == "__main__":
    harvest_step()
