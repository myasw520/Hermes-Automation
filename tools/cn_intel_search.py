"""
国内情报与免费资源嗅探工具 (cn_intel_search.py)
覆盖源:
1. B站 (Bilibili): 深度挖掘免费 API、开源 AI、本地部署、白嫖 VPS 等教程及置顶链接
2. 喜加一官方数据流: 聚合 Steam / Epic 官方限时 100% 免费领游戏/软件
"""

import sys, os, time, json, re, urllib.request, urllib.parse, requests
sys.path.append(r'C:\Users\zzx05\Hermes-Automation\services')
from wool_radar import send_telegram_text, TOPIC_WOOL_ID, TOPIC_GITHUB_ID, TOPIC_CHAT_ID
from config_lib import GATEWAY_URL, GATEWAY_KEY, GATEWAY_MODEL
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# 动态挂载活态大模型节点 (优先 ZeroGate/ZCode 25亿Token池)
def get_best_llm_node():
    pool_file = r"C:\Users\zzx05\Hermes-Automation\config\keys_pool.json"
    if os.path.exists(pool_file):
        try:
            with open(pool_file, "r", encoding="utf-8") as f:
                pool = json.load(f)
                alive = [x for x in pool if x.get("is_alive", True)]
                if alive:
                    for node in alive:
                        if "zerogate" in (node.get("name") or "").lower() or "zcode" in (node.get("name") or "").lower():
                            burl = node.get("base_url", "").rstrip("/")
                            return f"{burl}/chat/completions", node.get("api_key"), node.get("default_model") or "zcode/glm-5.3-flash"
                    n = alive[0]
                    burl = n.get("base_url", "").rstrip("/")
                    return f"{burl}/chat/completions", n.get("api_key"), n.get("default_model") or "gpt-4o-mini"
        except Exception:
            pass
    return f"{GATEWAY_URL.rstrip('/')}/chat/completions", GATEWAY_KEY, GATEWAY_MODEL

API_URL, API_KEY, MODEL_NAME = get_best_llm_node()
PROXY = {"http": "http://127.0.0.1:7897", "https": "http://127.0.0.1:7897"}
PROFILE_DIR = r"C:\Users\zzx05\.gemini\antigravity\scratch\bot_chrome_profile"

def search_bilibili(keyword, count=4):
    """通过自动化浏览器检索 B站 最新发布的高质量视频与资源"""
    print(f"[*] 正在检索 B站 最新情报: [{keyword}] ...")
    results = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            PROFILE_DIR,
            channel="chrome",
            headless=True,
            viewport={"width": 1280, "height": 850},
            args=["--no-first-run", "--no-default-browser-check"]
        )
        page = browser.pages[0] if browser.pages else browser.new_page()
        
        # 按最新发布排序
        url = f"https://search.bilibili.com/all?keyword={urllib.parse.quote(keyword)}&order=pubdate"
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=20000)
            time.sleep(3)
            
            cards = page.locator('.bili-video-card, .video-list-item').all()
            for card in cards[:count]:
                try:
                    title_el = card.locator('h3, .bili-video-card__info--tit').first
                    title = title_el.inner_text().strip() if title_el.is_visible() else ""
                    
                    link_el = card.locator('a[href*="/video/"]').first
                    href = link_el.get_attribute("href") if link_el.is_visible() else ""
                    if href and not href.startswith("http"):
                        href = f"https:{href}" if href.startswith("//") else f"https://www.bilibili.com{href}"
                    # 清理跟踪参数
                    if "?" in href:
                        href = href.split("?")[0]
                        
                    author_el = card.locator('.bili-video-card__info--author, .up-name').first
                    author = author_el.inner_text().strip() if author_el.is_visible() else "未知UP"
                    
                    date_el = card.locator('.bili-video-card__info--date').first
                    date_text = date_el.inner_text().strip() if date_el.is_visible() else "近期"
                    
                    if title and href:
                        results.append({
                            "title": title,
                            "url": href,
                            "author": author,
                            "date": date_text
                        })
                except Exception:
                    continue
        except Exception as e:
            print("[-] B站抓取异常:", e)
        finally:
            browser.close()
            
    return results

