# -*- coding: utf-8 -*-
"""小黑盒：登录态 + 编辑器状态检查（每次开跑前第一步）

为什么必须先跑这个：
    未登录也能打开 creator.xiaoheihe.cn 的后台框架，页面看着很正常，
    但所有填表操作都会失败。判据只有一个——右上角有没有「登录」按钮。

用法：
    python xhh_check.py
"""
from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

try:
    from playwright.async_api import async_playwright
except ImportError:
    from patchright.async_api import async_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
from xhh_common import connect, is_logged_in, log, print_config  # noqa: E402


async def main():
    ap = argparse.ArgumentParser(description="检查小黑盒登录态与编辑器状态")
    ap.add_argument("--wait", type=int, default=15,
                    help="每个标签页等待页面渲染的秒数（默认 15）")
    args = ap.parse_args()

    print_config()
    async with async_playwright() as p:
        browser, ctx = await connect(p)
        log("\n标签页 %d 个：" % len(ctx.pages))
        bad = 0
        unknown = 0
        checked = 0
        for i, pg in enumerate(ctx.pages):
            url = pg.url
            if not url.startswith("http"):
                continue
            marks = []
            if "/creator/editor/draft/" in url:
                marks.append("可写编辑器")
            elif "/creator/editor/edit/" in url:
                marks.append("已存草稿页(不回填)")
            st = await is_logged_in(pg, wait_s=args.wait)
            state = st.get("state")
            if state == "logged_out":
                marks.append("✗ 未登录")
                bad += 1
            elif state == "logged_in":
                marks.append("✓ 已登录")
            else:
                marks.append("? 判断不了: %s" % (st.get("error") or "页面未渲染"))
                unknown += 1
            checked += 1
            log("  [%d] %s" % (i, url[:88]))
            log("      %s %s" % (" ".join(marks), ("用户=" + ",".join(st["nicknames"])) if st.get("nicknames") else ""))

        if bad:
            log("\n[结论] 有页面显示未登录。处理：点右上角「登录」→ 手机小黑盒 App 扫码 → 扫码后重跑本脚本。")
            code = 2
        elif unknown or not checked:
            log("\n[结论] 没能确认登录态。先确认浏览器停在 https://creator.xiaoheihe.cn/creator，再重跑。")
            code = 3
        else:
            log("\n[结论] 登录态正常。")
            log("       接着在页面里「发布内容 → 发布文章」开一个空白编辑器，再跑 xhh_build.py。")
            code = 0
        await browser.close()
    return code


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
