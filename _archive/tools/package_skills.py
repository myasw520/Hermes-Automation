# -*- coding: utf-8 -*-
"""打包小黑盒全套 Skills（post-xiaoheihe + xhh-style-bible）为便携分发包。
排除：.chrome-profile, .venv, __pycache__, *.pyc 等冗余和敏感会话数据。
"""
import os
import sys
import zipfile
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_ZIP = BASE_DIR / "xiaoheihe_skills_bundle.zip"

EXCLUDE_DIRS = {
    ".chrome-profile",
    ".venv",
    "__pycache__",
    ".git",
    ".idea",
    ".vscode"
}

EXCLUDE_EXTS = {
    ".pyc",
    ".pyo",
    ".pyd",
    ".log",
    ".tmp"
}

SKILLS_TO_PACK = [
    ("post-xiaoheihe", BASE_DIR / ".agents" / "skills" / "post-xiaoheihe"),
    ("xhh-style-bible", BASE_DIR / ".agents" / "skills" / "xhh-style-bible"),
]

SETUP_GUIDE_CONTENT = """# 小黑盒发布与写作全套 Skill 分发安装指南

本压缩包包含两套互补的精品 Skill：
1. **post-xiaoheihe**：小黑盒全自动排版与草稿发布工具（支持标题、封面裁剪、创作者激励计划、AI辅助声明、多图插入、原生题注、cube表情、草稿保存与接口校验）。
2. **xhh-style-bible**：小黑盒赛道写作风格库 2.0（基于 167 篇热帖深度去 AI 味规范，含完整 5 大赛道语料库）。

---

## 快速安装与配置（3步）

### 第一步：解压到技能目录
将解压后的两个文件夹 `post-xiaoheihe` 与 `xhh-style-bible` 放到你的 Agent 技能目录中，例如：
- 项目级目录：`<项目根目录>/.agents/skills/`
- 全局级目录：`~/.gemini/antigravity/skills/` 或 `C:\\Users\\<用户名>\\.gemini\\antigravity\\skills\\`

### 第二步：安装 Python 依赖
进入 `post-xiaoheihe` 目录：
- **Windows 用户**：直接双击运行 `install.bat`。
- **手动安装**：
  ```bash
  python -m venv .venv
  .venv\\Scripts\\python.exe -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
  ```

### 第三步：拉起专用 Chrome 并登录小黑盒
- 双击运行 `scripts\\start_chrome.bat`（或运行 `.venv\\Scripts\\python.exe scripts\\start_chrome.py`）。
- 浏览器会自动打开小黑盒创作者后台并监听 9223 端口。
- 在打开的浏览器右上角点击「登录」，使用**手机小黑盒 App** 扫码登录。
- 双击 `scripts\\check.bat` 验证，出现 `[✓] 已登录` 即大功告成！

---

## 常用发布命令

### 推荐：结构化区块模式（支持分级标题、原生图片描述、封面与激励计划）
```bash
.venv\\Scripts\\python.exe scripts\\xhh_build.py ^
    --title "文章标题" ^
    --article-json article_blocks.json ^
    --cover "封面.png" ^
    --plan-article ^
    --declare-ai ^
    --save-draft
```

### 传统模式：图片目录 + 图注模式
```bash
.venv\\Scripts\\python.exe scripts\\xhh_build.py ^
    --layout caption ^
    --title "文章标题" ^
    --items items.json ^
    --hashtags "#电脑软件 #开源项目" ^
    --cover "封面.png" ^
    --plan-article ^
    --declare-ai ^
    --save-draft ^
    "图片目录路径"
```

保存草稿后，直接在手机端小黑盒 App 的草稿箱中查看并一键发布！
"""

def should_exclude(path: Path) -> bool:
    for part in path.parts:
        if part in EXCLUDE_DIRS:
            return True
    if path.suffix.lower() in EXCLUDE_EXTS:
        return True
    return False

def package():
    print(f"正在打包 Skills 到: {OUTPUT_ZIP} ...")
    total_files = 0
    total_size = 0

    with zipfile.ZipFile(OUTPUT_ZIP, "w", zipfile.ZIP_DEFLATED) as zf:
        # 1. 写入安装指南
        zf.writestr("README_INSTALL.md", SETUP_GUIDE_CONTENT)
        print("  [+] README_INSTALL.md")

        # 2. 打包两个 skill 目录
        for arc_prefix, src_dir in SKILLS_TO_PACK:
            if not src_dir.exists():
                print(f"  [!] 目录不存在: {src_dir}")
                continue
            
            for file_path in src_dir.rglob("*"):
                if file_path.is_dir() or should_exclude(file_path):
                    continue
                
                rel_path = file_path.relative_to(src_dir)
                archive_name = f"{arc_prefix}/{rel_path.as_posix()}"
                
                zf.write(file_path, archive_name)
                fsize = file_path.stat().st_size
                total_files += 1
                total_size += fsize
                # print(f"  + {archive_name} ({fsize} bytes)")

    zip_size_mb = OUTPUT_ZIP.stat().st_size / (1024 * 1024)
    raw_size_mb = total_size / (1024 * 1024)
    print(f"\n[✓] 打包完成！共压缩 {total_files} 个文件")
    print(f"    原始大小: {raw_size_mb:.2f} MB")
    print(f"    压缩后大小: {zip_size_mb:.2f} MB")
    print(f"    输出路径: {OUTPUT_ZIP.resolve()}")

if __name__ == "__main__":
    package()
