# -*- coding: utf-8 -*-
"""拉起带调试端口的 Chrome（小黑盒专用 profile），并打开创作者后台。

为什么用固定 profile：
    小黑盒保存的是**扫码登录的会话**，会话在浏览器 profile 里。
    用同一个 --user-data-dir 打开，下次就不用重扫（但服务端会踢会话，隔几天仍要重登）。

用法：
    python start_chrome.py            # 用默认 profile（本 skill 目录下 .chrome-profile）
    python start_chrome.py --force    # 已有 Chrome 在使用该 profile 时也强行再开（一般不用）

注意：
    - 同一个 profile 不能被两个 Chrome 实例同时占用，先关掉上次开的窗口再跑。
    - 脚本只负责拉起 + 打开页面，扫码要你自己用手机 App 完成。
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from xhh_common import cdp_url, chrome_path, launch_command, log, print_config, profile_dir  # noqa: E402


def port_alive(url: str) -> bool:
    try:
        with urllib.request.urlopen(url + "/json/version", timeout=2) as r:
            return r.status == 200
    except Exception:
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--open", default="https://creator.xiaoheihe.cn/creator/home",
                    help="启动后打开的页面")
    args = ap.parse_args()

    print_config()
    url = cdp_url()

    if port_alive(url):
        log("\n%s 已经在跑，不必重复启动。" % url)
        log("直接跑 xhh_check.py 看登录态。")
        return 0

    cmd = launch_command()
    cmd[-1] = args.open
    log("\n启动：%s" % " ".join('"%s"' % c if " " in c else c for c in cmd))
    
    if sys.platform == "win32":
        # 在 Windows 上使用 WMI 启动，脱离当前作业对象，避免脚本退出时被强杀
        import subprocess
        ps_cmd = (
            f"$chrome = '{chrome_path()}'; "
            f"$profile = '{profile_dir()}'; "
            f"$target = '{args.open}'; "
            f"$port = '{cdp_url().rsplit(':', 1)[-1]}'; "
            f"$c = '\"' + $chrome + '\" --remote-debugging-port=' + $port + ' --user-data-dir=\"' + $profile + '\" --no-first-run --no-default-browser-check ' + $target; "
            f"Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{{CommandLine = $c}}"
        )
        subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True)
    else:
        subprocess.Popen(cmd)

    log("等调试端口就绪...")
    for i in range(30):
        time.sleep(1)
        if port_alive(url):
            log("✓ 已就绪（%ds）：%s" % (i + 1, url))
            log("\n接下来：")
            log("  1) 在打开的浏览器里检查右上角——有「登录」按钮就点它，用手机小黑盒 App 扫码")
            log("  2) 登录后点「发布内容 → 发布文章」，进到编辑器页面")
            log("  3) 跑 xhh_check.py 确认，再跑 xhh_build.py")
            return 0
    log("✗ 30 秒内没连上调试端口。")
    log("  常见原因：profile 被另一个 Chrome 占用（先关掉所有用该 profile 的窗口），")
    log("            或 Chrome 路径不对（在 config.json 里写 chrome_path）。")
    return 1


if __name__ == "__main__":
    sys.exit(main())
