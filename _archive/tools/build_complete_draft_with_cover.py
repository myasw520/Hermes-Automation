# -*- coding: utf-8 -*-
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
import sys

sys.path.insert(0, r"c:\Users\zzx05\Hermes-Automation\.agents\skills\post-xiaoheihe\scripts")
from xhh_common import connect, find_editor_page, log, EDITOR_TITLE

BASE_IMG_DIR = Path(r"reports\practical_tools\drafts_ready\draft_1_assets\images")
COVER_PATH = str(Path(r"c:\Users\zzx05\Hermes-Automation\小黑盒封面_轻杂志漫风_推荐.png").resolve())

ARTICLE_BLOCKS = [
    # 1. Intro + Tool 1: LocalSend Header & Intro
    ("html", """<p>谁懂啊！每次新装电脑或者用久了，最折磨人的从来不是什么大病毒，而是这几个反人类日常——微信传照片压成像素油画、点个右键卡两秒弹出一堆流氓全家桶、想看个压缩包或者配置还要先打开几个大软件。</p>
<p>今天老哥直接掏心窝子分享 3 个常年压箱底的开源神器，全都是几 MB 大小、单文件无广告。装上它们，你的电脑才算真正属于你自己。[cube_酷]</p>
<h2>一、LocalSend：彻底戒掉微信传文件焦虑，内网满速飞传</h2>
<p>先来对号入座，你平时在手机和电脑之间倒腾文件，是不是总被恶心：辛辛苦苦修好的 4K 壁纸发到手机直接压成 480P 马赛克；传个 1G 视频进度条像乌龟爬；插数据线弹一堆全家桶助手。</p>
<p>LocalSend 在 GitHub 狂砍 9.5 万+ Star，说白了它就是一个开源跨平台版的 AirDrop。走家庭局域网，数据根本不出路由器！</p>
<h3>【实测体验】开箱即用，断网也能满速传</h3>"""),
    ("img", "01_localsend_main.png", "LocalSend 电脑端主界面"),
    ("html", "<p>▲ 电脑端主界面：极简无广告，开箱即用，断网也能互传</p>"),
    ("img", "02_localsend_mobile.png", "手机端局域网设备发现"),
    ("html", """<p>▲ 手机端秒识别局域网设备：连同一个 Wi-Fi 自动发现电脑与平板</p>
<h3>【隐私安全】走本地端到端加密，零云端泄露</h3>"""),
    ("img", "03_localsend_settings.png", "本地端到端加密设置"),
    ("html", """<p>▲ 本地端到端加密：走 HTTPS 局域网加密，告别微信压缩与云端泄露风险</p>
<p>防屏蔽指路：GitHub 搜索 localsend/localsend（开源地址：github。com/localsend/localsend）。</p>"""),
    
    # 2. Tool 2: ContextMenuManager
    ("html", """<h2>二、ContextMenuManager：2MB 绿色单文件，一键净化右键全家桶</h2>
<p>新电脑用上几个月，桌面点个鼠标右键是不是要卡两秒？满屏都是各类流氓软件强行塞进来的私货菜单，密密麻麻看着就高血压。</p>
<p>ContextMenuManager 只有区区 2MB，绿色免安装单文件，国内硬核作者打造，专治 Windows 右键烂摊子。</p>
<h3>【实测体验】分类梳理所有右键项，秒级禁用</h3>"""),
    ("img", "04_contextmenu_clean.png", "ContextMenuManager 主界面"),
    ("html", "<p>▲ 主界面清晰分类：梳理所有右键项，随手一点开关立即禁用</p>"),
    ("img", "05_contextmenu_details.png", "右键注册表与残留项清理"),
    ("html", """<p>▲ 精准定位注册表项：支持查看关联路径，彻底灰飞烟灭卸载残留菜单</p>
<h3>【深度清理】全维度右键与新建项管理</h3>"""),
    ("img", "06_contextmenu_rules.png", "多场景扩展与新建项管理"),
    ("html", """<p>▲ 多场景扩展管理：IE/Edge 扩展、发送到、新建项全维度清理，内存占用 0</p>
<p>防屏蔽指路：GitHub 搜索 BluePointLilac/ContextMenuManager（开源地址：github。com/BluePointLilac/ContextMenuManager）。</p>"""),
    
    # 3. Tool 3: QuickLook
    ("html", """<h2>三、QuickLook：空格键按一下，0 秒预览一切文件</h2>
<p>用过 Mac 的老哥都知道那个“按空格预览”有多爽，而 Windows 默认看个压缩包或者代码都要等大型软件转圈。</p>
<p>QuickLook 斩获 2.5 万+ Star，直接把 Mac 这一神仙级体验 100% 带给了 Windows！不用解压、不用等软件启动，敲一下空格键直接在屏幕正中央弹出超清大图或文件目录。</p>
<h3>【实测体验】压缩包免解压，敲空格直接看</h3>"""),
    ("img", "07_quicklook_zip.png", "QuickLook 空格键预览压缩包"),
    ("html", """<p>▲ 空格键秒预览压缩包内部：不用解压，直接看清所有文件层级</p>
<h3>【格式通吃】单反大图与代码文件原生高亮渲染</h3>"""),
    ("img", "08_quicklook_image.png", "高清单反大图秒级无损预览"),
    ("html", "<p>▲ 高清单反大图秒级渲染：敲空格瞬间全屏预览，支持无级滚轮缩放</p>"),
    ("img", "09_quicklook_code.png", "代码与 Markdown 高亮预览"),
    ("html", """<p>▲ 代码与文本高亮预览：对 JSON、Markdown、代码文件提供原生高亮预览</p>
<p>防屏蔽指路：GitHub 搜索 QL-Win/QuickLook（开源地址：github。com/QL-Win/QuickLook，微软商店也能直接搜到）。</p>"""),
    
    # 4. Summary & Outro
    ("html", """<h2>四、装机建议与总结</h2>
<p>老实说，咱们用 Windows 这么多年，受够了各种大厂全家桶打着“优化”的旗号反向塞流氓弹窗。这 3 个开源小工具是我换了 3 台电脑依然第一时间必装的：</p>
<p>• <strong>LocalSend（~30MB）</strong>：手机电脑跨端免登满速互传，传完即可退出；</p>
<p>• <strong>ContextMenuManager（2MB）</strong>：一键净化右键菜单卡顿与流氓残留，纯单文件用完即关；</p>
<p>• <strong>QuickLook（~50MB）</strong>：键盘空格键 0 秒预览任何文件，静默驻留内存仅十几MB。</p>
<p>大伙们平时还在用什么冷门但封神的小工具？有踩坑或者装不上的直接在评论区抓我，有问必答！觉得有用别忘了顺手点个赞收个藏，我们下期见！ [cube_干杯]</p>
<p>#电脑软件 #数码科技 #开源项目 #装机推荐</p>""")
]

