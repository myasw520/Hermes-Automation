import time
import json
import os
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# ================= 配置区 =================
# 凭证统一从项目根 .env 读取（config_lib），不再硬编码
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config_lib import BOT_TOKEN, CHAT_ID
TOPIC_WOOL_ID = 3                 # 羊毛情报话题 ID
TOPIC_GITHUB_ID = 4               # GitHub 高星话题 ID
TOPIC_CHAT_ID = 5                 # 随时对话话题 ID

HERMES_API_URL = os.environ.get("HERMES_API_URL", "http://localhost:8642/v1/chat/completions")
HERMES_API_KEY = os.environ.get("HERMES_API_KEY", "")
HERMES_MODEL_NAME = os.environ.get("HERMES_MODEL_NAME", "hermes-agent")

FEEDS = [
    {"name": "V2EX-全部", "url": "https://www.v2ex.com/index.xml"},
]

HISTORY_FILE = os.path.join(os.path.dirname(__file__), "pushed_history.json")
POLL_INTERVAL_SECONDS = 600
# ==========================================

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()

def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(list(history)[-1000:], f, ensure_ascii=False, indent=2)

def send_telegram_photo(thread_id, caption, photo_path):
    """带图片推送到指定话题"""
    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    
    with open(photo_path, "rb") as f:
        photo_bytes = f.read()

    body = []
    body.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"chat_id\"\r\n\r\n{CHAT_ID}\r\n".encode("utf-8"))
    body.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"message_thread_id\"\r\n\r\n{thread_id}\r\n".encode("utf-8"))
    body.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"caption\"\r\n\r\n{caption}\r\n".encode("utf-8"))
    filename = os.path.basename(photo_path)
    body.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"photo\"; filename=\"{filename}\"\r\nContent-Type: image/png\r\n\r\n".encode("utf-8"))
    body.append(photo_bytes)
    body.append(f"\r\n--{boundary}--\r\n".encode("utf-8"))

    payload = b"".join(body)
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"[-] Telegram 图片推送失败: {e}")
        return False

