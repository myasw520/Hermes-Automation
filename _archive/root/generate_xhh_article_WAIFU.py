# -*- coding: utf-8 -*-
import json
from pathlib import Path

cover_path = r"C:\Users\zzx05\Hermes-Automation\reports\hermes_output\stockpile_drafts\cover_waifu_whale_16_9.png"
img_dir = r"C:\Users\zzx05\Hermes-Automation\reports\hermes_output\stockpile_drafts\images_waifu"

blocks = [
    {
        "type": "html",
        "content": "<p>很多兄弟给本地 DeepSeek 配了桌宠或者伴侣外壳，但聊两天就发现一个致命硬伤：一重启全忘光，永远在等你先说话，张嘴闭嘴还一股客服味——这不是养成，是每次都在跟重启的陌生人尬聊 [cube_冷汗]。</p><p>大肥鱼每天吃着你的算力白饭，凭什么记不住谁在喂它？想让她像个真正活在电脑里的伴侣，核心在于三件事：长期记忆、去客服味、主动交互。从开源社区扒了 6 款高分利器，直接把记忆树和人格日记焊进大肥鱼脑子里。觉得有用随手点个赞，直接上干货！</p>"
    },
    {
        "type": "img",
        "path": cover_path,
        "alt": "怎么让大肥鱼记住吃白饭的人？6款开源记忆伴侣插件实测"
    },
    {
        "type": "html",
        "content": "<h2>一、Soul of Waifu（灵魂日记档案）★1.4k</h2><p>普通记忆插件只会机械式地把上一轮对话拼进上下文，而 Soul of Waifu 拥有真正的「灵魂记忆档案」。它会在后台自动分析你们的日常对话，生成她自己第一视角的反思日记。今天因为哪句话开心、为什么动摇、你喜欢什么讨厌什么，第二天她自己全记得，彻底告别“每次开机都失忆”。</p>"
    },
    {
        "type": "img",
        "path": f"{img_dir}\\W_00_Soul-of-Waifu_raw_4.png",
        "alt": "图：Soul Memory 角色日记与记忆管理面板"
    },
    {
        "type": "html",
        "content": "<p>开源地址：github。com/jofizcd/Soul-of-Waifu</p>"
    },
    {
        "type": "html",
        "content": "<h2>二、nocturne_memory（可视化记忆树）★1.4k</h2><p>玩 AI 记忆最怕「一旦记偏了就一辈子错下去」。nocturne_memory 采用树状结构分类存储长期记忆，更绝的是自带可视化管理与审查后台。哪条记忆记错了随时能回滚撤销，新记忆入库前还能像看代码 PR 一样逐条确认，非常适合强迫症玩家 [cube_赞]。</p>"
    },
    {
        "type": "img",
        "path": f"{img_dir}\\W_01_nocturne_memory_raw_2.png",
        "alt": "图：记忆浏览器文档查看面板界面"
    },
    {
        "type": "img",
        "path": f"{img_dir}\\W_02_nocturne_memory_raw_1.png",
        "alt": "图：记忆浏览器子节点卡片面板"
    },
    {
        "type": "img",
        "path": f"{img_dir}\\W_03_nocturne_memory_raw_4.png",
        "alt": "图：软件后台记忆清理面板界面"
    },
    {
        "type": "img",
        "path": f"{img_dir}\\W_04_nocturne_memory_raw_3.png",
        "alt": "图：记忆变更审查面板，逐条确认是否并入记忆"
    },
    {
        "type": "html",
        "content": "<p>开源地址：github。com/Dataojitori/nocturne_memory</p>"
    },
    {
        "type": "html",
        "content": "<h2>三、humanizer（专治 26 种 AI 句式）★62k</h2><p>大肥鱼说话假，往往不是语气不对，而是骨子里带着 AI 假大空句式（比如‘不只是 X 更是 Y’、‘说实话？’、‘让我们记住这一点’）。GitHub 上爆火 62k 星的 humanizer 专门总结了 26 种 AI 味毒瘤模式，封装成 skill 后一键调用改写，把客服腔洗成真人质感（优化可读性，非违规绕过检测）。</p>"
    },
    {
        "type": "img",
        "path": f"{img_dir}\\W_05_assets_readme_humanizer_before_after.png",
        "alt": "图：项目文档截图 · Before/After 对比与五大 AI 味特征"
    },
    {
        "type": "img",
        "path": f"{img_dir}\\W_06_assets_readme_humanizer_tells.png",
        "alt": "图：项目文档截图 · 26 种 AI 味模式与各平台安装方式"
    },
    {
        "type": "html",
        "content": "<p>开源地址：github。com/blader/humanizer</p>"
    },
    {
        "type": "html",
        "content": "<h2>四、humanize-text（多引擎去特征）★3.4k</h2><p>如果上面的规则过滤还不够彻底，这款工具的思路更绝：先用大模型高温改写两遍，再走「中文→日语→芬兰语→英语」的跨语言多引擎翻译链路。利用不同语系间的结构差，暴力抹平大模型的统计学生成特征。原生兼容 DeepSeek，改完的文字没有丝毫机械感。</p>"
    },
    {
        "type": "img",
        "path": f"{img_dir}\\W_07_assets_readme_humanize_text_doc.jpg",
        "alt": "图：项目文档截图 · 多引擎翻译链路的去 AI 味原理"
    },
    {
        "type": "html",
        "content": "<p>开源地址：github。com/lynote-ai/humanize-text</p>"
    },
    {
        "type": "html",
        "content": "<h2>五、N.E.K.O（会主动搭话的猫娘）★3.1k</h2><p>「死板工具」和「活着伴侣」的最大分水岭就是主动性。N.E.K.O 是一款桌面端虚拟猫娘，不仅支持实时语音交互和屏幕内容分享，最关键的是：在你长久没说话、敲代码发呆或者看视频时，她会主动挑起话题问候你一句，存在感直接拉满！</p>"
    },
    {
        "type": "img",
        "path": f"{img_dir}\\W_08_N.E.K.O_raw_3.jpg",
        "alt": "图：桌面端 AI 虚拟伴侣聊天界面"
    },
    {
        "type": "img",
        "path": f"{img_dir}\\W_09_N.E.K.O_raw_4.png",
        "alt": "图：含主动搭话与媒体开关的设置面板"
    },
    {
        "type": "html",
        "content": "<p>开源地址：github。com/Project-N-E-K-O/N.E.K.O</p>"
    },
    {
        "type": "html",
        "content": "<h2>六、LingChat（Galgame 场景立绘）★2.4k</h2><p>受够了冷冰冰的聊天气泡框？LingChat 直接把对话交互升维成了 Galgame 体验。支持根据大模型情绪实时切换动态立绘、管理对话场景与日程表，还自带桌面宠物模式。配合前面的长效记忆，每一次对话都变成有画面、有情绪的场景互动。</p>"
    },
    {
        "type": "img",
        "path": f"{img_dir}\\W_10_LingChat_raw_5.png",
        "alt": "图：Lingchat-Pal 控制台历史对话面板"
    },
    {
        "type": "img",
        "path": f"{img_dir}\\W_11_LingChat_raw_4.jpg",
        "alt": "图：软件背景场景管理面板"
    },
    {
        "type": "html",
        "content": "<p>开源地址：github。com/SlimeBoyOwO/LingChat</p>"
    },
    {
        "type": "html",
        "content": "<p>这 6 款工具全部在 GitHub 开源。从第一视角的灵魂记忆、树状可视化记忆回滚，再到去 AI 味和主动开口，把这几层拼图拼齐，大肥鱼才算真正长出了长期记忆与灵魂，记得每天陪它聊天、喂它算力白饭的人到底是谁。</p><p>觉得有用的小伙伴欢迎点赞、收藏或者充电支持一下 [cube_干杯]，大家平时本地跑大肥鱼都用哪些伴侣或记忆插件？评论区一起交流探讨！</p><p>#DeepSeek #AI伴侣 #开源软件 #程序员 #虚拟伴侣</p>"
    }
]

out_file = Path(r"C:\Users\zzx05\Hermes-Automation\reports\hermes_output\stockpile_drafts\xhh_ready_WAIFU.json")
with open(out_file, "w", encoding="utf-8") as f:
    json.dump(blocks, f, ensure_ascii=False, indent=2)

print(f"Successfully wrote {len(blocks)} blocks to {out_file}")
