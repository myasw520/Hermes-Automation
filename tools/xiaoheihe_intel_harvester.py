# -*- coding: utf-8 -*-
"""
小黑盒（Heybox）游戏资讯与冷门神作情报全自动生成器 (升级版)
- AI 引擎：切换为主力 ZCode BigModel 渠道 (glm-5.3-flash / glm-5.3 深度推理引擎，背靠 25 亿 Token)
- 选品策略：聚焦【Steam 好评如潮 / 骨折只要一杯奶茶钱】的冷门宝藏独立游戏，杜绝大众游戏撞车
- 社区规范：严格适配 post-xiaoheihe skill 的 [cube_xxx] 专属表情与直球硬核文风
- 产出：Markdown 推文直接存入 reports/xiaoheihe_articles/，并提供小黑盒一键关联游戏清单
"""

import sys
import os
import json
import time
import argparse
import urllib.request
import urllib.error
from datetime import datetime

# Windows 终端编码守护
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "reports", "xiaoheihe_articles")
os.makedirs(OUTPUT_DIR, exist_ok=True)

KEYS_POOL_FILE = os.path.join(PROJECT_ROOT, "config", "keys_pool.json")
# Telegram 凭证统一从项目根 .env 读取（config_lib），不再硬编码
sys.path.insert(0, os.path.join(PROJECT_ROOT, "services"))
from config_lib import BOT_TOKEN, CHAT_ID, GATEWAY_URL, GATEWAY_KEY, GATEWAY_MODEL

TELEGRAM_CONFIG = {
    "bot_token": BOT_TOKEN,
    "chat_id": CHAT_ID,
    "topic_id": 3
}

def get_active_llm():
    """获取可用 LLM 客户端配置（优先 ZeroGate zcode 渠道）"""
    if os.path.exists(KEYS_POOL_FILE):
        try:
            with open(KEYS_POOL_FILE, "r", encoding="utf-8") as f:
                keys = json.load(f)
                for item in keys:
                    if item.get("name") == "ZeroGate-ZCode" and item.get("is_alive", True):
                        return {
                            "name": "ZeroGate-ZCode",
                            "url": f"{item['base_url'].rstrip('/')}/chat/completions",
                            "key": item["api_key"],
                            "model": item.get("default_model", "zcode/glm-5.3-flash")
                        }
                    elif item.get("name") == "ZCode-BigModel" and item.get("is_alive", True):
                        return {
                            "name": "ZCode-BigModel",
                            "url": f"{item['base_url'].rstrip('/')}/chat/completions",
                            "key": item["api_key"],
                            "model": item.get("default_model", "glm-4-plus")
                        }
                    elif item.get("name") == "ChatAnywhere" and item.get("is_alive", True):
                        return {
                            "name": "ChatAnywhere",
                            "url": f"{item['base_url'].rstrip('/')}/chat/completions",
                            "key": item["api_key"],
                            "model": "gpt-3.5-turbo"
                        }
        except Exception as e:
            print(f"[!] 读取 keys_pool.json 失败: {e}")
            
    # 回退配置（凭证从 .env 读取）
    return {
        "name": "ZeroGate-Fallback",
        "url": f"{GATEWAY_URL.rstrip('/')}/chat/completions",
        "key": GATEWAY_KEY,
        "model": GATEWAY_MODEL
    }

# ==================== 1. 数据采集：冷门小众独立神作 ====================

def fetch_steam_indie_gems():
    """从 Steam 抓取好评如潮、价格在 5~25 元以内的冷门小众折扣神作"""
    print("[*] 正在扫描 Steam 独立游戏特惠库 (好评优先 + 国区价格)...")
    url = (
        "https://store.steampowered.com/search/results/?"
        "query=&start=0&count=30&dynamic_data=&sort_by=Reviews_DESC&"
        "snr=1_7_7_230_7&filter=ut2&tags=492&specials=1&cc=cn&l=schinese&infinite=1"
    )
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept-Language": "zh-CN,zh;q=0.9"
    }
    
    gems = []
    try:
        from bs4 import BeautifulSoup
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            soup = BeautifulSoup(data.get("results_html", ""), "html.parser")
            rows = soup.find_all("a", class_="search_result_row")
            
            # 常见容易撞车的大众游戏黑名单（坚决不推）
            blacklist = ["gta", "cyberpunk", "witcher", "red dead", "monster hunter", "counter-strike", "dota", "apex", "pubg"]
            
            for r in rows:
                title = r.find("span", class_="title")
                title_str = title.text.strip() if title else ""
                
                # 黑名单过滤
                if any(b in title_str.lower() for b in blacklist):
                    continue
                    
                disc_elem = r.find("div", class_="discount_pct")
                disc_str = disc_elem.text.strip() if disc_elem else ""
                
                price_elem = r.find("div", class_="discount_final_price")
                price_str = price_elem.text.strip() if price_elem else ""
                
                # 提取纯数字价格判断
                import re
                price_num = re.findall(r'[\d\.]+', price_str)
                final_val = float(price_num[0]) if price_num else 999.0
                
                # 仅筛选 30 元以内的骨折宝藏神作
                if disc_str and final_val <= 30.0:
                    gems.append({
                        "title": title_str,
                        "discount": disc_str,
                        "price": price_str,
                        "price_val": final_val
                    })
                    if len(gems) >= 5:
                        break
                        
        print(f"[+] 成功挖掘出 {len(gems)} 款小众高口碑折扣神作！")
    except Exception as e:
        print(f"[-] Steam 小众游戏抓取异常: {e}")
        
    return gems