def send_telegram_text(thread_id, text):
    """文本推送到指定群组话题"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = json.dumps({
        "chat_id": CHAT_ID,
        "message_thread_id": thread_id,
        "text": text,
        "disable_web_page_preview": False
    }).encode("utf-8")

    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"[-] Telegram 文本推送失败: {e}")
        return False

def probe_website(target_url):
    """【自主探路】真实打开网页并截图，提取现场文本（具备防撞锁自愈）"""
    profile_dir = r"C:\Users\zzx05\.gemini\antigravity\scratch\bot_chrome_profile"
    screenshot_file = os.path.join(os.path.dirname(__file__), "probe_screenshot.png")
    page_text = ""
    try:
        proxy_config = {"server": "http://127.0.0.1:7897"}
        with sync_playwright() as p:
            try:
                context = p.chromium.launch_persistent_context(
                    profile_dir,
                    channel="chrome",
                    headless=True,
                    viewport={"width": 1280, "height": 800},
                    proxy=proxy_config,
                    args=["--no-first-run", "--no-default-browser-check"]
                )
            except Exception:
                context = p.chromium.launch(channel="chrome", headless=True, proxy=proxy_config).new_context(viewport={"width": 1280, "height": 800})

            page = context.pages[0] if context.pages else context.new_page()
            page.goto(target_url, timeout=30000, wait_until="domcontentloaded")
            time.sleep(3)
            page.screenshot(path=screenshot_file, full_page=False)
            page_text = page.inner_text("body")[:1500]
            context.close()
        return True, screenshot_file, page_text
    except Exception as e:
        print(f"[-] 探路访问失败: {e}")
        return False, None, ""

def call_hermes_diagnosis(post_title, post_content, live_site_text):
    """呼叫 Hermes 结合现场页面进行深度诊断（严格防耍猴）"""
    system_prompt = (
        "你是一个极其严苛的极客资源鉴别专家。用户的关注点非常垂直，只在乎【真正能用的硬核基础设施资源】！\n\n"
        "【必须丢弃并判定为无效的情况】（只要满足任意一条，直接且仅回复：IGNORE）：\n"
        "1. 软件/APP送码：独立开发软件推广、自研工具发布、送注册码、送激活码、送兑换码、App Store 限免、送会员月卡（用户完全不玩这些垃圾软件！）；\n"
        "2. 套路营销：要求“加群领、私聊服主、回帖抽奖、公众号回复”才给额度的；\n"
        "3. 蝇头小利：杂牌个人小中转站仅送 1~2 元（低于 $2）额度的；\n"
        "4. 纯招聘、找工作、买卖二手、普通技术求助提问；\n"
        "5. 现场页面显示 Sold Out、404、或必须绑定个人真实信用卡扣费的。\n\n"
        "【唯一允许通过的高价值三大领域】：\n"
        "1. AI API 接口/中转站额度：知名云厂商/正规免绑卡推理 API（如 Groq、Together、Cloudflare、GitHub Token、New API/One API 真正开放免费赠送）且无需人工审核；\n"
        "2. 云服务器 / VPS / GPU 算力：免费或极低骨折价云主机、海外免绑卡 VPS、算力平台赠送额度；\n"
        "3. 廉价/免费顶级域名促销：正规注册商特价域名、免费二级分发。\n\n"
        "【输出格式】（仅通过时输出）：\n"
        "🚨 【实地探路战报】 [平台名称]\n"
        "📊 现场状态：[正常开放 / 免绑卡]\n"
        "💎 真实额度：[给什么，如：赠送 $25 额度 / 永久免费套餐]\n"
        "🔑 获取门槛：[简明扼要门槛]\n"
        "💡 探路建议：[一句话建议]"
    )
    user_prompt = f"【原帖描述】\n标题: {post_title}\n详情: {post_content}\n\n【浏览器现场抓取内容】\n{live_site_text}"

    payload = json.dumps({
        "model": HERMES_MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.1
    }).encode("utf-8")

    req = urllib.request.Request(
        HERMES_API_URL, 
        data=payload, 
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {HERMES_API_KEY}"}
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"[-] Hermes 诊断异常: {e}")
        return None

def extract_first_url(text):
    urls = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', text)
    if urls:
        url = urls[0]
        if not re.search(r'\.(png|jpg|jpeg|gif)$', url, re.I):
            return url
    return None

def scan_once():
    print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] 正在扫描最新社区动态...")
    history = load_history()
    new_found = 0

    for feed in FEEDS:
        items = fetch_rss(feed["url"])
        print(f"  > 抓取 {feed['name']} 得到 {len(items)} 条内容")
        for item in items:
            item_id = item["link"] or item["title"]
            if not item_id or item_id in history:
                continue

            history.add(item_id)
            new_found += 1
            print(f"  [新贴初审] {item['title'][:40]}...")

            target_url = extract_first_url(f"{item['title']} {item['content']}") or item["link"]
            
            if target_url and target_url.startswith("http"):
                # 如果命中明显水贴或软件送码垃圾关键词，连浏览器都不要开，直接跳过省资源
                bad_keywords = [
                    "抽奖", "加群", "微信群", "私聊", "返佣", "找工作", "求助", "出闲置",
                    "送码", "送激活码", "送兑换码", "送注册码", "兑换码", "激活码", "自研",
                    "限免", "App限免", "送月卡", "软件分享", "独立开发", "TestFlight", "App Store"
                ]
                if any(k in item['title'] for k in bad_keywords):
                    print("  💤 命中水贴/套路关键词，直接跳过。")
                    continue

                print(f"  🚀 正在派遣无头浏览器实地探路: {target_url} ...")
                ok, screenshot_path, live_text = probe_website(target_url)
                if ok:
                    print(f"  🤖 正在让 Hermes-Agent 进行深度防耍猴诊断...")
                    diagnosis = call_hermes_diagnosis(item["title"], item["content"][:600], live_text)
                    if diagnosis and "IGNORE" not in diagnosis and "实地探路战报" in diagnosis:
                        print(f"  🔥 判定为真正高价值福利！正在推送到群组话题 3...")
                        caption = f"{diagnosis}\n\n🔗 直达链接: {target_url}"
                        send_telegram_photo(TOPIC_WOOL_ID, caption, screenshot_path)

                        # 自动触发提 Key 闭环: 如果是 AI API / 中转站类型，立即自动调用通用收割器提 Key
                        if any(k in diagnosis for k in ["API", "中转", "令牌", "Token", "New API", "One API"]):
                            print(f"  🎯 发现目标为 AI API 站点，立即调度通用收割器 (oneapi_harvester) 自动提 Key ...")
                            try:
                                sys.path.append(r'C:\Users\zzx05\Hermes-Automation\tools')
                                from oneapi_harvester import automate_one_api_harvest
                                harvest_success = automate_one_api_harvest(target_url)
                                if harvest_success:
                                    print(f"  🎉 恭喜！已从 {target_url} 成功自动提取 Key 并存入蓄水池！")
                                    send_telegram_text(
                                        TOPIC_WOOL_ID,
                                        f"🎉 *【全自动收割大成功】*\n已为新中转站 `{target_url}` 完成自动授权/开户、提取 Key 并同步存入 `keys_pool.json`！"
                                    )
                                else:
                                    print(f"  [-] 该站点非标准 One-API 架构或有强人机验证，已记录情报供人工处理。")
                            except Exception as he:
                                print(f"  [-] 自动收割模块调用异常: {he}")
                    else:
                        print(f"  💤 经 Hermes 鉴定为套路/小额中转/无效信息，已果断抛弃。")
            else:
                print("  💤 无有效直达链接，已跳过。")

    save_history(history)
    print(f"[{time.strftime('%H:%M:%S')}] 扫描完成，共分析 {new_found} 条新帖。\n")

def fetch_rss(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            xml_data = resp.read()
            root = ET.fromstring(xml_data)
            items = []
            for item in root.findall(".//item"):
                t = item.findtext("title") or ""
                l = item.findtext("link") or ""
                d = item.findtext("description") or ""
                items.append({"title": t, "link": l, "content": d})
            if not items:
                ns = {'atom': 'http://www.w3.org/2005/Atom'}
                for entry in root.findall(".//atom:entry", ns):
                    t = entry.findtext("atom:title", namespaces=ns) or ""
                    link_elem = entry.find("atom:link", namespaces=ns)
                    l = link_elem.attrib.get("href", "") if link_elem is not None else ""
                    c = entry.findtext("atom:content", namespaces=ns) or ""
                    items.append({"title": t, "link": l, "content": c})
            return items
    except Exception as e:
        print(f"[-] 抓取 RSS 失败 {url}: {e}")
        return []

def start_loop():
    print("==================================================")
    print("🤖 Hermes 24小时羊毛雷达巡检已启动！(防套路纯享版)")
    print(f"📡 目标群组: {CHAT_ID} (羊毛情报话题 ID: {TOPIC_WOOL_ID})")
    print(f"🧠 推理大脑: Docker Hermes-Agent (8642)")
    print(f"⏱️ 轮询频率: 每 {POLL_INTERVAL_SECONDS} 秒一次")
    print("==================================================")
    
    if "--once" in sys.argv:
        scan_once()
        return

    # 启动时直接发向群组的【羊毛情报】话题 3
    send_telegram_text(TOPIC_WOOL_ID, "🚀 *Hermes 羊毛雷达已就绪！(纯净防套路版)*\n\n已锁定推送到本话题，已开启全网防耍猴审查，小额中转与套路帖已全面屏蔽，只推送真正高价值福利！")

    while True:
        try:
            scan_once()
        except Exception as e:
            print(f"[-] 轮询扫描异常: {e}")
        time.sleep(POLL_INTERVAL_SECONDS)

if __name__ == "__main__":
    start_loop()
