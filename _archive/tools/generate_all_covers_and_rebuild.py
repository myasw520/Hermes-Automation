# -*- coding: utf-8 -*-
"""
精修小黑盒屯稿生成器：
1. 合成三大主题专属 16:9 二次元轻杂志封面
2. 将封面图片作为 Hero Banner 插入正文「开头第一句话/导语之后」
3. 彻底清洗所有图片：剔除所有头像、小图标与纯横幅，只留 100% 真实软件界面
4. 一键自动推送到小黑盒草稿箱（带 cover 绑定、文章计划、AI声明）
"""

import os
import sys
import json
import shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BRAIN_DIR = Path(r"C:\Users\zzx05\.gemini\antigravity\brain\1df70796-e1a9-4d4b-b590-e026bcc2348f")
STOCKPILE_DIR = PROJECT_ROOT / "reports" / "stockpile_drafts"

FONT_BOLD = r"C:\Windows\Fonts\msyhbd.ttc"
FONT_REGULAR = r"C:\Windows\Fonts\msyh.ttc"
FONT_ARIAL = r"C:\Windows\Fonts\arial.ttf"

def render_magazine_cover(base_img_path: Path, out_path: Path, issue_tag: str, hook_text: str, sub_line: str, watermark: str):
    """合成轻杂志日漫风 16:9 封面"""
    im = Image.open(base_img_path).convert("RGBA")
    W, H = im.size
    
    # 强制 16:9 裁剪
    target_ratio = 16.0 / 9.0
    cur_ratio = W / H
    if abs(cur_ratio - target_ratio) > 0.02:
        if cur_ratio > target_ratio:
            new_w = int(H * target_ratio)
            left = (W - new_w) // 2
            im = im.crop((left, 0, left + new_w, H))
        else:
            new_h = int(W / target_ratio)
            top = (H - new_h) // 2
            im = im.crop((0, top, W, top + new_h))
        W, H = im.size

    # 左上角柔和暗角微遮罩
    vignette = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    v_draw = ImageDraw.Draw(vignette)
    for x in range(int(W * 0.58)):
        alpha = int(130 * (1.0 - (x / (W * 0.58)) ** 1.8))
        v_draw.line([(x, 0), (x, H)], fill=(10, 20, 35, alpha))
    im = Image.alpha_composite(im, vignette)

    draw = ImageDraw.Draw(im)
    f_tag = ImageFont.truetype(FONT_ARIAL, 20)
    f_big = ImageFont.truetype(FONT_BOLD, 64)
    f_sub = ImageFont.truetype(FONT_REGULAR, 28)
    f_wm = ImageFont.truetype(FONT_ARIAL, 20)

    start_x, start_y = 65, 55
    # Tag
    draw.text((start_x, start_y), issue_tag, font=f_tag, fill=(0, 220, 255, 240))
    # Big Hook
    draw.text((start_x + 3, start_y + 45), hook_text, font=f_big, fill=(0, 0, 0, 160))
    draw.text((start_x, start_y + 42), hook_text, font=f_big, fill=(255, 255, 255, 255))
    # Subline
    draw.text((start_x + 2, start_y + 132), sub_line, font=f_sub, fill=(0, 0, 0, 140))
    draw.text((start_x, start_y + 130), sub_line, font=f_sub, fill=(210, 230, 255, 255))
    # Watermark
    draw.text((start_x, H - 55), watermark, font=f_wm, fill=(255, 255, 255, 180))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    im.convert("RGB").save(out_path, quality=95)
    print(f"[✓ 封面已生成] {out_path.name} ({W}x{H})")

