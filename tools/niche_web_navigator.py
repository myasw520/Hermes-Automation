#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Niche Web Navigator & Knowledge Engine (冷门小众网站/黑科技/科研查资料/接码代充导航引擎)
================================================================================
专为极客、科研学者、出海开发者打造的冷门高价值站点数据库与查询器。
支持按分类速查、关键词搜索、支付宝支持筛选、反坑避雷提示与 Markdown 报表自动导出。
"""

import os
import sys
import json
import argparse
from datetime import datetime

# Windows 终端 UTF-8 编码安全重置
try:
    if sys.stdout.encoding.lower() != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
    if sys.stderr.encoding.lower() != 'utf-8':
        sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "niche_web_vault", "niche_websites.json")
MARKDOWN_PATH = os.path.join(BASE_DIR, "data", "niche_web_vault", "NICHE_WEB_VAULT.md")
POST_PATH = os.path.join(BASE_DIR, "reports", "xiaoheihe_niche_sites.md")

def load_data():
    if not os.path.exists(DATA_PATH):
        print(f"[-] 错误: 找不到数据文件 {DATA_PATH}")
        sys.exit(1)
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def generate_markdown_docs(data):
    """自动生成完整结构化 Markdown 知识库与小黑盒直球推文"""
    os.makedirs(os.path.dirname(MARKDOWN_PATH), exist_ok=True)
    os.makedirs(os.path.dirname(POST_PATH), exist_ok=True)

    categories = {c["id"]: c for c in data["categories"]}
    websites = data["websites"]

    # 1. 生成 master 文档: NICHE_WEB_VAULT.md
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    md = f"""# 🌐 冷门小众高价值网站全景导航与极客避坑宝典
> *最后修订: {now_str} | 已收录收敛站点: {len(websites)} 个 | 覆盖四大刚需领域*

---

## 🧭 领域速查索引

"""
    for cid, c in categories.items():
        count = sum(1 for w in websites if w["category"] == cid)
        md += f"- **{c['icon']} [{c['name']}](#{cid})** ({count} 个神器) —— *{c['description']}*\n"

    md += "\n---\n\n"

    for cid, c in categories.items():
        cat_sites = [w for w in websites if w["category"] == cid]
        md += f"## <a id='{cid}'></a>{c['icon']} {c['name']}\n"
        md += f"> *{c['description']}*\n\n"
        
        md += "| 站点名称 | 访问地址 | 费用/门槛 | 支付宝友好 | 核心解决痛点与不可替代性 |\n"
        md += "| :--- | :--- | :---: | :---: | :--- |\n"
        for s in cat_sites:
            alipay_badge = "✅ 支持" if s["alipay_supported"] else "❌ 需海外卡/USDT"
            md += f"| **{s['name']}** | [{s['url']}]({s['url']}) | `{s['cost_type']}` | {alipay_badge} | {s['pain_point']} |\n"
        
        md += "\n### 🔍 深度详评与防坑避雷指南\n\n"
        for s in cat_sites:
            alipay_badge = "✅ 支付宝友好" if s["alipay_supported"] else "⚠️ 需海外支付/USDT"
            md += f"#### [{s['name']}]({s['url']})\n"
            md += f"- **标签属性**: `{'` `'.join(s['tags'])}`\n"
            md += f"- **付费与门槛**: `{s['cost_type']}` | **支付渠道**: `{alipay_badge}`\n"
            md += f"- **精准痛点**: {s['pain_point']}\n"
            md += f"- **降维亮点**: {s['highlights']}\n"
            md += f"- **🛡️ 避坑建议与技术边界**: `{s['risk_note']}`\n\n"
        
        md += "---\n\n"

    with open(MARKDOWN_PATH, "w", encoding="utf-8") as f:
        f.write(md)

    # 2. 生成小黑盒直球推文: xiaoheihe_niche_sites.md
    post = f"""# 收藏夹别只装百度和B站了！这些压箱底的冷门黑科技与出海神站建议焊死

兄弟们好，我是老张！[cube_点赞]

平时无论是搞科研查文献、折腾极客工具，还是玩 AI 想搞个海外账号/接码充值，最恶心的就是百度搜出来全是一堆营销软文、钓鱼假站或者动不动割你大几百的二道贩子。[cube_吐血]

今天老哥把我私藏的**高价值冷门小众站点**一口气端出来！全都是**真正解决刚需、没有流氓弹窗、性价比直接拉满**的硬核站点，带上防坑指南，建议直接收藏吃灰备用！[cube_挑衅]

---

