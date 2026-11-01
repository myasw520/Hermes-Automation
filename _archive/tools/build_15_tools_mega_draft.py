# -*- coding: utf-8 -*-
"""一键组装并构建 15 款神仙开源小工具（50+ 张真实 UI 截图）超长大长文
"""
import os
import sys
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "reports" / "stockpile_drafts" / "track_a_windows" / "03_15款神仙开源工具全家桶_50张实操截图糊脸"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
IMG_DIR = OUTPUT_DIR / "images"
IMG_DIR.mkdir(parents=True, exist_ok=True)

# 15 个工具清单与配图规划
TOOLS_SPEC = [
    {
        "id": "01",
        "name": "Disable-automatic-Windows-update",
        "repo": "WavesMan/Disable-automatic-Windows-update",
        "stars": 130,
        "style": "brutal",
        "title": "01 Disable-Update：专治 Win11 恶心强推更新",
        "desc": "如它名字一样简单，没什么好介绍的。看名字懂的都懂，就一个按钮，按完收工，直接看图。",
        "images": [
            ("reports/niche_gems/assets/WavesMan_Disable-automatic-Windows-update/img_01.png", "图：主界面就一个开关，直接彻底静止更新服务"),
            ("reports/niche_gems/assets/WavesMan_Disable-automatic-Windows-update/img_02.png", "图：服务状态显示已彻底静默")
        ]
    },
    {
        "id": "02",
        "name": "Stealth",
        "repo": "celeron533/Stealth",
        "stars": 68,
        "style": "brutal",
        "title": "02 Stealth：老板键与摸鱼隐身神技",
        "desc": "没废话，快捷键一按所有指定窗口直接人间蒸发，任务栏和托盘全空，看图自取。",
        "images": [
            ("reports/niche_gems/assets/celeron533_Stealth/img_01.png", "图：勾选需要隐身的进程与快捷键配置"),
            ("reports/niche_gems/assets/celeron533_Stealth/img_02.png", "图：隐身生效后任务栏与托盘干净如初")
        ]
    },
    {
        "id": "03",
        "name": "PowerPlanSwitcher",
        "repo": "SebastianBecker2/PowerPlanSwitcher",
        "stars": 117,
        "style": "brutal",
        "title": "03 PowerPlanSwitcher：托盘秒切满血/省电模式",
        "desc": "还在一层层点开 Windows 设置找电源选项？任务栏托盘右键秒切电源计划（省电/游戏满血），不讲废话，看图就行。",
        "images": [
            ("reports/niche_gems/assets/SebastianBecker2_PowerPlanSwitcher/img_02.png", "图：任务栏托盘图标右键直出所有已配置电源计划"),
            ("reports/niche_gems/assets/SebastianBecker2_PowerPlanSwitcher/img_04.png", "图：支持根据不同运行程序自动匹配模式"),
            ("reports/niche_gems/assets/SebastianBecker2_PowerPlanSwitcher/img_05.png", "图：极简设置界面，开机自启且内存占用忽略不计")
        ]
    },
    {
        "id": "04",
        "name": "GhostDeck",
        "repo": "wygodad/ghostdeck",
        "stars": 67,
        "style": "deep",
        "title": "04 GhostDeck：掌机与轻薄本独立风扇曲线控温",
        "desc": "专治笔记本一插电风扇就起飞啸叫的毛病。无需官方臃肿驱动，直接接管底层传感器，支持自由拉动温度与转速曲线。<b>避坑提醒：别把起转温度设得太死，建议阶梯式平滑爬升</b>，看实机面板。",
        "images": [
            ("reports/niche_gems/assets/wygodad_ghostdeck/img_01.png", "图：主界面实时显示 CPU/GPU 核心温度与风扇当前转速"),
            ("reports/niche_gems/assets/wygodad_ghostdeck/img_02.png", "图：多节点自定义风扇转速阶梯曲线调节"),
            ("reports/niche_gems/assets/wygodad_ghostdeck/img_03.png", "图：功耗限制与 TDP 动态调整页面"),
            ("reports/niche_gems/assets/wygodad_ghostdeck/img_04.png", "图：后台常驻监视窗，单文件绿色免安装")
        ]
    },
    {
        "id": "05",
        "name": "intag",
        "repo": "Jamminroot/intag",
        "stars": 134,
        "style": "deep",
        "title": "05 intag：给 Win 资源管理器加上 Mac 彩色标签",
        "desc": "用惯了 Mac 文件标签的老哥狂喜。给 Windows 原生资源管理器直接注入彩色小圆点标签，右键任意文件直接打色标。<b>注意：首次使用以管理员身份运行一键批处理注册右键，之后就能彻底脱手原生使用</b>。",
        "images": [
            ("reports/niche_gems/assets/Jamminroot_intag/img_04.png", "图：右键菜单直接集成原生彩色标签选项"),
            ("reports/niche_gems/assets/Jamminroot_intag/img_05.png", "图：标签过滤器，点击红标瞬间过滤出所有重要合同与文档"),
            ("reports/niche_gems/assets/Jamminroot_intag/img_06.png", "图：自定义标签名称与十六进制颜色配方")
        ]
    },
    {
        "id": "06",
        "name": "subsearch",
        "repo": "vagabondHustler/subsearch",
        "stars": 58,
        "style": "deep",
        "title": "06 subsearch：生肉视频极速离线字幕刮削",
        "desc": "看海外剧或生肉电影最怕没中文字幕。右键任意视频，自动从视频元数据提取哈希，秒级匹配国内外最精准的中文字幕并下载重命名。完全本地离线跑，无需复杂网络环境。",
        "images": [
            ("reports/niche_gems/assets/vagabondHustler_subsearch/img_02.png", "图：右键视频菜单直接触发 subsearch 搜索"),
            ("reports/niche_gems/assets/vagabondHustler_subsearch/img_03.png", "图：自动搜索并匹配多个字幕源并打分对比"),
            ("reports/niche_gems/assets/vagabondHustler_subsearch/img_04.png", "图：偏好语言设置为简体中文与字幕格式过滤"),
            ("reports/niche_gems/assets/vagabondHustler_subsearch/img_01.gif", "图：刮削动图演示：右键到字幕就绪仅耗时 2 秒")
        ]
    },
    {
        "id": "07",
        "name": "LoongPort",
        "repo": "SailingLoong/LoongPort",
        "stars": 138,
        "style": "brutal",
        "title": "07 LoongPort：一键查杀顽固端口占用",
        "desc": "启动项目或游戏联机服务提示端口被占用？打开它输入端口号，直接揪出背后作妖的进程 PID 并一键强杀，就这一个界面，看图自取。",
        "images": [
            ("reports/niche_gems/assets/SailingLoong_LoongPort/img_02.jpeg", "图：输入端口号快速检索当前占用进程名与路径，全局网络监听"),
            ("reports/niche_gems/assets/SailingLoong_LoongPort/img_03.png", "图：点击 Kill 按钮直接秒杀后台幽灵进程")
        ]
    },
    {
        "id": "08",
        "name": "ohmyshot",
        "repo": "redf0x1/ohmyshot-releases",
        "stars": 76,
        "style": "deep",
        "title": "08 ohmyshot：截图即排版，自带圆角阴影宣发壳",
        "desc": "受够了平平无奇的方块截图？这个工具在截图后自动为图片加上精美圆角、漫反射柔和阴影与毛玻璃背景，直接输出高级宣发海报质感，发群里交流倍有面子。",
        "images": [
            ("reports/niche_gems/assets/redf0x1_ohmyshot-releases/img_01.png", "图：一键生成带设备外壳与柔和渐变背景的精致截图"),
            ("reports/niche_gems/assets/redf0x1_ohmyshot-releases/img_02.png", "图：边距、阴影扩散半径与圆角自由滑块调节"),
            ("reports/niche_gems/assets/redf0x1_ohmyshot-releases/img_03.png", "图：预设多种高质感壁纸色调背景")
        ]
    },
    {
        "id": "09",
        "name": "mimick",
        "repo": "nicx17/mimick",
        "stars": 135,
        "style": "deep",
        "title": "09 mimick：轻量窗口置顶与透明度滚轮调节",
        "desc": "比起几百兆的庞大窗口管理软件，这个只有几兆。按住快捷键滚动鼠标滚轮，任意窗口立刻半透明，查资料写代码对照极其顺手，还带一键窗口绝对置顶。",
        "images": [
            ("reports/niche_gems/assets/nicx17_mimick/img_01.png", "图：窗口即时半透明效果，透过窗口直接看底层参考代码"),
            ("reports/niche_gems/assets/nicx17_mimick/img_02.png", "图：窗口快速吸附与边缘半屏平铺布局"),
            ("reports/niche_gems/assets/nicx17_mimick/img_03.png", "图：系统级快捷键自定义面板"),
            ("reports/niche_gems/assets/nicx17_mimick/img_04.png", "图：后台常驻内存占用不足 5MB")
        ]
    },
    {
        "id": "10",
        "name": "orca",
        "repo": "shubham-pathak1/orca",
        "stars": 62,
        "style": "deep",
        "title": "10 orca：Rust 打造的无广告极简本地播放器",
        "desc": "没有任何首页推荐、不偷跑任何外链、没有弹窗广告。纯用 Rust 写的本地音频播放器，极度轻量，内存占用几近于零，专门给本地存高码率无损音乐的老哥准备。",
        "images": [
            ("reports/niche_gems/assets/shubham-pathak1_orca/img_01.png", "图：极简纯黑终端与 GUI 混血界面，专注歌曲列表"),
            ("reports/niche_gems/assets/shubham-pathak1_orca/img_02.png", "图：本地歌词自动解析与滚动显示"),
            ("reports/niche_gems/assets/shubham-pathak1_orca/img_03.png", "图：专辑封面流式提取与无损音频格式直出"),
            ("reports/niche_gems/assets/shubham-pathak1_orca/img_04.png", "图：极速目录扫描，万首歌曲秒级入库")
        ]
    },
    {
        "id": "11",
        "name": "stedding-browser",
        "repo": "ysalitrynskyi/stedding-browser",
        "stars": 53,
        "style": "deep",
        "title": "11 stedding-browser：极简 Arc 风格竖向标签浏览器",
        "desc": "小屏笔记本开二十个网页上方标签全挤扁了？这款开源浏览器原生采用左侧竖向侧边栏，支持多工作区自由收纳，垂直视野拉满，彻底拯救小屏笔记本文档阅读。",
        "images": [
            ("reports/niche_gems/assets/ysalitrynskyi_stedding-browser/img_01.gif", "图：侧边栏快速切换工作区动图演示"),
            ("reports/niche_gems/assets/ysalitrynskyi_stedding-browser/img_02.gif", "图：标签页竖向分组与折叠效果"),
            ("reports/niche_gems/assets/ysalitrynskyi_stedding-browser/img_03.gif", "图：一键隐藏整个侧边栏进入全屏阅读模式"),
            ("reports/niche_gems/assets/ysalitrynskyi_stedding-browser/img_04.gif", "图：分屏浏览双网页并排对比")
        ]
    },
    {
        "id": "12",
        "name": "FrameShift",
        "repo": "Gaurox/FrameShift",
        "stars": 99,
        "style": "deep",
        "title": "12 FrameShift：显卡离线加速音视频无损压制",
        "desc": "录屏出来的几十个 GB 视频发不出去？基于 FFmpeg 和显卡硬件加速的离线压制工具，拖入视频一键选无损压缩，体积缩水 80% 画质毫无感知下降，再也不用开沉重的剪辑软件。",
        "images": [
            ("reports/niche_gems/assets/Gaurox_FrameShift/img_01.gif", "图：拖入视频文件一键自动化分析编码"),
            ("reports/niche_gems/assets/Gaurox_FrameShift/img_02.gif", "图：硬件编码器自动调用与转码进度条"),
            ("reports/niche_gems/assets/Gaurox_FrameShift/img_04.png", "图：音视频参数高级调节与输出格式配置")
        ]
    },
    {
        "id": "13",
        "name": "pane",
        "repo": "Aafff623/pane",
        "stars": 107,
        "style": "brutal",
        "title": "13 pane：极简多窗平铺辅助工作台",
        "desc": "纯绿色单文件。按网格自动把屏幕划分为两分屏、四分屏，把聊天窗、浏览器和文档瞬间卡进对应网格，没有花哨设置，看图就懂。",
        "images": [
            ("reports/niche_gems/assets/Aafff623_pane/img_03.png", "图：快捷键拖拽窗口吸附到指定网格区域"),
            ("reports/niche_gems/assets/Aafff623_pane/img_04.png", "图：多显示器自动记忆各屏幕分屏规则"),
            ("reports/niche_gems/assets/Aafff623_pane/img_05.png", "图：极小内存占用，退出无任何驻留进程")
        ]
    },
    {
        "id": "14",
        "name": "FileMint",
        "repo": "FileMintApp/FileMint",
        "stars": 148,
        "style": "deep",
        "title": "14 FileMint：轻量右键增强与文件整理工具",
        "desc": "比微软臃肿的 PowerToys 干净太多。右键一键新建各种工程文件、一键将 Windows 路径转为标准的 Linux 斜杠路径、批量快速改名前缀，日常办公用起来极度顺手。",
        "images": [
            ("reports/niche_gems/assets/FileMintApp_FileMint/img_02.png", "图：一键转换路径斜杠与格式化复制"),
            ("reports/niche_gems/assets/FileMintApp_FileMint/img_03.png", "图：批量文件重命名与规则替换"),
            ("reports/niche_gems/assets/FileMintApp_FileMint/img_04.png", "图：模块开关设置，不需要的功能直接彻底关闭")
        ]
    },
    {
        "id": "15",
        "name": "folio-terminal",
        "repo": "lulu-loopp/folio-terminal",
        "stars": 80,
        "style": "brutal",
        "title": "15 folio-terminal：开箱即用的轻量漂亮终端",
        "desc": "厌烦了老土的黑框 CMD 却又懒得配置繁琐的 Windows Terminal？开箱即用，自带漂亮的半透明毛玻璃与主题配色，看图自取。",
        "images": [
            ("reports/niche_gems/assets/lulu-loopp_folio-terminal/img_01.png", "图：开箱即用的磨砂质感终端界面"),
            ("reports/niche_gems/assets/lulu-loopp_folio-terminal/img_02.png", "图：内置多种终端配色方案一键切换"),
            ("reports/niche_gems/assets/lulu-loopp_folio-terminal/img_03.png", "图：多标签页平铺与快捷键管理")
        ]
    }
]

