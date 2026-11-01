import sys, io, time, os, urllib.request, subprocess
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PROXY = "http://127.0.0.1:7897"
DOWNLOAD_DIR = r"C:\Users\zzx05\Downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
INSTALLER_PATH = os.path.join(DOWNLOAD_DIR, "ObsidianSetup.exe")

URL = "https://github.com/obsidianmd/obsidian-releases/releases/download/v1.14.4/Obsidian-1.14.4.exe"

print(f"[*] 准备通过本地代理 {PROXY} 下载官方最新版 Obsidian...")
print(f"[*] 目标 URL: {URL}")

opener = urllib.request.build_opener(urllib.request.ProxyHandler({'http': PROXY, 'https': PROXY}))
urllib.request.install_opener(opener)

def report_progress(block_num, block_size, total_size):
    downloaded = block_num * block_size
    if total_size > 0:
        percent = downloaded * 100 / total_size
        if block_num % 1000 == 0 or downloaded >= total_size:
            print(f"  [↓] 已下载 {downloaded / 1024 / 1024:.1f} MB / {total_size / 1024 / 1024:.1f} MB ({percent:.1f}%)", flush=True)

try:
    urllib.request.urlretrieve(URL, INSTALLER_PATH, reporthook=report_progress)
    print(f"\n[+] Obsidian 安装包下载完成: {INSTALLER_PATH} (大小: {os.path.getsize(INSTALLER_PATH) / 1024 / 1024:.1f} MB)")
    
    print("[*] 正在执行静默安装 (/S)...")
    p = subprocess.run([INSTALLER_PATH, "/S"], capture_output=True, timeout=60)
    print(f"[+] 安装进程退出码: {p.returncode}")
    time.sleep(3)
    
    # 查找 Obsidian.exe 安装位置
    possible_paths = [
        os.path.expandvars(r"%LOCALAPPDATA%\Obsidian\Obsidian.exe"),
        os.path.expandvars(r"%PROGRAMFILES%\Obsidian\Obsidian.exe")
    ]
    for pth in possible_paths:
        if os.path.exists(pth):
            print(f"🎉🎉🎉 Obsidian 成功安装并就绪: {pth}")
            break
except Exception as e:
    print(f"[-] 下载/安装异常: {e}")
