# -*- coding: utf-8 -*-
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
import sys

sys.path.insert(0, r"c:\Users\zzx05\Hermes-Automation\.agents\skills\post-xiaoheihe\scripts")
from xhh_common import connect, find_editor_page, log, EDITOR_ARTICLE, EDITOR_TITLE

BASE_IMG_DIR = Path(r"reports\practical_tools\drafts_ready\draft_1_assets\images")

# Structured sections with Markdown H2 (#) and H3 (##) for rich visual hierarchy
SECTIONS = [
    {
        "h2": "# 一、LocalSend：彻底戒掉微信传文件焦虑，内网满速飞传",
        "intro_p": "先来对号入座，你平时在手机和电脑之间倒腾文件，是不是总被恶心：辛辛苦苦修好的 4K 壁纸发到手机直接压成 480P 马赛克；传个 1G 视频进度条像乌龟爬；插数据线弹一堆全家桶助手。\n\nLocalSend 在 GitHub 狂砍 9.5 万+ Star，说白了它就是一个开源跨平台版的 AirDrop。走家庭局域网，数据根本不出路由器！",
        "sub_1": "## 核心优势：开箱即用与跨端秒连",
        "imgs": [
            ("01_localsend_main.png", "LocalSend 电脑端主界面", "▲ 电脑端主界面：极简无广告，开箱即用，断网也能互传"),
            ("02_localsend_mobile.png", "手机端局域网设备发现", "▲ 手机端秒识别局域网设备：连同一个 Wi-Fi 自动发现电脑与平板"),
        ],
        "sub_2": "## 安全与隐私：本地端到端加密",
        "imgs_2": [
            ("03_localsend_settings.png", "本地端到端加密设置", "▲ 本地端到端加密：走 HTTPS 局域网加密，告别微信压缩与云端泄露风险")
        ],
        "outro": "防屏蔽指路：GitHub 搜索 localsend/localsend（开源地址：github。com/localsend/localsend）。"
    },
    {
        "h2": "# 二、ContextMenuManager：2MB 绿色单文件，一键净化右键全家桶",
        "intro_p": "新电脑用上几个月，桌面点个鼠标右键是不是要卡两秒？满屏都是各类流氓软件强行塞进来的私货菜单，密密麻麻看着就高血压。\n\nContextMenuManager 只有区区 2MB，绿色免安装单文件，国内硬核作者打造，专治 Windows 右键烂摊子。",
        "sub_1": "## 功能一览：分类梳理与秒级开关",
        "imgs": [
            ("04_contextmenu_clean.png", "ContextMenuManager 主界面", "▲ 主界面清晰分类：梳理所有右键项，随手一点开关立即禁用"),
            ("05_contextmenu_details.png", "右键注册表与残留项清理", "▲ 精准定位注册表项：支持查看关联路径，彻底灰飞烟灭卸载残留菜单"),
        ],
        "sub_2": "## 深度扩展：全场景右键管理",
        "imgs_2": [
            ("06_contextmenu_rules.png", "多场景扩展与新建项管理", "▲ 多场景扩展管理：IE/Edge 扩展、发送到、新建项全维度清理，内存占用 0")
        ],
        "outro": "防屏蔽指路：GitHub 搜索 BluePointLilac/ContextMenuManager（开源地址：github。com/BluePointLilac/ContextMenuManager）。"
    },
    {
        "h2": "# 三、QuickLook：空格键按一下，0 秒预览一切文件",
        "intro_p": "用过 Mac 的老哥都知道那个“按空格预览”有多爽，而 Windows 默认看个压缩包或者代码都要等大型软件转圈。\n\nQuickLook 斩获 2.5 万+ Star，直接把 Mac 这一神仙级体验 100% 带给了 Windows！不用解压、不用等软件启动，敲一下空格键直接在屏幕正中央弹出超清大图或文件目录。",
        "sub_1": "## 实测体验：压缩包免解压秒开",
        "imgs": [
            ("07_quicklook_zip.png", "QuickLook 空格键预览压缩包", "▲ 空格键秒预览压缩包内部：不用解压，直接看清所有文件层级"),
        ],
        "sub_2": "## 全格式支持：图片与代码无损高亮",
        "imgs_2": [
            ("08_quicklook_image.png", "高清单反大图秒级无损预览", "▲ 高清单反大图秒级渲染：敲空格瞬间全屏预览，支持无级滚轮缩放"),
            ("09_quicklook_code.png", "代码与 Markdown 高亮预览", "▲ 代码与文本高亮预览：对 JSON、Markdown、代码文件提供原生高亮预览")
        ],
        "outro": "防屏蔽指路：GitHub 搜索 QL-Win/QuickLook（开源地址：github。com/QL-Win/QuickLook，微软商店也能直接搜到）。"
    }
]

FINAL_SUMMARY = """老实说，咱们用 Windows 这么多年，受够了各种大厂全家桶打着“优化”的旗号反向塞流氓弹窗。这 3 个开源小工具是我换了 3 台电脑依然第一时间必装的：

• LocalSend（~30MB）：手机电脑跨端免登满速互传，传完即可退出；
• ContextMenuManager（2MB）：一键净化右键菜单卡顿与流氓残留，纯单文件用完即关；
• QuickLook（~50MB）：键盘空格键 0 秒预览任何文件，静默驻留内存仅十几MB。

大伙们平时还在用什么冷门但封神的小工具？有踩坑或者装不上的直接在评论区抓我，有问必答！觉得有用别忘了顺手点个赞收个藏，我们下期见！ [cube_干杯]"""

HASHTAGS = "#电脑软件 #数码科技 #开源项目 #装机推荐"