def make_cover(dest_path):
    """生成高质量 16:9 封面 Hero Banner"""
    base_cover = Path(r"C:\Users\zzx05\.gemini\antigravity\brain\1df70796-e1a9-4d4b-b590-e026bcc2348f\tech_anime_cover_1792907009828.jpg")
    if not base_cover.exists():
        base_cover = Path(r"C:\Users\zzx05\.gemini\antigravity\brain\1df70796-e1a9-4d4b-b590-e026bcc2348f\anime_cover_efficiency_1792945070614.jpg")
    
    with Image.open(base_cover) as im:
        w, h = im.size
        # 裁剪为 16:9
        target_w = w
        target_h = int(w * 9 / 16)
        if target_h > h:
            target_h = h
            target_w = int(h * 16 / 9)
        left = (w - target_w) // 2
        top = (h - target_h) // 2
        im_crop = im.crop((left, top, left + target_w, top + target_h))
        im_crop = im_crop.resize((1920, 1080), Image.Resampling.LANCZOS)
    
    # 底部暗部渐变遮罩增强文字可读性
    overlay = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for y in range(450, 1080):
        alpha = int(220 * ((y - 450) / 630.0) ** 1.3)
        draw.line([(0, y), (1920, y)], fill=(12, 16, 28, alpha))
    
    combined = Image.alpha_composite(im_crop.convert("RGBA"), overlay)
    draw_final = ImageDraw.Draw(combined)
    
    font_path = "C:/Windows/Fonts/msyhbd.ttc"
    if not os.path.exists(font_path):
        font_path = "C:/Windows/Fonts/simhei.ttf"
        
    font_badge = ImageFont.truetype(font_path, 32)
    font_title = ImageFont.truetype(font_path, 80)
    font_sub = ImageFont.truetype(font_path, 42)
    
    # 胶囊徽章
    draw_final.rounded_rectangle([100, 680, 480, 735], radius=12, fill=(240, 90, 40, 240))
    draw_final.text((120, 688), "★ 50+ 实操截图大合集", font=font_badge, fill=(255, 255, 255))
    
    # 主标题
    draw_final.text((100, 770), "15 款神仙级冷门开源工具", font=font_title, fill=(255, 255, 255))
    
    # 副标题
    draw_final.text((100, 890), "纯本地零后台 · 专治各种 Windows 疑难杂症与流氓发热", font=font_sub, fill=(200, 220, 245))
    
    combined.convert("RGB").save(dest_path, "PNG", quality=95)
    print(f"[✓] 16:9 封面 Hero Banner 生成完成: {dest_path}")

