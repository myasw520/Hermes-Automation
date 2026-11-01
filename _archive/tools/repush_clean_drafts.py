# -*- coding: utf-8 -*-
import subprocess
import sys
import time
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

PROJECT_ROOT = Path(__file__).resolve().parent.parent
STOCKPILE_DIR = PROJECT_ROOT / "reports" / "stockpile_drafts"
PYTHON_EXE = PROJECT_ROOT / ".agents" / "skills" / "post-xiaoheihe" / ".venv" / "Scripts" / "python.exe"
if not PYTHON_EXE.exists():
    PYTHON_EXE = Path(sys.executable)

BUILD_SCRIPT = PROJECT_ROOT / ".agents" / "skills" / "post-xiaoheihe" / "scripts" / "xhh_build.py"

TASKS = [
    {
        "title": "别装几百兆全家桶了！这3个几十星的单文件专治发热与弹窗",
        "json": STOCKPILE_DIR / "track_a_windows" / "01_专治发热与流氓更新_三款百星单文件" / "article_blocks.json",
        "cover": STOCKPILE_DIR / "track_a_windows" / "01_专治发热与流氓更新_三款百星单文件" / "cover_16_9.png"
    },
    {
        "title": "别看那几个几万星的水货了！这3个野生独立工具把Windows效率拉满",
        "json": STOCKPILE_DIR / "track_a_windows" / "02_摸鱼与桌面效率巅峰_窗口透明与平铺" / "article_blocks.json",
        "cover": STOCKPILE_DIR / "track_a_windows" / "02_摸鱼与桌面效率巅峰_窗口透明与平铺" / "cover_16_9.png"
    },
    {
        "title": "别再给云端API交保护费了！3个几MB的本地离线AI神仙小玩具",
        "json": STOCKPILE_DIR / "track_b_local_ai" / "01_别给云端API交保护费_三款离线本地AI黑科技" / "article_blocks.json",
        "cover": STOCKPILE_DIR / "track_b_local_ai" / "01_别给云端API交保护费_三款离线本地AI黑科技" / "cover_16_9.png"
    }
]

def main():
    for idx, t in enumerate(TASKS, 1):
        print(f"\n==================================================")
        print(f"正在全自动重新推送第 {idx}/3 篇: 《{t['title']}》")
        print(f"==================================================")

        cmd = [
            str(PYTHON_EXE),
            str(BUILD_SCRIPT),
            "--auto-open",
            "--title", t["title"],
            "--article-json", str(t["json"]),
            "--cover", str(t["cover"]),
            "--plan-article",
            "--declare-ai",
            "--save-draft"
        ]

        ret = subprocess.run(cmd)
        if ret.returncode != 0:
            print(f"[!] 推送失败，退出码: {ret.returncode}")
        else:
            print(f"[✓] 第 {idx} 篇推送并保存草稿成功！")
        time.sleep(3)

if __name__ == "__main__":
    main()