def fetch_epic_freebies():
    """获取 Epic 本周免费游戏"""
    print("[*] 正在扫描 Epic Games 官方免费送数据...")
    url = "https://store-site-backend-static-ipv4.ak.epicgames.com/freeGamesPromotions?locale=zh-CN&country=CN&allowCountries=CN"
    headers = {"User-Agent": "Mozilla/5.0"}
    req = urllib.request.Request(url, headers=headers)
    
    freebies = []
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            elements = data.get("data", {}).get("Catalog", {}).get("searchStore", {}).get("elements", [])
            for game in elements:
                title = game.get("title", "")
                price_info = game.get("price", {}).get("totalPrice", {})
                orig_price = price_info.get("originalPrice", 0) / 100
                disc_price = price_info.get("discountPrice", 0) / 100
                promotions = game.get("promotions") or {}
                if disc_price == 0 and promotions.get("promotionalOffers"):
                    freebies.append({
                        "title": title,
                        "orig_price": orig_price
                    })
        print(f"[+] Epic 当前白嫖: {len(freebies)} 款")
    except Exception as e:
        print(f"[-] Epic 抓取失败: {e}")
    return freebies

# ==================== 2. AI 深度推理与小黑盒重构 ====================

def generate_niche_xiaoheihe_article(gems, freebies, model_name="zcode/glm-5.3"):
    """调用 ZeroGate zcode 渠道，按照 post-xiaoheihe 社区规范生成文章"""
    llm = get_active_llm()
    if model_name:
        llm["model"] = model_name
    print(f"[*] 启动 AI 渠道: {llm['model']} @ {llm['url']} ...")
    
    # 构造素材清单
    materials = ["【精选冷门好评宝藏游戏】"]
    for g in gems:
        materials.append(f"- 《{g['title']}》: 折扣 {g['discount']} -> 现价仅 {g['price']}")
        
    if freebies:
        materials.append("\n【本周 Epic 免费白嫖】")
        for f in freebies:
            materials.append(f"- 《{f['title']}》: 原价 {f['orig_price']} 元 -> 现价 0 元")
            
    raw_text = "\n".join(materials)
    
    # 提示词 v2：接入 xhh-style-bible 总纲（167 篇热帖提炼），替代旧 15 行自制调性
    # 原则：skill 是单一事实来源，这里引用其核心而非复述全文；游戏分册见
    # .agents/skills/xhh-style-bible/references/track_game.md
    system_rules = (
        "【写作风格宪法——来自 167 篇真实小黑盒可充电热帖的审计结论，违反任何一条即为废稿】\n"
        "\n"
        "■ 三大人味密码：\n"
        "1. 真实的狼狈感与免责式自嘲：先泼冷水、交代局限、袒露翻车（例：'别学我，3 点睡觉第二天上班像行尸'）。\n"
        "   禁止全知全能、客观完美、热心鼓励式口吻。\n"
        "2. 烟火气与具体物理场景：写具体数字与场景（'宿舍 11 点断网'、'一杯奶茶钱'），禁止'提升体验''高性价比'这类虚词。\n"
        "3. 鲜明主观偏见 + 直接吐槽：敢下断言敢骂（'XX 嘛，能跑就行'），禁止'A 与 B 各有千秋，请根据需求选择'这种中立废话。\n"
        "\n"
        "■ 硬性执行规则：\n"
        "a. 每款游戏的写法必须各不相同——第一款可以正经点评，第二款可以通篇吐槽画面，第三款可以只讲一个翻车故事，\n"
        "   第四款可以一句话打发。严禁出现'玩法一句话+为什么值得买+踩坑提醒'这种机械对称模板。\n"
        "b. 高频口语词：其实、说白了、直接、顺手、真不行、哦豁、这破玩意、老实说；善用括号吐槽（别学我）（真的是）。\n"
        "c. 加粗只放结论与避坑点（'**必须开中文语音**'），绝不加粗整段。\n"
        "d. cube 表情克制：全篇 3~5 个，只放翻车打脸/情绪爆点处，段落开头不放。\n"
        "e. 结尾不升华不展望：留白、催更或直白收工（'欧克，打完收工'），禁止'希望这篇对你有帮助'。\n"
        "f. AI 味黑名单词一个不准出现：深入、赋能、携手、不容忽视、一站式、综上所述、值得一提的是、\n"
        "   总而言之、无论是…还是…、不仅…更…、点亮、解锁（游戏语境的解锁成就除外）、 delve、landscape。\n"
        "\n"
        "■ 本篇任务（游戏折扣安利帖）：\n"
        "1. 标题 20 字内带梗（例：《个位数捡漏！这几款好评如潮的冷门作香疯了》）。\n"
        "2. 开场 1~2 句个人动机唠嗑直接破题（为什么最近盯上冷门区），禁止'随着游戏市场的发展'。\n"
        "3. 逐款点评 3~4 款：规则 a 的差异化写法；价格信息（原价/现价/折扣力度）自然融进吐槽，不列表。\n"
        "4. E 宝限免顺带一嘴（赛博仓鼠式），1~2 句即可。\n"
        "5. 结尾：一个具体互动动作 + 2~3 个话题标签。\n"
        "直接输出 Markdown 原文，不要任何客套与前言。"
    )
    
    # 注意：ZCode 渠道协议不支持独立的 system 角色，必须合入首条 user 消息
    full_prompt = f"{system_rules}\n\n【实时抓取的一手游戏折扣与白嫖数据】：\n{raw_text}\n\n请直接输出小黑盒 Markdown 文章："
    
    payload = json.dumps({
        "model": llm["model"],
        "messages": [
            {"role": "user", "content": full_prompt}
        ],
        "max_tokens": 2400,
        "temperature": 0.7
    }).encode("utf-8")
    
    req = urllib.request.Request(
        llm["url"],
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {llm['key']}"
        }
    )
    
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            msg = data["choices"][0]["message"]
            reasoning = msg.get("reasoning_content")
            content = msg.get("content", "")
            usage = data.get("usage", {})
            
            elapsed = round(time.time() - t0, 1)
            print(f"[+] AI 思考与生成完毕（耗时 {elapsed}s）！")
            if reasoning:
                print(f"[*] 深度思考 Token 消耗: {usage.get('completion_tokens_details', {}).get('reasoning_tokens', 'N/A')}")
            print(f"[*] 本次总计消耗 Token: {usage.get('total_tokens', 'N/A')}（从 25 亿 Token 池扣除）")
            return content
    except Exception as e:
        print(f"[-] AI 推理失败: {e}")
        return None

