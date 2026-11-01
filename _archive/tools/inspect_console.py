import sys, io, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth

PROFILE_DIR = r"C:\Users\zzx05\.gemini\antigravity\scratch\bot_chrome_profile"

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(PROFILE_DIR, channel="chrome", headless=True)
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    Stealth().apply_stealth_sync(page)
    
    page.goto("https://docode.cc/console", wait_until="networkidle")
    time.sleep(2)
    print("Console URL:", page.url)
    print("Page Title:", page.title())
    
    links = [(a.inner_text().strip(), a.get_attribute("href")) for a in page.locator("a").all() if a.inner_text().strip()]
    print("\nConsole Links:", links)
    
    buttons = [b.inner_text().strip() for b in page.locator("button").all() if b.inner_text().strip()]
    print("\nConsole Buttons:", buttons)
    
    # Check if there is an avatar or user info
    text_snippet = page.locator("body").inner_text()
    print("\nConsole Body Text Snippet:\n", text_snippet[:500].replace("\n", " "))
    ctx.close()