async def insert_img_with_alt(page, img_path, alt_text, body_caption):
    """Insert image, immediately fill its .article__image-desc-input, and add body caption."""
    await page.locator(".editor-menu-image").first.click()
    await page.wait_for_timeout(800)
    
    async with page.expect_file_chooser(timeout=15000) as fc_info:
        await page.locator(".editor-image-wrapper__box.upload").first.click()
    file_chooser = await fc_info.value
    await file_chooser.set_files(img_path)
    
    # Wait for thumbnail upload
    for _ in range(30):
        await page.wait_for_timeout(600)
        ready = await page.evaluate("""() => {
            const imgs = document.querySelectorAll('.editor-image-wrapper__box-image img');
            if (!imgs.length) return false;
            const last = imgs[imgs.length - 1];
            return last.complete && last.naturalWidth > 0;
        }""")
        if ready:
            break
            
    await page.get_by_text("确定", exact=True).first.click()
    await page.wait_for_timeout(1500)
    
    # 1. Fill native alt description
    inputs = page.locator(".article__image-desc-input")
    cnt = await inputs.count()
    if cnt > 0:
        inp = inputs.nth(cnt - 1)
        await inp.focus()
        await page.wait_for_timeout(200)
        is_active = await page.evaluate("() => document.activeElement.classList.contains('article__image-desc-input')")
        if is_active:
            await page.keyboard.type(alt_text, delay=15)
            log(f"  [alt filled] '{alt_text}'")
        else:
            log(f"  [alt warn] Focus not on input, skipping typing to avoid text leakage")
    
    # 2. Return focus to editor body after the image
    boxes = page.locator("div.article__edit-content--inner .article__image-box")
    n = await boxes.count()
    if n > 0:
        await boxes.nth(n - 1).click()
        await page.wait_for_timeout(200)
        await page.keyboard.press("ArrowRight")
        await page.keyboard.press("Enter")
        # Insert body caption
        await page.keyboard.insert_text(body_caption)
        await page.keyboard.press("Enter")
        await page.wait_for_timeout(200)

async def main():
    async with async_playwright() as p:
        browser, ctx = await connect(p)
        page = ctx.pages[0]
        
        # Navigate to a fresh blank article editor
        log("Opening blank article editor...")
        await page.goto("https://creator.xiaoheihe.cn/creator/editor/draft/article")
        await page.wait_for_timeout(3500)
        
        page = find_editor_page(ctx) or page
        log("Editor ready: " + page.url)
        
        # 1. Fill title
        t = page.locator(EDITOR_TITLE).first
        await t.click()
        await page.keyboard.type("微信压画质右键卡两秒？这3个良心开源工具直接封神", delay=8)
        log("Title filled!")
        
        # 2. Fill intro
        ed = page.locator(EDITOR_ARTICLE).first
        await ed.click()
        intro = "谁懂啊！每次新装电脑或者用久了，最折磨人的从来不是什么大病毒，而是这几个反人类日常——微信传照片压成像素油画、点个右键卡两秒弹出一堆流氓全家桶、想看个压缩包或者配置还要先打开几个大软件。\n\n今天老哥直接掏心窝子分享 3 个常年压箱底的开源神器，全都是几 MB 大小、单文件无广告。装上它们，你的电脑才算真正属于你自己。[cube_酷]\n"
        await page.keyboard.insert_text(intro)
        await page.wait_for_timeout(500)
        
        # 3. Fill sections with Markdown headings (# for H2, ## for H3)
        for sec in SECTIONS:
            await page.keyboard.press("Enter")
            
            # Section H2 (Large Heading)
            await page.keyboard.type(sec["h2"], delay=8)
            await page.keyboard.press("Enter")
            await page.wait_for_timeout(300)
            
            # Section Intro paragraph
            await page.keyboard.insert_text(sec["intro_p"])
            await page.keyboard.press("Enter")
            await page.wait_for_timeout(300)
            
            # Subheading 1 (H3 Medium)
            await page.keyboard.type(sec["sub_1"], delay=8)
            await page.keyboard.press("Enter")
            await page.wait_for_timeout(300)
            
            # Images set 1
            for img_name, alt_name, body_caption in sec["imgs"]:
                img_path = str(BASE_IMG_DIR / img_name)
                log(f"Inserting image {img_name}...")
                await insert_img_with_alt(page, img_path, alt_name, body_caption)
                
            # Subheading 2 (H3 Medium)
            await page.keyboard.type(sec["sub_2"], delay=8)
            await page.keyboard.press("Enter")
            await page.wait_for_timeout(300)
            
            # Images set 2
            for img_name, alt_name, body_caption in sec["imgs_2"]:
                img_path = str(BASE_IMG_DIR / img_name)
                log(f"Inserting image {img_name}...")
                await insert_img_with_alt(page, img_path, alt_name, body_caption)
                
            # Outro / Anti-blocking link
            await page.keyboard.insert_text(sec["outro"])
            await page.keyboard.press("Enter")
            await page.wait_for_timeout(300)
            
        # 4. Fill final summary with H3 header
        await page.keyboard.press("Enter")
        await page.keyboard.type("## 总结与避坑建议", delay=8)
        await page.keyboard.press("Enter")
        await page.wait_for_timeout(300)
        await page.keyboard.insert_text(FINAL_SUMMARY)
        await page.keyboard.press("Enter")
        await page.keyboard.press("Enter")
        await page.keyboard.insert_text(HASHTAGS)
        await page.wait_for_timeout(1000)
        log("Body completely written with H2/H3 visual hierarchy!")
        
        # 5. Save draft
        save_btn = page.locator("button:has-text('保存草稿')")
        if await save_btn.count():
            await save_btn.first.click()
            log("Saved draft successfully!")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
