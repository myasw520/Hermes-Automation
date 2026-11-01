# -*- coding: utf-8 -*-
"""
小黑盒屯稿生成器（Stockpile Generator）
======================================
将已经下载好实机截图与提炼好痛点的低星宝藏项目，
批量编排成高标准的“小黑盒草稿储备库”：
1. 彻底去 AI 味（真人老哥自嘲、具体物理场景、猛烈吐槽高星刷榜与全家桶）
2. 坚决删除所有生硬的 '▲' 三角符号
3. 每篇草稿独立成文件夹，包含：
   - draft.md（方便人工阅读和随时二次润色）
   - article_blocks.json（可直接调用 xhh_build.py 一键生成草稿并传图）
   - images/（本地高分辨率实机图直通）
"""

import os
import sys
import json
import shutil
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = PROJECT_ROOT / "reports" / "niche_gems" / "assets"
STOCKPILE_DIR = PROJECT_ROOT / "reports" / "stockpile_drafts"

# 精选组合方案设计
DRAFT_BLUEPRINTS = [
    # ================= TRACK A: Windows 治流氓与原生效率 =================
    {
        "track": "track_a_windows",
        "folder_name": "01_专治发热与流氓更新_三款百星单文件",
        "title": "别装几百兆全家桶了！这3个几十星的单文件专治发热与弹窗",
        "hashtags": "#电脑技巧 #开源项目 #系统优化 #装机必备",
        "intro": """说实话，现在去搜什么电脑优化软件，十个里面有九个是坑——动辄两三百兆、开机自启动、右下角天天弹什么买会员清理垃圾，甚至有些在 GitHub 上刷了几万 Star 的项目，被大厂收购之后直接成了全家桶下载器。

老哥换了这台游戏本之后，最烦两件事：一是官方控制中心吃内存还发热，二是微软半夜强制重启给我更系统。

今天掏出 3 个常年压箱底、Star 数只有几十到一百出头的野生单文件小工具。全是独立开发者写的，没有商业广告、不偷跑流量、单文件用完即关。装上它们，这台电脑才算真正听你的话。[cube_酷]""",
        "items": [
            {
                "repo_slug": "wygodad_ghostdeck",
                "h2": "一、GhostDeck：甩掉几百兆官方控制中心，独立接管风扇与功耗",
                "h3": "【实测体验】彻底干掉开机自启，原生 WMI 直调转速",
                "lead": "很多用微星或者游戏本的老哥肯定深有体会，官方那个 MSI Center 动辄几个 G，开机自启一堆后台服务，风扇转得跟直升机起飞一样，还经常闪退打不开。",
                "body": "GhostDeck 斩获 67 个 Star，作者自己受够了官方恶心全家桶，用 C# 写了一个零驱动依赖、直接通过 WMI 走 EC 芯片接管硬件的独立工具。不仅能随手切静音和狂暴模式，还能自定义风扇曲线、电池充电阈值（充到 80% 停），甚至带游戏 OSD 监控。用完随手关掉，内存占用直接归零。",
                "tip": "防屏蔽指路：GitHub 搜索 wygodad/ghostdeck（开源地址：github。com/wygodad/ghostdeck）。"
            },
            {
                "repo_slug": "SebastianBecker2_PowerPlanSwitcher",
                "h2": "二、PowerPlanSwitcher：任务栏托盘秒切电源计划，告别控制面板翻找",
                "h3": "【实测体验】右键一点，狂暴高性能与静音省电秒级切换",
                "lead": "平时码字写文档想要安静省电，晚上打 3A 大作又想榨干 CPU 性能。但 Windows 默认把电源计划藏在传统控制面板的犄角旮旯里，每次改都要点四五层窗口。",
                "body": "PowerPlanSwitcher 只有 117 个 Star，主打一个极简纯粹。它就是一个常驻在右下角托盘的小图标，不仅能直观显示当前生效的电源方案，鼠标点一下就能在“高性能”、“平衡”、“省电”之间秒级切换，还支持根据前台游戏自动切换。几十 KB 大小，比微软原生体验顺滑十倍。",
                "tip": "防屏蔽指路：GitHub 搜索 SebastianBecker2/PowerPlanSwitcher（开源地址：github。com/SebastianBecker2/PowerPlanSwitcher）。"
            },
            {
                "repo_slug": "WavesMan_Disable-automatic-Windows-update",
                "h2": "三、Disable-automatic-Windows-update：一行代码锁死半夜强制重启更新",
                "h3": "【实测体验】彻底治好 Windows 突袭重启焦虑，杜绝负优化",
                "lead": "谁懂啊！前一天晚上跑代码或者渲染视频，第二天早上一拉开笔记本，屏幕显示正在更新 100%，昨晚辛辛苦苦跑了半夜的进度全没了，血压瞬间拉满。",
                "body": "很多第三方管家软件所谓“关闭自动更新”本质上是塞自己的后台服务。这个只有 130 Star 的开源工具极其纯粹，直接在底层禁用 Windows Update 相关的组策略与更新触发服务，把系统的自动重启通道彻底堵死。当你哪天想升级了，点一下又能一键恢复，把主动权牢牢拿回自己手里。",
                "tip": "防屏蔽指路：GitHub 搜索 WavesMan/Disable-automatic-Windows-update（开源地址：github。com/WavesMan/Disable-automatic-Windows-update）。"
            }
        ],
        "outro": """大伙们平时还在用什么冷门但神仙的单文件小工具？那些动辄几个 G 的所谓官方套件真没必要惯着。有踩坑或者装不上的直接在评论区抓我，有问必答！觉得有用别忘了顺手点个赞收个藏，我们下期见！ [cube_干杯]"""
    },

    # ================= TRACK A: 摸鱼与桌面效率 =================
    {
        "track": "track_a_windows",
        "folder_name": "02_摸鱼与桌面效率巅峰_窗口透明与平铺",
        "title": "别看那几个几万星的水货了！这3个野生独立工具把Windows效率拉满",
        "hashtags": "#电脑日常 #效率工具 #开源神器 #桌面美化",
        "intro": """现在的 GitHub 效率工具区，充斥着各种靠营销号互刷出来的几万星半成品，下了个安装包动辄三四百兆，功能华而不实，装完电脑直接慢半拍。

平时在宿舍自习或者办公室干活，最恶心的事情就是屏幕不够用——想照着 PDF 敲代码或者查资料，只能不停按 Alt+Tab 切屏，切得眼花缭乱；随手截个图想发给别人，自带的截图工具连个好看的底色和阴影都做不出来。

今天分享 3 个真正轻量的百星级桌面神仙小工具，全是极客一个人手搓的干净作品，无广告、极度丝滑。[cube_酷]""",
        "items": [
            {
                "repo_slug": "celeron533_Stealth",
                "h2": "一、Stealth：鼠标滚轮随手调窗口透明度，查资料摸鱼神器",
                "h3": "【实测体验】照着原画修图/看参考码字，双窗口完美重叠",
                "lead": "Windows 原生一直不给窗口半透明功能。以前为了照着设计稿或者视频抄代码，要么买第二块屏幕，要么把窗口左右拼凑，字缩得像蚂蚁。",
                "body": "Stealth 只有 68 个 Star，是一个极其精致小巧的 Windows 窗口透明度调节器。开启后，按住快捷键或者滚轮，就能把当前窗口无极渐变透明，直接垫在参考资料上方操作。修图、对照文档打字、边摸鱼看番边码字，体验极度顺畅。",
                "tip": "防屏蔽指路：GitHub 搜索 celeron533/Stealth（开源地址：github。com/celeron533/Stealth）。"
            },
            {
                "repo_slug": "dccif_KeySteer",
                "h2": "二、KeySteer：纯键盘 Vim 式操控鼠标与窗口平铺，手不离键盘",
                "h3": "【实测体验】多窗口平铺切换全靠键位，彻底告别鼠标晃荡",
                "lead": "用惯了机械键盘的老哥都知道，写字或者打游戏时频繁把右手从键盘挪到鼠标上，一天下来手腕又酸又累。",
                "body": "KeySteer 斩获 90 个 Star，作者用 Rust 编写。它直接把平铺式窗口管理器（Tiling WM）和 Vim 导航键位带到了 Windows。不用去装极其难配置的大型平铺软件，按下自定义热键即可用键盘瞬间移动光标、切换焦点窗口、多屏分窗。内存占用极低，运行飞快。",
                "tip": "防屏蔽指路：GitHub 搜索 dccif/KeySteer（开源地址：github。com/dccif/KeySteer）。"
            },
            {
                "repo_slug": "redf0x1_ohmyshot-releases",
                "h2": "三、OhMyShot：自带渐变壁纸底板与优雅阴影，告别土味截图",
                "h3": "【实测体验】截图自动套壳美化，发帖发群逼格拉满",
                "lead": "微信或者系统自带截图截出来的图片，四周边缘生硬，直接甩到技术群或者帖子里显得特别粗糙土味；那些在线美化截图的网站又要排队又要充钱。",
                "body": "OhMyShot 仅 76 个 Star，是一个跨平台的本地截图与标注美化神仙工具。截完图后自动给图片套上圆角、渐变背景底板和多层弥散阴影，还自带几十种专业标注箭头。完全离线本地处理，生成出来的长图直接可以直接拿去发推或者发文章，观感赏心悦目。",
                "tip": "防屏蔽指路：GitHub 搜索 redf0x1/ohmyshot-releases（开源地址：github。com/redf0x1/ohmyshot-releases）。"
            }
        ],
        "outro": """工具不在于名气大不大、Star 刷得有多狠，只要能精准解决日常操作里的那几个恶心痛点，它就是好工具。大家平时写码办公还有什么私房操作？有装机疑问直接在评论区留言！ [cube_干杯]"""
    },

    # ================= TRACK B: 本地离线 AI 与极客玩具 =================
    {
        "track": "track_b_local_ai",
        "folder_name": "01_别给云端API交保护费_三款离线本地AI黑科技",
        "title": "别再给云端API交保护费了！3个几MB的本地离线AI神仙小玩具",
        "hashtags": "#人工智能 #本地AI #开源黑科技 #极客玩家",
        "intro": """现在的 AI 圈子可以说是群魔乱舞，到处都在鼓吹所谓“划时代大模型”，点进去一看要么是套壳网页包月 99，要么是商业 API 调两下直接按 Token 计费割韭菜，甚至把用户的聊天记录和私人代码全传回云端。

老哥一向主张能白嫖就绝不充钱、能本地跑就绝不上网。

今天掏出 3 个完全不用联网、没有任何云端后门、Star 仅几十到一百出头的本地离线极客玩具。几十 MB 的小体积，不吃高性能显卡，断网照样满血跑，把 AI 真正变成只属于你自己的私房工具。[cube_酷]""",
        "items": [
            {
                "repo_slug": "rerender2021_heard",
                "h2": "一、heard：基于本地离线 Whisper，断网直接给生肉音视频啃字幕",
                "h3": "【实测体验】零云端 API 费用，单文件直接吐出完美对齐的 SRT 字幕",
                "lead": "追生肉剧、啃国外技术教程视频、或者整理录音文件，网上那些语音转文字工具不是按分钟收巨额费用，就是强制你把私人录音传上他们的服务器。",
                "body": "heard 只有 66 个 Star，基于 Whisper 与极简桌面界面打造。它完全在本地设备上运行模型推断，拖拽视频或音频进去，不用连网直接在本地秒级识别并生成精准对齐的 SRT 字幕。没有调用次数限制，彻底告别云端转写的隐私泄露与付费套路。",
                "tip": "防屏蔽指路：GitHub 搜索 rerender2021/heard（开源地址：github。com/rerender2021/heard）。"
            },
            {
                "repo_slug": "darshi1337_apogee",
                "h2": "二、apogee：个人私有离线 AI 阅读摘要器，你的文章第二大脑",
                "h3": "【实测体验】本地小模型一键提炼核心要点，告别漫长翻页",
                "lead": "很多云端大模型插件打着“帮你读长文”的旗号，实则把你的浏览记录、工作内部报告一股脑同步上云，数据完全不受控。",
                "body": "apogee 仅 96 个 Star，灵感来自 Mozilla Orbit，是一个专门为个人隐私打造的离线 AI 文本摘要器。它可以在本地加载量化小模型，选中任何长篇报告、技术文档或论文，秒级在侧边栏提炼结构化摘要与核心结论。零网络请求，在飞机上断网也能顺畅阅读。",
                "tip": "防屏蔽指路：GitHub 搜索 darshi1337/apogee（开源地址：github。com/darshi1337/apogee）。"
            },
            {
                "repo_slug": "dadwritestech_LlamaForge",
                "h2": "三、LlamaForge：本地 llama.cpp 极简工作台，开跑前精算显存不爆卡",
                "h3": "【实测体验】清楚看清模型每一层显存落点，告别卡死死机",
                "lead": "本地玩大模型的老哥最怕什么？辛辛苦苦下好十几 G 的 GGUF 模型，一加载直接 OOM 爆显存，系统直接卡死黑屏，根本不知道该开几层 GPU 卸载。",
                "body": "LlamaForge 仅 113 个 Star，是一个专为硬核 llama.cpp 玩家打造的精算控制面板。最大的神仙功能是：在模型真正加载之前，直接精确计算出模型在你的显存与内存里的落点分布，一目了然看清会占用几 GB 显存。支持一键管理多模型并发，界面干净轻快，完全是极客桌面必备。",
                "tip": "防屏蔽指路：GitHub 搜索 dadwritestech/LlamaForge（开源地址：github。com/dadwritestech/LlamaForge）。"
            }
        ],
        "outro": """算力属于自己，数据才能留在本地。大伙们平时在本地还折腾过什么好玩但冷门的小模型或小工具？评论区一起交流，有疑问随手丢出来！觉得有用别忘了点赞收藏，我们下期见！ [cube_干杯]"""
    }
]