async def paste_html(page, html):
    """Paste HTML chunk into ProseMirror cleanly."""
    await page.evaluate("""html => {
        const dt = new DataTransfer();
        dt.setData('text/html', html);
        dt.setData('text/plain', html.replace(/<[^>]+>/g, ''));
        const ev = new ClipboardEvent('paste', {
            clipboardData: dt,
            bubbles: true,
            cancelable: true
        });
        const ed = document.querySelector('div.article__edit-content--inner .ProseMirror');
        ed.dispatchEvent(ev);
    }""", html)
    await page.wait_for_timeout(300)

async def insert_img(page, img_path, alt_text):
    """Upload image via UI and fill alt description."""
    ed = page.locator("div.article__edit-content--inner .ProseMirror").first
    await ed.click()
    await page.keyboard.press("Control+End")
    await page.wait_for_timeout(250)
    
    await page.locator(".editor-menu-image").first.click()
    await page.wait_for_timeout(800)
    
    async with page.expect_file_chooser(timeout=15000) as fc_info:
        await page.locator(".editor-image-wrapper__box.upload").first.click()
    file_chooser = await fc_info.value
    await file_chooser.set_files(img_path)
    
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
    
    # Fill native alt description
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
    
    # Return cursor to editor after the image
    boxes = page.locator("div.article__edit-content--inner .article__image-box")
    n = await boxes.count()
    if n > 0:
        await boxes.nth(n - 1).click()
        await page.wait_for_timeout(200)
        await page.keyboard.press("ArrowRight")
        await page.keyboard.press("Enter")
        await page.wait_for_timeout(200)