def get_epic_free_games():
    """实时查询 Epic 官方正在限时免费（喜加一）的游戏"""
    print("[*] 正在查询本周官方限时 100% 免费领游戏 (喜加一)...")
    url = "https://store-site-backend-static-ipv4.ak.epicgames.com/freeGamesPromotions?locale=zh-CN&country=CN&allowCountries=CN"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            elements = data.get("data", {}).get("Catalog", {}).get("searchStore", {}).get("elements", [])
            
            free_games = []
            for item in elements:
                promotions = item.get("promotions")
                if not promotions:
                    continue
                promo_offers = promotions.get("promotionalOffers", [])
                if promo_offers:
                    offers = promo_offers[0].get("promotionalOffers", [])
                    for offer in offers:
                        discount = offer.get("discountSetting", {})
                        if discount.get("discountPercentage") == 0:
                            # 100% 免费
                            title = item.get("title")
                            desc = item.get("description")
                            end_date = offer.get("endDate", "")[:10]
                            page_slug = item.get("productSlug") or (item.get("catalogNs", {}).get("mappings", [{}])[0].get("pageSlug", ""))
                            store_url = f"https://store.epicgames.com/zh-CN/p/{page_slug}" if page_slug else "https://store.epicgames.com/zh-CN/free-games"
                            free_games.append({
                                "title": title,
                                "desc": desc,
                                "end_date": end_date,
                                "url": store_url
                            })
            return free_games
    except Exception as e:
        print("[-] Epic 限免查询异常:", e)
        return []

def summarize_with_ai(prompt):
    """调用免费 GPT-4o-mini 提炼结论"""
    try:
        use_proxies = None if any(h in API_URL for h in ["192.168.", "127.0.0.1", "localhost"]) else PROXY
        r = requests.post(
            API_URL,
            headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
            json={
                "model": MODEL_NAME,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 400,
                "temperature": 0.2
            },
            proxies=use_proxies,
            timeout=15
        )
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"].strip()
    except Exception:
        pass
    return None

def run_bili_intelligence(keyword="免费API", target_topic=TOPIC_WOOL_ID):
    """运行 B站情报脱水并推流 Telegram"""
    videos = search_bilibili(keyword, count=4)
    if not videos:
        print("[-] 未检索到有效视频")
        return

    content_list = []
    for v in videos:
        content_list.append(f"• 标题: {v['title']} (UP: {v['author']}, 时间: {v['date']})\n  链接: {v['url']}")

    prompt = (
        f"请作为资深技术情报员，对以下关于【{keyword}】的最新视频列表进行极速精炼总结：\n\n"
        + "\n".join(content_list) + "\n\n"
        "请用 3 句话总结这些视频中透露的最有价值的免费工具、接口或技巧，并挑出 2 个最值得看的视频链接给用户。"
    )
    
    print("[*] 正在调用 AI 智能脱水提炼...")
    ai_digest = summarize_with_ai(prompt) or "请查看以下推荐视频。"

    msg = (
        f"📺 *【B站情报速递: {keyword}】*\n\n"
        f"{ai_digest}\n\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        + "\n\n".join([f"🎬 *[{v['title']}]({v['url']})*\n👤 UP: `{v['author']}` | 🕒 {v['date']}" for v in videos[:3]])
    )
    
    send_telegram_text(target_topic, msg)
    print(f"🎉 B站情报已推送到 Telegram 话题 {target_topic}！")

def run_free_games_intelligence():
    """运行游戏喜加一情报监控并推流 Telegram"""
    games = get_epic_free_games()
    if not games:
        print("[-] 当前暂无进行中的 100% 喜加一活动")
        return

    lines = ["🎮 *【限时喜加一！正版游戏免费白嫖】*\n"]
    for g in games:
        lines.append(
            f"🎁 *[{g['title']}]({g['url']})*\n"
            f"📝 简介: {g['desc'][:80]}...\n"
            f"⏰ 截止日期: `{g['end_date']}`\n"
            f"🔗 领取链接: {g['url']}\n"
        )
        
    msg = "\n".join(lines)
    send_telegram_text(TOPIC_WOOL_ID, msg)
    print("🎉 喜加一情报已推送到 Telegram 话题 3！")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="国内情报与免费资源嗅探工具")
    parser.add_argument("--bili", type=str, default="", help="搜索 B站 关键词并推流 Telegram")
    parser.add_argument("--freegames", action="store_true", help="查询最新正版游戏喜加一")
    args = parser.parse_args()

    if args.freegames:
        run_free_games_intelligence()
    elif args.bili:
        run_bili_intelligence(args.bili)
    else:
        # 默认执行一次喜加一和一次免费API探路
        print("运行默认巡检...")
        run_free_games_intelligence()
        run_bili_intelligence("免费API")
