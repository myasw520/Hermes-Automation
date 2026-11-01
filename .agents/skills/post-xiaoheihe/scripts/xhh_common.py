# -*- coding: utf-8 -*-
"""小黑盒发布脚本公共模块：配置、Chrome 定位、CDP 连接、登录态检查。

设计原则：换台电脑不用改代码。
- 调试端口：环境变量 XHH_CDP > config.json 的 cdp_url > 127.0.0.1:9223
- Chrome 路径：环境变量 XHH_CHROME > config.json 的 chrome_path > 常见安装位置自动探测
- profile 目录：环境变量 XHH_PROFILE > config.json 的 profile_dir > 本 skill 目录下 .chrome-profile
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

# Fix Windows console UTF-8 encoding
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# scripts/ 的上一级就是 skill 根目录
SKILL_ROOT = Path(__file__).resolve().parent.parent
CONFIG_FILE = SKILL_ROOT / "config.json"

DEFAULT_CDP = "http://127.0.0.1:9223"
DEFAULT_PROFILE = ".chrome-profile"

_CHROME_CANDIDATES = [
    os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
    os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
    os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium",
]

EDITOR_TITLE = "div.editor-title__container .ProseMirror"
EDITOR_ARTICLE = "div.article__edit-content--inner .ProseMirror"
EDITOR_IMAGE_TEXT = "div.image-text__edit-content .ProseMirror"


def log(msg: str) -> None:
    try:
        print(msg, flush=True)
    except UnicodeEncodeError:
        print(msg.encode("ascii", errors="backslashreplace").decode("ascii"), flush=True)


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        return {}
    try:
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except Exception as e:
        log("[warn] config.json 解析失败（%s），改用默认值" % e)
        return {}


def cdp_url() -> str:
    return os.environ.get("XHH_CDP") or load_config().get("cdp_url") or DEFAULT_CDP


def chrome_path() -> str | None:
    explicit = os.environ.get("XHH_CHROME") or load_config().get("chrome_path")
    if explicit:
        if Path(explicit).exists():
            return explicit
        log("[warn] 配置里的 chrome_path 不存在：%s" % explicit)
    for c in _CHROME_CANDIDATES:
        if Path(c).exists():
            return c
    return None


def profile_dir() -> Path:
    p = os.environ.get("XHH_PROFILE") or load_config().get("profile_dir") or str(SKILL_ROOT / DEFAULT_PROFILE)
    path = Path(p).expanduser()
    path.mkdir(parents=True, exist_ok=True)
    return path


def print_config() -> None:
    log("  调试端口 : %s" % cdp_url())
    cp = chrome_path()
    log("  Chrome   : %s" % (cp or "未找到（请写进 config.json 的 chrome_path）"))
    log("  profile  : %s" % profile_dir())


def launch_command() -> list[str]:
    """返回拉起 Chrome 的命令行（列表形式，避免 shell 转义问题）。"""
    cp = chrome_path()
    if not cp:
        raise RuntimeError(
            "找不到 Chrome，请在 config.json 里写 chrome_path，或设置环境变量 XHH_CHROME"
        )
    return [
        cp,
        "--remote-debugging-port=%s" % cdp_url().rsplit(":", 1)[-1],
        "--user-data-dir=%s" % profile_dir(),
        "--no-first-run",
        "--no-default-browser-check",
        "https://creator.xiaoheihe.cn/creator/home",
    ]


async def connect(playwright_obj):
    """连接已开启调试端口的 Chrome，返回 (browser, context)。

    连不上时给出可操作的报错，而不是原始 traceback。
    """
    url = cdp_url()
    try:
        browser = await playwright_obj.chromium.connect_over_cdp(url)
    except Exception as e:
        raise RuntimeError(
            "连不上 %s（%s）。\n"
            "  先运行 scripts/start_chrome.bat 拉起浏览器，再用同一个 profile 扫码登录。"
            % (url, type(e).__name__)
        ) from e
    if not browser.contexts:
        raise RuntimeError(
            "已连上 %s，但浏览器没有一个可用的上下文。\n"
            "  说明这个 Chrome 是空的调试会话，请用 start_chrome.bat 指定的 profile 重新打开。"
            % url
        )
    return browser, browser.contexts[0]


def find_editor_page(ctx):
    """挑出可写内容的编辑器标签页。

    优先级：
      1. /creator/editor/draft/...  未保存的创建会话（可写）
      2. /creator/editor/edit/...    已保存草稿的编辑页（打开是空白，不回填内容）
    """
    draft_sessions = [pg for pg in ctx.pages if "/creator/editor/draft/" in pg.url]
    if draft_sessions:
        return draft_sessions[-1]
    edit_pages = [pg for pg in ctx.pages if "/creator/editor/edit/" in pg.url]
    if edit_pages:
        return edit_pages[-1]
    any_editor = [pg for pg in ctx.pages if "/creator/editor" in pg.url]
    return any_editor[-1] if any_editor else None


_PROBE_JS = """() => {
    const bodyText = document.body ? (document.body.innerText || '') : '';
    const loginBtn = document.querySelector('button.creator-nav-login-btn');
    const anyLogin = Array.from(document.querySelectorAll('button, a'))
        .some(el => (el.textContent || '').trim() === '登录');
    const unauthText = bodyText.includes('未登录');
    const logoutHit = Array.from(document.querySelectorAll('button, a, [class*="logout"], [class*="user"]'))
        .some(el => /退出登录|退出账号/.test((el.textContent || '').trim()));
    const nick = Array.from(document.querySelectorAll(
        '[class*="nickname"],[class*="user-name"],[class*="avatar"]'
    )).map(e => (e.textContent || '').trim()).filter(t => t && t !== '未登录').slice(0, 2);
    return {
        hasLoginBtn: !!loginBtn || anyLogin,
        unauthText,
        hasLogout: logoutHit,
        nicknames: nick,
        bodyLen: bodyText.trim().length,
        url: location.href,
    };
}"""


async def is_logged_in(page, wait_s: int = 15) -> dict:
    """检查登录态（轮询等待页面渲染完）。

    为什么必须轮询：创作者后台是 SPA，连上 CDP 时页面往往还没渲染，
    `/creator/home` 会跳 `/creator`，导航按钮是后挂载的。
    如果这时候直接查「登录」按钮，会因为页面空白而误判成已登录。
    （2026-10-23 实测踩到：全新 profile 被判成「✓ 已登录」。）

    判据（任一命中即定论）：
      未登录：存在「登录」按钮  或  正文出现「未登录」
      已登录：存在「退出登录」  或  有昵称/头像且没有登录按钮
      都没有：继续等，超时返回 unknown
    """
    last = {}
    for _ in range(max(1, wait_s)):
        try:
            last = await page.evaluate(_PROBE_JS)
        except Exception as e:
            last = {"hasLoginBtn": None, "error": str(e)[:120]}
            await page.wait_for_timeout(1000)
            continue

        if last.get("hasLoginBtn") or last.get("unauthText"):
            last["state"] = "logged_out"
            return last
        if last.get("hasLogout"):
            last["state"] = "logged_in"
            return last
        # 有昵称/头像、正文也有内容、且没有登录入口 → 认为已登录
        if last.get("nicknames") and last.get("bodyLen", 0) > 20:
            last["state"] = "logged_in"
            return last
        await page.wait_for_timeout(1000)

    last = dict(last or {})
    last["state"] = "unknown"
    return last


async def require_login(page, wait_s: int = 15) -> bool:
    """登录态不通过就打印处理步骤并返回 False。"""
    st = await is_logged_in(page, wait_s=wait_s)
    state = st.get("state")

    if state == "logged_in":
        log("[登录态] ✓ 已登录 %s" % (" ".join(st.get("nicknames") or "")))
        return True
    if state == "logged_out":
        log("[登录态] ✗ 未登录（%s）" % (
            "页面有「登录」按钮" if st.get("hasLoginBtn") else "正文显示「未登录」"))
        log("         处理：点右上角「登录」→ 手机小黑盒 App 扫码 → 扫码后重跑本脚本。")
        return False
    log("[登录态] ? 判断不了（页面没渲染出登录/用户信息，%s）"
        % (st.get("error") or "等 %ds 仍空白" % wait_s))
    log("         常见原因：页面还在加载、网络慢、或标签页不是 creator 页面。")
    log("         先确认浏览器停在 https://creator.xiaoheihe.cn/creator，再重跑。")
    return False