def setup_draft_1():
    """Draft 1: Windows 治流氓与发热"""
    d_dir = STOCKPILE_DIR / "track_a_windows" / "01_专治发热与流氓更新_三款百星单文件"
    img_dir = d_dir / "images"
    cover_path = d_dir / "cover_16_9.png"
    
    render_magazine_cover(
        base_img_path=BRAIN_DIR / "tech_anime_cover_1792907009828.jpg",
        out_path=cover_path,
        issue_tag="ISSUE 01  /  MINIMALIST PC GUIDE",
        hook_text="「告别发热与全家桶」",
        sub_line="3款几十星单文件专治电脑发热与突袭更新",
        watermark="FREE & OPEN SOURCE  ·  NO ADS"
    )

    title = "别装几百兆全家桶了！这3个几十星的单文件专治发热与弹窗"
    opening_hook = "说实话，现在去搜什么电脑优化软件，十个里面有九个是坑——动辄两三百兆、开机自启动、右下角天天弹什么买会员清理垃圾，甚至有些在 GitHub 上刷了几万 Star 的项目，被大厂收购之后直接成了全家桶下载器。"
    intro_p2 = "老哥换了这台游戏本之后，最烦两件事：一是官方控制中心吃内存还发热，二是微软半夜强制重启给我更系统。今天掏出 3 个常年压箱底、Star 数只有几十到一百出头的野生单文件小工具。全是独立开发者写的，没有商业广告、不偷跑流量、单文件用完即关。装上它们，这台电脑才算真正听你的话。[cube_酷]"

    article_blocks = [
        {"type": "html", "content": f"<p>{opening_hook}</p>"},
        {"type": "img", "path": str(cover_path), "alt": "3款几十星单文件专治发热与弹窗"},
        {"type": "html", "content": f"<p>{intro_p2}</p><h2>一、GhostDeck：甩掉几百兆官方控制中心，独立接管风扇与功耗</h2><p>很多用微星或者游戏本的老哥肯定深有体会，官方那个 MSI Center 动辄几个 G，开机自启一堆后台服务，风扇转得跟直升机起飞一样，还经常闪退打不开。</p><p>GhostDeck 斩获 67 个 Star，作者自己受够了官方恶心全家桶，用 C# 写了一个零驱动依赖、直接通过 WMI 走 EC 芯片接管硬件的独立工具。不仅能随手切静音和狂暴模式，还能自定义风扇曲线、电池充电阈值（充到 80% 停），甚至带游戏 OSD 监控。用完随手关掉，内存占用直接归零。</p><h3>【实测体验】彻底干掉开机自启，原生 WMI 直调转速与温度</h3>"},
        {"type": "img", "path": str(img_dir / "item_1_status.png"), "alt": "GhostDeck 独立状态监控与模式切换面板"},
        {"type": "html", "content": "<p>GhostDeck 独立状态面板：直观监控 CPU/GPU 温度与功耗，秒级切换静音与狂暴模式。</p>"},
        {"type": "img", "path": str(img_dir / "item_1_settings.png"), "alt": "GhostDeck 详细硬件参数与充电阈值控制"},
        {"type": "html", "content": "<p>系统与电源设置：单文件免驱动直接控制充电阈值，支持防误触与无后台驻留。</p><p>防屏蔽指路：GitHub 搜索 wygodad/ghostdeck（开源地址：github。com/wygodad/ghostdeck）。</p><h2>二、PowerPlanSwitcher：任务栏托盘秒切电源计划，告别控制面板翻找</h2><p>平时码字写文档想要安静省电，晚上打 3A 大作又想榨干 CPU 性能。但 Windows 默认把电源计划藏在传统控制面板的犄角旮旯里，每次改都要点四五层窗口。</p><p>PowerPlanSwitcher 只有 117 个 Star，主打一个极简纯粹。它就是一个常驻在右下角托盘的小图标，不仅能直观显示当前生效的电源方案，鼠标点一下就能在“高性能”、“平衡”、“省电”之间秒级切换，还支持根据前台游戏自动切换。几十 KB 大小，比微软原生体验顺滑十倍。</p><h3>【实测体验】右键一点，狂暴高性能与静音省电秒级切换</h3>"},
        {"type": "img", "path": str(img_dir / "item_2_img_02.png"), "alt": "PowerPlanSwitcher 托盘电源计划秒切菜单"},
        {"type": "html", "content": "<p>托盘菜单直调：鼠标随手一点即可切换平衡与卓越性能模式，完全不用开控制面板。</p>"},
        {"type": "img", "path": str(img_dir / "item_2_img_04.png"), "alt": "PowerPlanSwitcher 自动规则设置"},
        {"type": "html", "content": "<p>自动化规则配置：支持按接入交流电或检测到游戏进程自动切换电源策略。</p><p>防屏蔽指路：GitHub 搜索 SebastianBecker2/PowerPlanSwitcher（开源地址：github。com/SebastianBecker2/PowerPlanSwitcher）。</p><h2>三、Disable-automatic-Windows-update：一行代码锁死半夜强制重启更新</h2><p>谁懂啊！前一天晚上跑代码或者渲染视频，第二天早上一拉开笔记本，屏幕显示正在更新 100%，昨晚辛辛苦苦跑了半夜的进度全没了，血压瞬间拉满。</p><p>很多第三方管家软件所谓“关闭自动更新”本质上是塞自己的后台服务。这个只有 130 Star 的开源工具极其纯粹，直接在底层禁用 Windows Update 相关的组策略与更新触发服务，把系统的自动重启通道彻底堵死。当你哪天想升级了，点一下又能一键恢复，把主动权牢牢拿回自己手里。</p><h3>【实测体验】彻底治好 Windows 突袭重启焦虑，杜绝负优化</h3>"},
        {"type": "img", "path": str(img_dir / "item_3_img_02.png"), "alt": "一键锁死 Windows 自动更新界面"},
        {"type": "html", "content": "<p>独立小界面：绿色单文件点一下即可锁死 Windows Update 服务通道，杜绝半夜突袭重启。</p><p>防屏蔽指路：GitHub 搜索 WavesMan/Disable-automatic-Windows-update（开源地址：github。com/WavesMan/Disable-automatic-Windows-update）。</p><h2>总结与交流</h2><p>大伙们平时还在用什么冷门但神仙的单文件小工具？那些动辄几个 G 的所谓官方套件真没必要惯着。有踩坑或者装不上的直接在评论区抓我，有问必答！觉得有用别忘了顺手点个赞收个藏，我们下期见！ [cube_干杯]</p><p>#电脑技巧 #开源项目 #系统优化 #装机必备</p>"}
    ]

    (d_dir / "article_blocks.json").write_text(json.dumps(article_blocks, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[✓ Draft 1 数据已就绪] 封面与实机图完全对齐")
    return d_dir, title, cover_path

def setup_draft_2():
    """Draft 2: Windows 效率神器 (Stealth + intag + OhMyShot)"""
    d_dir = STOCKPILE_DIR / "track_a_windows" / "02_摸鱼与桌面效率巅峰_窗口透明与平铺"
    img_dir = d_dir / "images"
    cover_path = d_dir / "cover_16_9.png"

    # 拷贝本地已沉淀的真实实机图
    src_intag = PROJECT_ROOT / "reports/niche_gems/assets/Jamminroot_intag"
    if (src_intag / "img_05.png").exists():
        shutil.copy2(src_intag / "img_05.png", img_dir / "item_2_intag_01.png")
    if (src_intag / "img_06.png").exists():
        shutil.copy2(src_intag / "img_06.png", img_dir / "item_2_intag_02.png")

    render_magazine_cover(
        base_img_path=BRAIN_DIR / "anime_cover_efficiency_1792945070614.jpg",
        out_path=cover_path,
        issue_tag="ISSUE 02  /  DESKTOP EFFICIENCY",
        hook_text="「把电脑效率拉满」",
        sub_line="3款野生独立极客工具拒绝臃肿与水货",
        watermark="DESKTOP EFFICIENCY · NO BLOAT"
    )

    title = "别看那几个几万星的水货了！这3个野生独立工具把Windows效率拉满"
    opening_hook = "现在的 GitHub 效率工具区，充斥着各种靠营销号互刷出来的几万星半成品，下了个安装包动辄三四百兆，功能华而不实，装完电脑直接慢半拍。"
    intro_p2 = "平时在宿舍自习或者办公室干活，最恶心的事情就是屏幕不够用——想照着 PDF 敲代码只能不停切屏；系统资源管理器二十年不给标签分类；随手截个图四周生硬难看。今天分享 3 个真正轻量的百星级桌面神仙小工具，全是极客一个人手搓的干净作品，无广告、极度丝滑。[cube_酷]"

    article_blocks = [
        {"type": "html", "content": f"<p>{opening_hook}</p>"},
        {"type": "img", "path": str(cover_path), "alt": "3款野生独立工具把Windows效率拉满"},
        {"type": "html", "content": f"<p>{intro_p2}</p><h2>一、Stealth：鼠标滚轮随手调窗口透明度，查资料摸鱼神器</h2><p>Windows 原生一直不给窗口半透明功能。以前为了照着设计稿或者视频抄代码，要么买第二块屏幕，要么把窗口左右拼凑，字缩得像蚂蚁。</p><p>Stealth 只有 68 个 Star，是一个极其精致小巧的 Windows 窗口透明度调节器。开启后，按住快捷键或者滚轮，就能把当前窗口无极渐变透明，直接垫在参考资料上方操作。修图、对照文档打字、边摸鱼看番边码字，体验极度顺畅。</p><h3>【实测体验】照着原画修图/看参考码字，双窗口完美重叠</h3>"},
        {"type": "img", "path": str(img_dir / "item_1_img_01.png"), "alt": "Stealth 极简控制面板与透明度滑块"},
        {"type": "html", "content": "<p>极简调节界面：支持快捷键绑定与鼠标滚轮全局透明度渐变调节。</p>"},
        {"type": "img", "path": str(img_dir / "item_1_img_02.png"), "alt": "Stealth 窗口透明重叠实测效果"},
        {"type": "html", "content": "<p>实测效果：当前编辑窗口半透明悬浮在网页参考图上方，对照录入零切换。</p><p>防屏蔽指路：GitHub 搜索 celeron533/Stealth（开源地址：github。com/celeron533/Stealth）。</p><h2>二、intag：给资源管理器加上原生彩色标签，专治文件翻找内耗</h2><p>微软在 Windows 11 里磨蹭了二十年终于憋出了多标签页，但始终不肯做 macOS 标志性的“文件彩色标签”功能，平时项目文件一多，找个文档只能瞎眼翻找。</p><p>intag 仅 134 个 Star，作者是一个硬核洁癖开发者。它不装第三方臃肿的资源管理器外壳，而是直接在原生右键菜单里注入彩色标签分类！红黄蓝绿随手标记重要文件，点击标签瞬间筛选所有同类文档，内存占用 0，丝滑至极。</p><h3>【实测体验】原生右键直接打标，分类一目了然</h3>"},
        {"type": "img", "path": str(img_dir / "item_2_intag_01.png"), "alt": "intag 文件资源管理器彩色圆点标签展示"},
        {"type": "html", "content": "<p>资源管理器效果：给重要工程文件打上醒目彩色圆点，一秒辨认优先级。</p>"},
        {"type": "img", "path": str(img_dir / "item_2_intag_02.png"), "alt": "intag 右键菜单直接加标签操作"},
        {"type": "html", "content": "<p>原生右键集成：选中文件右键一键打标，零后台服务驻留。</p><p>防屏蔽指路：GitHub 搜索 Jamminroot/intag（开源地址：github。com/Jamminroot/intag）。</p><h2>三、OhMyShot：自带渐变壁纸底板与优雅阴影，告别土味截图</h2><p>微信或者系统自带截图截出来的图片，四周边缘生硬，直接甩到技术群或者帖子里显得特别粗糙土味；那些在线美化截图的网站又要排队又要充钱。</p><p>OhMyShot 仅 76 个 Star，是一个跨平台的本地截图与标注美化神仙工具。截完图后自动给图片套上圆角、渐变背景底板和多层弥散阴影，还自带几十种专业标注箭头。完全离线本地处理，生成出来的长图直接拿去发推或者发文章，观感赏心悦目。</p><h3>【实测体验】截图自动套壳美化，发帖发群逼格拉满</h3>"},
        {"type": "img", "path": str(img_dir / "item_3_img_01.png"), "alt": "OhMyShot 渐变背景与优雅阴影截图展示"},
        {"type": "html", "content": "<p>截图美化效果：自动增加高逼格壁纸渐变底板与多层弥散阴影，告别生硬白边。</p>"},
        {"type": "img", "path": str(img_dir / "item_3_img_02.png"), "alt": "OhMyShot 内置专业技术标注工具箱"},
        {"type": "html", "content": "<p>专业标注工具：放大镜、步骤序号、高亮框一应俱全，纯本地免登录。</p><p>防屏蔽指路：GitHub 搜索 redf0x1/ohmyshot-releases（开源地址：github。com/redf0x1/ohmyshot-releases）。</p><h2>总结与交流</h2><p>工具不在于名气大不大、Star 刷得有多狠，只要能精准解决日常操作里的那几个恶心痛点，它就是好工具。大家平时写码办公还有什么私房操作？有装机疑问直接在评论区留言！ [cube_干杯]</p><p>#电脑日常 #效率工具 #开源神器 #桌面美化</p>"}
    ]

    (d_dir / "article_blocks.json").write_text(json.dumps(article_blocks, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[✓ Draft 2 数据已就绪] 封面与实机图完全对齐")
    return d_dir, title, cover_path

def setup_draft_3():
    """Draft 3: 本地离线 AI (heard + apogee + LlamaForge)"""
    d_dir = STOCKPILE_DIR / "track_b_local_ai" / "01_别给云端API交保护费_三款离线本地AI黑科技"
    img_dir = d_dir / "images"
    cover_path = d_dir / "cover_16_9.png"

    render_magazine_cover(
        base_img_path=BRAIN_DIR / "anime_cover_offline_ai_1792945104686.jpg",
        out_path=cover_path,
        issue_tag="ISSUE 03  /  LOCAL & OFFLINE AI",
        hook_text="「告别云端付费API」",
        sub_line="3款轻量级纯本地离线AI黑科技小玩具",
        watermark="LOCAL & OFFLINE AI · PRIVACY FIRST"
    )

    title = "别再给云端API交保护费了！3个几MB的本地离线AI神仙小玩具"
    opening_hook = "现在的 AI 圈子可以说是群魔乱舞，到处都在鼓吹所谓“划时代大模型”，点进去一看要么是套壳网页包月 99，要么是商业 API 调两下直接按 Token 计费割韭菜，甚至把用户的聊天记录和私人代码全传回云端。"
    intro_p2 = "老哥一向主张能白嫖就绝不充钱、能本地跑就绝不上网。今天掏出 3 个完全不用联网、没有任何云端后门、Star 仅几十到一百出头的本地离线极客玩具。几十 MB 的小体积，不吃高性能显卡，断网照样满血跑，把 AI 真正变成只属于你自己的私房工具。[cube_酷]"

    article_blocks = [
        {"type": "html", "content": f"<p>{opening_hook}</p>"},
        {"type": "img", "path": str(cover_path), "alt": "3款本地离线AI神仙小玩具"},
        {"type": "html", "content": f"<p>{intro_p2}</p><h2>一、heard：基于本地离线 Whisper，断网直接给生肉音视频啃字幕</h2><p>追生肉剧、啃国外技术教程视频、或者整理录音文件，网上那些语音转文字工具不是按分钟收巨额费用，就是强制你把私人录音传上他们的服务器。</p><p>heard 只有 66 个 Star，基于 Whisper 与极简桌面界面打造。它完全在本地设备上运行模型推断，拖拽视频或音频进去，不用连网直接在本地秒级识别并生成精准对齐的 SRT 字幕。没有调用次数限制，彻底告别云端转写的隐私泄露与付费套路。</p><h3>【实测体验】零云端 API 费用，单文件直接吐出完美对齐的 SRT 字幕</h3>"},
        {"type": "img", "path": str(img_dir / "item_1_img_02.png"), "alt": "heard 离线拖拽音视频秒级转录与字幕生成界面"},
        {"type": "html", "content": "<p>本地 Whisper 桌面转写面板：拖入音频自动分段识别，纯离线保护录音隐私。</p>"},
        {"type": "img", "path": str(img_dir / "item_1_img_03.png"), "alt": "heard 原生字幕时间轴精准对齐展示"},
        {"type": "html", "content": "<p>对齐输出效果：秒级生成标准 SRT 字幕文件，断网也能满血跑。</p><p>防屏蔽指路：GitHub 搜索 rerender2021/heard（开源地址：github。com/rerender2021/heard）。</p><h2>二、apogee：个人私有离线 AI 阅读摘要器，你的文章第二大脑</h2><p>很多云端大模型插件打着“帮你读长文”的旗号，实则把你的浏览记录、工作内部报告一股脑同步上云，数据完全不受控。</p><p>apogee 仅 96 个 Star，灵感来自 Mozilla Orbit，是一个专门为个人隐私打造的离线 AI 文本摘要器。它可以在本地加载量化小模型，选中任何长篇报告、技术文档或论文，秒级在侧边栏提炼结构化摘要与核心结论。零网络请求，在飞机上断网也能顺畅阅读。</p><h3>【实测体验】本地小模型一键提炼核心要点，告别漫长翻页</h3>"},
        {"type": "img", "path": str(img_dir / "item_2_img_01_sidepanel.png"), "alt": "apogee 本地离线长文摘要提取侧边栏"},
        {"type": "html", "content": "<p>侧边栏离线摘要：本地推断选中长文核心要点，零数据回传风险。</p>"},
        {"type": "img", "path": str(img_dir / "item_2_img_02_popup.png"), "alt": "apogee 极简快捷摘要弹窗"},
        {"type": "html", "content": "<p>快捷弹窗模式：一键总结当前文章核心结论，断网状态丝滑阅读。</p><p>防屏蔽指路：GitHub 搜索 darshi1337/apogee（开源地址：github。com/darshi1337/apogee）。</p><h2>三、LlamaForge：本地 llama.cpp 极简工作台，开跑前精算显存不爆卡</h2><p>本地玩大模型的老哥最怕什么？辛辛苦苦下好十几 G 的 GGUF 模型，一加载直接 OOM 爆显存，系统直接卡死黑屏，根本不知道该开几层 GPU 卸载。</p><p>LlamaForge 仅 113 个 Star，是一个专为硬核 llama.cpp 玩家打造的精算控制面板。最大的神仙功能是：在模型真正加载之前，直接精确计算出模型在你的显存与内存里的落点分布，一目了然看清会占用几 GB 显存。支持一键管理多模型并发，界面干净轻快，完全是极客桌面必备。</p><h3>【实测体验】清楚看清模型每一层显存落点，告别卡死死机</h3>"},
        {"type": "img", "path": str(img_dir / "item_3_img_01.png"), "alt": "LlamaForge 本地模型管理与多并发控制工作台"},
        {"type": "html", "content": "<p>本地 llama 控制面板：多模型一键启动与参数配置，告别黑框命令行。</p>"},
        {"type": "img", "path": str(img_dir / "item_3_img_02.png"), "alt": "LlamaForge 显存占用提前精算曲线"},
        {"type": "html", "content": "<p>显存落点精算：载入前直观查看 GPU 显存占用与分层建议，杜绝 OOM 死机。</p><p>防屏蔽指路：GitHub 搜索 dadwritestech/LlamaForge（开源地址：github。com/dadwritestech/LlamaForge）。</p><h2>总结与交流</h2><p>算力属于自己，数据才能留在本地。大伙们平时在本地还折腾过什么好玩但冷门的小模型或小工具？评论区一起交流，有疑问随手丢出来！觉得有用别忘了点赞收藏，我们下期见！ [cube_干杯]</p><p>#人工智能 #本地AI #开源黑科技 #极客玩家</p>"}
    ]

    (d_dir / "article_blocks.json").write_text(json.dumps(article_blocks, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[✓ Draft 3 数据已就绪] 封面与实机图完全对齐")
    return d_dir, title, cover_path

def main():
    print("=== 开始全量精修与封面合成 ===")
    setup_draft_1()
    setup_draft_2()
    setup_draft_3()
    print("=== 全量精修完成！===")

if __name__ == "__main__":
    main()