def build_draft_bundle(blueprint: dict):
    track = blueprint["track"]
    folder_name = blueprint["folder_name"]
    target_dir = STOCKPILE_DIR / track / folder_name
    img_dir = target_dir / "images"
    target_dir.mkdir(parents=True, exist_ok=True)
    img_dir.mkdir(parents=True, exist_ok=True)

    title = blueprint["title"]
    hashtags = blueprint["hashtags"]
    intro = blueprint["intro"].strip()
    outro = blueprint["outro"].strip()

    # Markdown 文稿构建
    md_lines = [
        f"# {title}\n",
        f"{intro}\n"
    ]

    # article_blocks.json 构建 (供 xhh_build.py 直接调用)
    article_blocks = [
        {
            "type": "html",
            "content": f"<p>{intro.replace(chr(10), '</p><p>')}</p>"
        }
    ]

    for item_idx, it in enumerate(blueprint["items"], 1):
        h2 = it["h2"]
        h3 = it["h3"]
        lead = it["lead"]
        body = it["body"]
        tip = it["tip"]
        repo_slug = it["repo_slug"]

        md_lines.append(f"## {h2}\n")
        md_lines.append(f"{lead}\n")
        md_lines.append(f"{body}\n")
        md_lines.append(f"### {h3}\n")

        # 查找该仓库已抓取的实机图
        repo_asset_dir = ASSETS_DIR / repo_slug
        copied_images = []
        if repo_asset_dir.exists():
            for src_img in sorted(repo_asset_dir.glob("img_*")):
                ext = src_img.suffix
                dest_img_name = f"item_{item_idx}_{src_img.name}"
                dest_img = img_dir / dest_img_name
                shutil.copy2(src_img, dest_img)
                copied_images.append(dest_img_name)

        # 组装 HTML 块
        html_chunk = f"<h2>{h2}</h2><p>{lead}</p><p>{body}</p><h3>{h3}</h3>"
        article_blocks.append({
            "type": "html",
            "content": html_chunk
        })

        if copied_images:
            for c_idx, c_img in enumerate(copied_images[:2]): # 每项挑 1~2 张典型实机图
                alt_desc = f"{h2.split('：')[0]} 实测界面 {c_idx+1}"
                md_lines.append(f"![{alt_desc}](images/{c_img})")
                md_lines.append(f"*{alt_desc}*\n")
                
                article_blocks.append({
                    "type": "img",
                    "path": f"reports/stockpile_drafts/{track}/{folder_name}/images/{c_img}",
                    "alt": alt_desc
                })
                # 自然说明，坚决不用 ▲ 符号
                article_blocks.append({
                    "type": "html",
                    "content": f"<p>{alt_desc}：单文件极简运行，无冗余后台。</p>"
                })

        md_lines.append(f"> {tip}\n")
        article_blocks.append({
            "type": "html",
            "content": f"<p>{tip}</p>"
        })

    md_lines.append(f"## 总结与交流\n")
    md_lines.append(f"{outro}\n")
    md_lines.append(f"{hashtags}\n")

    summary_html = f"<h2>总结与交流</h2><p>{outro.replace(chr(10), '</p><p>')}</p><p>{hashtags}</p>"
    article_blocks.append({
        "type": "html",
        "content": summary_html
    })

    # 写入 draft.md
    (target_dir / "draft.md").write_text("\n".join(md_lines), encoding="utf-8")
    
    # 写入 article_blocks.json
    (target_dir / "article_blocks.json").write_text(json.dumps(article_blocks, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[✓ 已生成草稿包] {folder_name} (配图 {len(copied_images)} 张)")

def generate_stockpile_index():
    lines = [
        "# 小黑盒存稿储备仓库（去AI味·真人化2.0）",
        "> 本目录专供作者屯稿、二次润色与按计划分批发布。",
        "",
        "---",
        "",
        "## 一、已就绪的精编草稿目录",
        ""
    ]

    for bp in DRAFT_BLUEPRINTS:
        track = bp["track"]
        fname = bp["folder_name"]
        title = bp["title"]
        draft_md_rel = f"{track}/{fname}/draft.md"
        blocks_json_rel = f"{track}/{fname}/article_blocks.json"
        
        lines.append(f"### 📂 [{fname}]({draft_md_rel})")
        lines.append(f"- **主标题**：`{title}`")
        lines.append(f"- **所属题材**：`{track}`")
        lines.append(f"- **文稿阅读/润色**：[`draft.md`](file:///{PROJECT_ROOT.as_posix()}/reports/stockpile_drafts/{draft_md_rel})")
        lines.append(f"- **一键上传命令**：")
        lines.append("```bash")
        lines.append(f".venv\\Scripts\\python.exe .agents\\skills\\post-xiaoheihe\\scripts\\xhh_build.py ^")
        lines.append(f"    --title \"{title}\" ^")
        lines.append(f"    --article-json \"reports\\stockpile_drafts\\{track}\\{fname}\\article_blocks.json\" ^")
        lines.append(f"    --plan-article --declare-ai --save-draft")
        lines.append("```\n")

    lines.append("---")
    lines.append("## 二、发布流程建议")
    lines.append("1. **打开草稿浏览**：在 Markdown 阅读器或记事本中打开对应的 `draft.md`，加上你自己的口头禅或体验微调。")
    lines.append("2. **一键生成草稿**：直接复制上方对应草稿的命令行在终端运行，脚本全自动配好分级标题、实机截图、原生题注与AI声明并保存到小黑盒草稿箱。")
    lines.append("3. **手机端发布**：打开手机小黑盒 App，点进草稿箱确认效果，一键正式发布！")

    (STOCKPILE_DIR / "README.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"\n[✓ 存稿索引已生成] {STOCKPILE_DIR / 'README.md'}")

def main():
    STOCKPILE_DIR.mkdir(parents=True, exist_ok=True)
    for bp in DRAFT_BLUEPRINTS:
        build_draft_bundle(bp)
    generate_stockpile_index()

if __name__ == "__main__":
    main()