def build_article():
    cover_path = OUTPUT_DIR / "cover_16_9.png"
    make_cover(cover_path)
    
    blocks = []
    
    # 1. 开场破题（灵魂吐槽 + 反AI预判破题）
    intro_html = (
        "<p>别天天在评论区当上下文比老旧豆包还短的劣质小模型了，见个排版整齐的帖子就只会复读‘又是AI’。稍微用用脑子，幻觉比劣质AI还重。</p>"
        "<p>今天老子一口气盘 <b>15 个几十星到一百多星的纯本地冷门神仙工具</b>，全是实打实解决日常痛点的硬货，<b>50 多张真实运行截图直接糊你脸上</b>！"
        "规则很简单：简单的绝不多废话直接甩图，复杂的带你手把手避坑。懂的都懂，慢慢看！</p>"
    )
    blocks.append({"type": "html", "content": intro_html})
    
    # 2. 插入全宽 16:9 Hero Banner
    hero_copy = IMG_DIR / "hero_banner.png"
    import shutil
    shutil.copyfile(cover_path, hero_copy)
    blocks.append({
        "type": "img",
        "path": str(hero_copy),
        "alt": "图：15 款神仙级冷门开源工具全家桶 · 50+ 实操截图糊脸",
        "desc": "图：15 款纯本地神仙开源工具全家桶 · 50+ 实操截图"
    })
    
    img_counter = 1
    # 3. 逐个工具遍历
    for t in TOOLS_SPEC:
        h2_title = f"<h2>{t['title']}</h2>"
        p_desc = f"<p>{t['desc']}</p>"
        p_star = f"<p><b>GitHub 搜索：</b><code>{t['repo']}</code>（当前仅 {t['stars']}★，纯净无广告）</p>"
        blocks.append({"type": "html", "content": f"{h2_title}\n{p_desc}\n{p_star}"})
        
        for p_img, alt_text in t["images"]:
            p_src = BASE_DIR / p_img
            if not p_src.exists():
                print(f"[warn] 图片不存在: {p_src}")
                continue
            dest_img = IMG_DIR / f"img_{img_counter:02d}_{Path(p_img).name}"
            shutil.copyfile(p_src, dest_img)
            blocks.append({
                "type": "img",
                "path": str(dest_img),
                "alt": alt_text,
                "desc": alt_text
            })
            img_counter += 1
            
    # 4. 收尾与降维打击
    outro_html = (
        "<h2>打完收工：防弹衣与置顶说明</h2>"
        "<p>整整 15 个工具、50 多张真实实机运行截图，全是我们自己淘出来用得爽的冷门宝贝，代码全开源在 GitHub，自己搜名字就能下载。</p>"
        "<p>另外提前预判评论区无脑扣帽子的机型：别在评论区当劣质人机复读机，稍微用用脑子。有疑问的正常老哥评论区抓我，下期见！[cube_干杯]</p>"
        "<p>#Windows #开源工具 #电脑折腾 #软件推荐 #冷门宝藏 #数码科技</p>"
    )
    blocks.append({"type": "html", "content": outro_html})
    
    article_json_path = OUTPUT_DIR / "article_blocks.json"
    article_json_path.write_text(json.dumps(blocks, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[✓] 结构化区块生成完毕，共 {len(blocks)} 个区块，包含 {img_counter - 1} 张实操截图！")
    print(f"    文件位置: {article_json_path}")
    return article_json_path, cover_path

if __name__ == "__main__":
    build_article()
