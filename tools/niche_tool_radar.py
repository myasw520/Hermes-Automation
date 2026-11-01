# -*- coding: utf-8 -*-
"""
全网【冷门好用极客神级工具雷达】(niche_tool_radar.py)
- 特点：不局限于开源（包含极高口碑的闭源独立神器、单文件工具、免折腾利器）
- 维度：游戏黑科技 / Windows 恶心痛点根治 / 学习与考研效率 / 局域网与极客小品
- 调性：杜绝 AI 假大空废话，句句大实话，直击痛点与避坑点
- AI 引擎：ZeroGate zcode/glm-5.3 深度推理
- 产出：reports/niche_tools/
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
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "reports", "niche_tools")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 网关凭证统一从项目根 .env 读取（config_lib），不再硬编码
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "services"))
from config_lib import GATEWAY_URL as _CFG_GATEWAY_URL, GATEWAY_KEY as _CFG_GATEWAY_KEY
GATEWAY_URL = f"{_CFG_GATEWAY_URL.rstrip('/')}/chat/completions"
GATEWAY_KEY = _CFG_GATEWAY_KEY
MODEL_NAME = "zcode/glm-5.3"

# ==================== 1. 精选冷门/高价值神级工具库 ====================

CURATED_TOOLS = [
    {
        "name": "Lossless Scaling",
        "type": "闭源商业小品 (Steam 仅20多元)",
        "category": "游戏显示黑科技",
        "official_url": "https://store.steampowered.com/app/993090/Lossless_Scaling/",
        "pain_point": "老显卡/核显玩游戏帧率拉胯卡顿，或者老游戏锁 30/60 帧，官方不支持 DLSS 3 帧生成。",
        "killer_feature": "独家 LSFG (帧生成) 算法与空间缩放！不需要任何游戏支持，在 Windows 桌面级强行给任何游戏甚至视频'插帧'，直接 30 帧变 60 帧、60 帧变 120 帧，肉眼顺滑到飞起。",
        "geek_score": 9.8
    },
    {
        "name": "LocalSend",
        "type": "开源免费 (GitHub 50k+ Star)",
        "category": "跨设备极速互传",
        "official_url": "https://localsend.org/",
        "pain_point": "手机和电脑互传文件，用微信会压缩文件而且要走腾讯外网服务器，蓝牙速度慢如蜗牛，AirDrop 又被苹果生态锁死。",
        "killer_feature": "完全基于局域网通信，免注册、免登录、免公网。两台设备连同一个 Wi-Fi 秒级自动发现，点对点千兆内网跑满，零隐私泄露风险。",
        "geek_score": 9.7
    },
    {
        "name": "ContextMenuManager",
        "type": "开源轻量单文件",
        "category": "Windows 痛点清道夫",
        "official_url": "https://github.com/BluePointLilac/ContextMenuManager",
        "pain_point": "Windows 用久了，右键菜单被各种国产流氓软件、网盘、解压软件塞得像老太婆的裹脚布，点开右键甚至要卡顿 2 秒。",
        "killer_feature": "仅几百 KB 的单文件纯净神器，清晰将右键菜单按'文件/文件夹/桌面/发送到'分门别类，一键物理屏蔽或彻底删除流氓右键项，瞬间还你秒级响应。",
        "geek_score": 9.6
    },
    {
        "name": "Auto Actions",
        "type": "开源免费",
        "category": "游戏硬件自动化",
        "official_url": "https://github.com/Codectory/AutoActions",
        "pain_point": "高刷显示器平时办公想省电开 60Hz，玩 CS2/瓦罗兰特想开 240Hz；玩 3A 想开 HDR，退出来桌面看 HDR 发灰发白，每次都要手动进系统设置反复点。",
        "killer_feature": "绑定游戏进程自动触发！打开特定游戏自动拉满 240Hz、开启 HDR 并切换卓越性能电源计划；游戏一关，瞬间自动还原为省电办公模式，完全无人值守。",
        "geek_score": 9.5
    },
    {
        "name": "Umi-OCR",
        "type": "开源完全离线",
        "category": "生产力与排版",
        "official_url": "https://github.com/hiroi-sora/Umi-OCR",
        "pain_point": "想要识别考研 PDF、论文或者游戏截图里的文字/表格，网上的 OCR 工具要么收费、要么要求上传云端偷隐私、要么排版全乱套。",
        "killer_feature": "本地内置 PaddleOCR 推理引擎，拔掉网线照样秒级识别！最绝的是支持'还原表格排版'和'截图直接输出 Markdown/LaTeX'，考研党与程序员神器。",
        "geek_score": 9.6
    },
    {
        "name": "Geek Uninstaller",
        "type": "闭源免费单文件",
        "category": "系统深度清理",
        "official_url": "https://geekuninstaller.com/",
        "pain_point": "Windows 自带控制面板卸载软件永远卸不干净，残留的 AppData 垃圾和注册表几十万条死键把系统拖慢。",
        "killer_feature": "单文件免安装，体积不到 3MB。常规卸载后立即深层扫描注册表、残留临时文件夹，甚至支持'强制粉碎卸载'顽固流氓后台。",
        "geek_score": 9.7
    },
    {
        "name": "LosslessCut",
        "type": "开源无损切片",
        "category": "多媒体极客工具",
        "official_url": "https://github.com/mifi/lossless-cut",
        "pain_point": "录制了几十分钟的游戏超神集锦或者考研网课，只想切出其中 2 分钟，扔进剪映/PR 重新导出慢得要死而且画质变糊。",
        "killer_feature": "直接基于 ffmpeg 关键帧流复制，【绝对不重新编码】！截取一段 4K 60 帧视频只要 0.5 秒，原画质 100% 保留，零 CPU 占用。",
        "geek_score": 9.8
    }
]

# ==================== 2. AI 深度排雷与极客评测生成 ====================

def generate_tool_review(tool_data):
    """呼叫 zcode/glm-5.3 生成充满极客老哥直球味道的干货评测"""
    name = tool_data["name"]
    t_type = tool_data["type"]
    cat = tool_data["category"]
    pain = tool_data["pain_point"]
    feat = tool_data["killer_feature"]
    url = tool_data["official_url"]
    score = tool_data["geek_score"]
    
    prompt = (
        f"你是一个拥有十几年玩机经验的硬核 PC 极客老哥。\n"
        f"请针对以下这款【解决恶心痛点的冷门神级工具】写一篇干货满满、直击灵魂的评测（绝无 AI 腔调，说人话，糙汉直球）：\n\n"
        f"【工具名称】：{name} ({t_type})\n"
        f"【所属领域】：{cat}\n"
        f"【解决的恶心痛点】：{pain}\n"
        f"【核心杀手级亮点】：{feat}\n"
        f"【官网/获取方式】：{url}\n\n"
        f"【撰写格式与调性规范】：\n"
        f"1. 标题必须有冲击力，20字以内（例如：《被流氓软件恶心吐了？这3MB单文件直接教它做人！》）；\n"
        f"2. 融入小黑盒专属表情代码：[cube_niubi]、[cube_le]、[cube_wunai]、[cube_shengqi]（每段最多1个，点在情绪上）；\n"
        f"3. 核心板块：\n"
        f"   - ⚡【恶心痛点】：开篇一句话痛骂用户平时遇到的反人类设定或大厂流氓行为；\n"
        f"   - 🔨【神仙解法】：这工具到底怎么一击必杀的？（原理解析：内存占用、单文件、离线安全）；\n"
        f"   - 📦【1分钟上手与避坑】：安装或配置时唯一需要注意的 1 个关键设置（别整复杂）；\n"
        f"   - 💬【老哥打分】：给出 10 分制打分，文末留获取路径与互动反响钩子；\n"
        f"4. 严禁出现'在当今数字化时代'、'不仅如此'、'总的来说'等 AI 八股文。\n"
        f"直接输出 Markdown 原文。"
    )
    
    payload = json.dumps({
        "model": MODEL_NAME,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 1500,
        "temperature": 0.65
    }).encode("utf-8")
    
    req = urllib.request.Request(
        GATEWAY_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {GATEWAY_KEY}"
        }
    )
    
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            msg = data.get("choices", [{}])[0].get("message", {})
            content = msg.get("content", "").strip()
            usage = data.get("usage", {})
            tokens = usage.get("total_tokens", 0)
            elapsed = round(time.time() - t0, 1)
            return content, tokens, elapsed
    except Exception as e:
        print(f"[-] AI 评测生成失败 ({name}): {e}")
        return None, 0, 0

# ==================== 3. 运行与输出 ====================

def run_radar():
    print("=" * 65)
    print("🛠️ 启动【冷门好用极客神级工具雷达】分析流水线")
    print(f"⏰ 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 引擎: {MODEL_NAME} @ {GATEWAY_URL}")
    print(f"📁 产出目录: {OUTPUT_DIR}")
    print("=" * 65)
    
    total = len(CURATED_TOOLS)
    all_reviews = []
    total_tokens = 0
    
    for i, tool in enumerate(CURATED_TOOLS, 1):
        name = tool["name"]
        print(f"\n[{i}/{total}] 🔍 正在深度剖析工具: {name} ({tool['category']}) ...")
        content, tokens, elapsed = generate_tool_review(tool)
        
        if content:
            total_tokens += tokens
            # 保存单独文件
            clean_name = name.lower().replace(" ", "_").replace("+", "plus")
            single_file = os.path.join(OUTPUT_DIR, f"{i:02d}_{clean_name}.md")
            with open(single_file, "w", encoding="utf-8") as f:
                f.write(content + f"\n\n---\n**官方获取/开源地址**: `{tool['official_url']}`\n")
                
            all_reviews.append(content)
            print(f"    [+] 评测生成完成！耗时: {elapsed}s | 消耗 Token: {tokens}")
            print(f"    [+] 保存至: {single_file}")
        else:
            print(f"    [-] 工具 {name} 评测失败。")
            
        time.sleep(1)
        
    # 合并成一篇长文大汇总（极其适合小黑盒长文）
    if all_reviews:
        summary_file = os.path.join(OUTPUT_DIR, "xiaoheihe_tools_collection.md")
        with open(summary_file, "w", encoding="utf-8") as sf:
            sf.write("# 💥 电脑卡成PPT、弹窗满天飞？这几款冷门神级小工具直接封神！\n\n")
            sf.write("大厂全家桶吃饱了撑的净搞恶心人操作？今天盘点 7 款自己天天在用、单文件免折腾、绝不偷隐私的极客神级小工具。[cube_niubi]\n\n")
            sf.write("\n\n---\n\n".join(all_reviews))
            sf.write("\n\n---\n你平时用过哪款？还有什么私藏的神级小工具？评论区交出来交流交流！[cube_tusiji]\n#电脑技巧 #软件推荐 #干货分享 #开源")
        print("\n" + "=" * 65)
        print(f"🎉 汇总长文推文已生成: {summary_file}")
        print(f"🔥 本次累计消耗 Token: {total_tokens}")
        print("=" * 65)

if __name__ == "__main__":
    run_radar()