# ==================== 3. 主入口与文件落地 ====================

def main():
    parser = argparse.ArgumentParser(description="小黑盒冷门宝藏神作全自动流水线")
    parser.add_argument("--push-tg", action="store_true", help="是否推送到 Telegram 话题群组")
    parser.add_argument("--model", type=str, default="zcode/glm-5.3", help="使用的 AI 模型 (默认: zcode/glm-5.3, 备选: zcode/glm-5.3-flash)")
    args = parser.parse_args()
    
    print("=" * 65)
    print("🎮 小黑盒【冷门宝藏打折神作】智能生成流水线启动")
    print(f"⏰ 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 65)
    
    # 1. 抓取冷门神作
    gems = fetch_steam_indie_gems()
    freebies = fetch_epic_freebies()
    
    if not gems:
        print("[-] 未能筛选出有效的冷门游戏，退出。")
        return
        
    # 2. 调用 AI 深度生成
    article = generate_niche_xiaoheihe_article(gems, freebies, model_name=args.model)
    if not article:
        print("[-] 文章生成失败。")
        return
        
    # 3. 保存至本地
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = os.path.join(OUTPUT_DIR, f"xiaoheihe_niche_post_{timestamp}.md")
    
    # 在文末附加上小黑盒“关联游戏”一键复制参考表
    appendix = "\n\n---\n### 📌 小黑盒发帖指引（手机端一秒关联词条）：\n"
    for g in gems:
        appendix += f"- 关联游戏搜索词: `{g['title']}`（当前价格: {g['price']}）\n"
    
    full_output = article + appendix
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(full_output)
        
    print("\n" + "=" * 65)
    print(f"🎉 成功生成！已保存至: {file_path}")
    print("=" * 65 + "\n")
    print(full_output)
    print("\n" + "=" * 65)
    
    if args.push_tg:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_CONFIG['bot_token']}/sendMessage"
            payload = json.dumps({
                "chat_id": TELEGRAM_CONFIG["chat_id"],
                "message_thread_id": TELEGRAM_CONFIG["topic_id"],
                "text": full_output[:3800],
                "parse_mode": "Markdown"
            }).encode("utf-8")
            req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                print("[+] 已成功推送到 Telegram 话题群组！")
        except Exception as e:
            print(f"[-] Telegram 推送失败: {e}")

if __name__ == "__main__":
    main()
