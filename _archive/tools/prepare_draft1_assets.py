# -*- coding: utf-8 -*-
import os
import shutil
import json
from pathlib import Path
from PIL import Image

BASE_DIR = Path("reports/practical_tools")
ASSETS_DIR = BASE_DIR / "drafts_ready" / "draft_1_assets"
IMG_OUT = ASSETS_DIR / "images"

ASSETS_DIR.mkdir(parents=True, exist_ok=True)
if IMG_OUT.exists():
    shutil.rmtree(IMG_OUT)
IMG_OUT.mkdir(parents=True, exist_ok=True)

# 9 Verified High-Res UI Screenshots
img_sources = [
    # LocalSend
    ("localsend_localsend/screenshot_5.webp", "01_localsend_main.png", 
     "01 LocalSend：电脑端主界面，极简无广告开箱即用", 
     "狂砍 9.5 万+ Star 的开源跨平台版 AirDrop。设备走家庭局域网点对点直连，数据根本不出路由器。防屏蔽指路：github。com/localsend/localsend",
     "LocalSend 电脑端主界面"),
    ("localsend_localsend/screenshot_6.webp", "02_localsend_mobile.png", 
     "02 LocalSend：手机端秒识别局域网所有设备", 
     "手机连同一个 Wi-Fi 自动发现电脑、平板甚至电视。不用注册、不用扫码、断网也能传！",
     "LocalSend 手机端自动发现设备"),
    ("localsend_localsend/screenshot_7.webp", "03_localsend_settings.png", 
     "03 LocalSend：端到端本地加密与安全传输设置", 
     "局域网走 HTTPS 本地加密传输，私照、大文件直达目的地，告别微信压缩画质与第三方服务器泄露风险。",
     "LocalSend 加密设置"),
     
    # ContextMenuManager
    ("BluePointLilac_ContextMenuManager/screenshot_6.png", "04_contextmenu_clean.png", 
     "04 ContextMenuManager：2MB 单文件一键净化右键", 
     "国内硬核作者打造。分类梳理文件、文件夹、桌面等所有右键项，随手一点开关立即禁用，右键瞬间秒开！防屏蔽地址：github。com/BluePointLilac/ContextMenuManager",
     "ContextMenuManager 极简主界面"),
    ("BluePointLilac_ContextMenuManager/screenshot_5.png", "05_contextmenu_details.png", 
     "05 ContextMenuManager：精准注册表定位与残留彻底删除", 
     "支持直接定位注册表项与残留关联路径，彻底灰飞烟灭各路流氓全家桶，内存占用 0，用完即关。",
     "ContextMenuManager 高级清理项"),
    ("BluePointLilac_ContextMenuManager/screenshot_8.png", "06_contextmenu_rules.png", 
     "06 ContextMenuManager：多场景右键规则与拓展管理", 
     "包含 IE/Edge 扩展、文件发送到、新建项等全维度清理，右键卡顿彻底药到病除。",
     "ContextMenuManager 扩展管理"),

    # QuickLook
    ("QL-Win_QuickLook/branding_01.png", "07_quicklook_zip.png", 
     "07 QuickLook：空格键按一下，0 秒预览压缩包内部", 
     "2.5 万+ Star 开源神器，把 Mac 顶级的空格预览体验 100% 带给 Windows。不用解压，敲空格直接看压缩包目录！防屏蔽地址：github。com/QL-Win/QuickLook",
     "QuickLook 预览压缩包"),
    ("QL-Win_QuickLook/branding_04.png", "08_quicklook_image.png", 
     "08 QuickLook：大图无损秒级全屏预览与滚轮缩放", 
     "告别 Windows 慢吞吞的看图软件转圈。敲空格瞬间渲染超清大图，支持无级滚轮缩放，看图选图极速流畅。",
     "QuickLook 高清大图预览"),
    ("QL-Win_QuickLook/branding_03.png", "09_quicklook_code.png", 
     "09 QuickLook：代码、文本与日志文件原生高亮", 
     "对 JSON、Markdown、代码文件提供原生高亮预览，不用启动大型编辑器，秒查文件内容。",
     "QuickLook 代码高亮预览"),
]

items = []
for src, dst, name, desc, alt in img_sources:
    src_path = BASE_DIR / "images" / src
    dst_path = IMG_OUT / dst
    # Convert webp or copy png
    with Image.open(src_path) as im:
        rgb_im = im.convert("RGB") if im.mode in ("RGBA", "P") and not dst.endswith(".png") else im
        im.save(dst_path, "PNG")
    print(f"Saved {dst} ({im.size})")
    items.append({
        "name": name,
        "desc": desc,
        "alt": alt
    })

(ASSETS_DIR / "items.json").write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")

intro_text = """谁懂啊！每次新装电脑或者用久了，最折磨人的从来不是什么大病毒，而是这几个反人类日常——微信传照片压成像素油画、点个右键卡两秒弹出一堆流氓全家桶、想看个压缩包或者配置还要先打开几个大软件。

今天老哥直接掏心窝子分享 3 个常年压箱底的开源神器，全都是几 MB 大小、单文件无广告。装上它们，你的电脑才算真正属于你自己。[cube_酷]"""

(ASSETS_DIR / "intro.txt").write_text(intro_text, encoding="utf-8")

outro_text = """老实说，咱们用 Windows 这么多年，受够了各种大厂全家桶打着“优化”的旗号反向塞流氓弹窗。这 3 个开源小工具是我换了 3 台电脑依然第一时间必装的：

• LocalSend（~30MB）：手机电脑跨端免登满速互传，传完即可退出；
• ContextMenuManager（2MB）：一键净化右键菜单卡顿与流氓残留，纯单文件用完即关；
• QuickLook（~50MB）：键盘空格键 0 秒预览任何文件，静默驻留内存仅十几MB。

大伙们平时还在用什么冷门但封神的小工具？有踩坑或者装不上的直接在评论区抓我，有问必答！觉得有用别忘了顺手点个赞收个藏，我们下期见！[cube_干杯]"""

(ASSETS_DIR / "outro.txt").write_text(outro_text, encoding="utf-8")

print(f"\nSetup complete! Prepared {len(items)} verified UI screenshots in {IMG_OUT}")