async def configure_publish_settings(page):
    """Set creation plan, upload cover, and choose AI declaration."""
    log("Configuring publish settings on the right panel...")
    
    # 1. 创作计划 -> 参与
    plan_btn = page.locator(".creation-plan-join .switch__button").first
    if await plan_btn.count():
        # Check if already active
        is_active = await page.locator(".creation-plan-join .switch__true-label.active").count()
        if not is_active:
            await plan_btn.click()
            await page.wait_for_timeout(800)
            log("  [✓] 创作计划已勾选【参与】")
    
    # 2. 选择计划 -> 文章计划
    article_plan = page.locator(".creation-plan-select__radio:has-text('文章计划')").first
    if await article_plan.count():
        await article_plan.click()
        await page.wait_for_timeout(400)
        log("  [✓] 已选【文章计划】")
        
    # 3. 上传封面
    thumb_btn = page.locator(".thumb-card__right, .thumb-card__corner, .creator-editor__thumb-card").first
    if await thumb_btn.count():
        await thumb_btn.click()
        await page.wait_for_timeout(1000)
        
        # In upload modal
        upload_box = page.locator(".editor-model__thumb-upload").first
        if await upload_box.count():
            log(f"  Uploading cover: {COVER_PATH}")
            async with page.expect_file_chooser(timeout=15000) as fc_info:
                await upload_box.click()
            fc = await fc_info.value
            await fc.set_files(COVER_PATH)
            await page.wait_for_timeout(3500)
            
            # Click confirm crop
            mask = page.locator(".hb-cpt__mask-wrapper")
            confirm_btn = mask.locator(".hb-color__btn--confirm").first
            if await confirm_btn.count():
                await confirm_btn.click()
                await page.wait_for_timeout(2000)
                log("  [✓] 封面图片上传并裁剪确认成功！")
                
    # 4. 其他声明 -> 包含AI辅助创作
    decl_box = page.locator(".article-transshipment .selector__box").first
    if await decl_box.count():
        await decl_box.click()
        await page.wait_for_timeout(500)
        ai_opt = page.locator(".article-transshipment .selector__pull-list-item:has-text('包含AI辅助创作')").first
        if await ai_opt.count():
            await ai_opt.click()
            await page.wait_for_timeout(500)
            log("  [✓] 其他声明已选【包含AI辅助创作】")

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
        
        # 2. Iterate through ARTICLE_BLOCKS
        for idx, block in enumerate(ARTICLE_BLOCKS):
            btype = block[0]
            if btype == "html":
                html_chunk = block[1].strip()
                if html_chunk.startswith("<h2>"):
                    await page.keyboard.press("Enter")
                    await page.wait_for_timeout(150)
                await paste_html(page, html_chunk)
            elif btype == "img":
                img_name, alt_text = block[1], block[2]
                img_path = str(BASE_IMG_DIR / img_name)
                log(f"Inserting image {img_name}...")
                await insert_img(page, img_path, alt_text)
                
        await page.wait_for_timeout(1000)
        log("Body completely written with exact semantic tags (h2/h3/p/strong)!")
        
        # 3. Configure publishing settings: Plan + Cover + Declaration
        await configure_publish_settings(page)
        await page.wait_for_timeout(1000)
        
        # 4. Save draft
        save_btn = page.locator("button:has-text('保存草稿')")
        if await save_btn.count():
            await save_btn.first.click()
            log("Saved draft with COVER & SETTINGS successfully!")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