## 1. 学习科研与学术查资料（穿透付费墙与文献拓扑）
- **[Anna's Archive (安娜档案)](https://annas-archive.org)**：[cube_酷] 全球最大的影子图书馆元数据库！整合了 Sci-Hub、Libgen、Z-Library。找任何原版 PDF 电子书或绝版文献，贴 DOI 直接秒出，再也不用被各大数据库的付费墙恶心！
- **[Connected Papers](https://www.connectedpapers.com)**：文献可视化拓扑神器。输入一篇开山顶会论文，自动生成星系图般的引文演进网络，哪个是基石、哪个是最新衍生，一眼看穿脉络！
- **[Archive.today](https://archive.today)**：快照与穿透神器。不仅能永久存证防删，还能直接绕开外网大量新闻和技术博客的动态 JS 付费墙弹窗。

---

## 2. 极客黑科技与在线神级生产力
- **[Cobalt.tools](https://cobalt.tools)**：[cube_赞] 全球最良心的多平台视频解析站！油管、B站、推特、TikTok 粘贴链接直接下无水印原画，**零弹窗、零广告、不推恶心全家桶**，吊打市面上一切商业垃圾站！
- **[CyberChef (GCHQ 开源)](https://gchq.github.io/CyberChef)**：英国国家情报局开源的“数据加工厨房”。Base64/Hex/URL/Gzip/AES/正则，纯前端单页面拖拽流水线一气呵成，离线可用，逆向分析神器！
- **[Any.Run](https://any.run)**：免费云端交互式恶意沙箱。怀疑群里发的 exe 或压缩包有木马？丢进去直接给你一台浏览器里的虚拟机，看它后台悄悄连了哪些 IP、改了哪些注册表，无处遁形！

---

## 3. 真实好用的全球接码平台（防风控与极低成本）
- **[DaisySMS](https://daisysms.com)**：[cube_思考] **美国真实物理 SIM 实体卡接码**！单次约 $0.5 ~ $1.5。很多廉价平台给的是虚拟号（VoIP），OpenAI 和 Claude 风控直接秒封。如果必须过高风控实卡验证，认准这家，收不到短信自动全额退款！
- **[SMS-Activate](https://sms-activate.org)**：老牌战斗民族接码龙头，**原生支持支付宝扫码充值**！覆盖全球 170+ 国家，单次注册只要几毛到一块钱，日常注册普通海外应用、社交软件的最佳高性价比方案。

---

## 4. 出海虚拟卡、代充与合租拼车（省钱指南）
- **[WildCard](https://bewildcard.com)**：[cube_开心] 专治国内银行卡无法支付 OpenAI/Claude/Cursor/Midjourney 订阅。微信支付宝直接扫码充，自带正规美国家庭环境与账单地址生成，专防 Stripe 支付风控封号。
- **[银河录像局](https://nf.video)**：国内头部合租拼车平台。如果不想一个人硬扛每月 140+ 块钱的 ChatGPT Plus 或 Claude 独享车，可以走这种独立对话隔离的合租车位，支持微信支付宝且有掉线售后换号。
- **[Gamsgo](https://www.gamsgo.com)**：老牌跨国流媒体拼车平台，Netflix/YouTube Premium/Spotify 价格极度便宜（最低每月几块到十几块），省下大笔开销！

---

### 老哥避坑总结
1. **不要在公开免费接码池绑定重要银行卡或主邮箱**；
2. **需要强风控海外 AI 账号时，实体卡 > 虚拟卡 > 廉价共享号**；
3. **好网站不需要花里胡哨的充值弹窗，纯净、单点突破才是神仙站的标准**！[cube_干杯]

你们平时还私藏过哪些舍不得删的冷门宝藏站？评论区互相偷师！[cube_斜眼笑]
"""
    with open(POST_PATH, "w", encoding="utf-8") as f:
        f.write(post)

    print(f"[+] 结构化全景知识库已生成: {MARKDOWN_PATH}")
    print(f"[+] 小黑盒直球推文已生成: {POST_PATH}")

def search_sites(keyword=None, category=None, alipay_only=False):
    data = load_data()
    sites = data["websites"]

    if category:
        sites = [s for s in sites if s["category"].lower() == category.lower()]
    if alipay_only:
        sites = [s for s in sites if s["alipay_supported"]]
    if keyword:
        kw = keyword.lower()
        sites = [
            s for s in sites 
            if kw in s["name"].lower() or kw in s["pain_point"].lower() 
            or kw in s["highlights"].lower() or any(kw in t.lower() for t in s["tags"])
        ]

    print(f"\n[*] 🔍 检索到 {len(sites)} 个符合条件的神级冷门站点：")
    print("=" * 80)
    for s in sites:
        alipay_badge = "✅ 支付宝直充" if s["alipay_supported"] else "⚠️ 需海外卡/USDT"
        print(f"📌 【{s['name']}】  ({s['url']})")
        print(f"   类别: {s['category']} | 费用: {s['cost_type']} | 支付方式: {alipay_badge}")
        print(f"   标签: {', '.join(s['tags'])}")
        print(f"   痛点: {s['pain_point']}")
        print(f"   亮点: {s['highlights']}")
        print(f"   避坑: {s['risk_note']}")
        print("-" * 80)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Niche Web Navigator")
    parser.add_argument("--search", "-s", type=str, help="按关键词全局搜索")
    parser.add_argument("--category", "-c", type=str, help="按分类筛选 (academic_research / geek_black_tech / sms_verification / virtual_cards_subs)")
    parser.add_argument("--alipay", action="store_true", help="仅显示支持支付宝的网站")
    parser.add_argument("--export", action="store_true", help="重新生成 Markdown 知识库与小黑盒推文")
    args = parser.parse_args()

    data = load_data()
    generate_markdown_docs(data)

    if args.search or args.category or args.alipay:
        search_sites(keyword=args.search, category=args.category, alipay_only=args.alipay)
    else:
        print("[*] 数据与知识库已同步就绪。使用 -h 查看查询参数。")
