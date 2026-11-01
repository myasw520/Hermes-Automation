import requests
import re
import os
import sys

proxies = {
    'http': 'http://127.0.0.1:7897',
    'https': 'http://127.0.0.1:7897'
}
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

print("Fetching obsidian.md/download...")
try:
    r = requests.get('https://obsidian.md/download', proxies=proxies, headers=headers, timeout=20)
    print("Page status:", r.status_code)
    # Search for windows exe download link
    # Usually obsidian has direct link like https://github.com/obsidianmd/obsidian-releases/releases/download/.../Obsidian-*.exe
    # Or https://github.com/...
    matches = re.findall(r'https://github\.com/obsidianmd/obsidian-releases/releases/download/[^"\'<>\s]+\.exe', r.text)
    if matches:
        print("Found URL:", matches[0])
        exe_url = matches[0]
    else:
        # Fallback to direct release URL
        print("Finding all github release links...")
        matches2 = re.findall(r'https://[a-zA-Z0-9_\.\-/]+Obsidian[^"\'<>\s]*\.exe', r.text)
        print("Matches:", matches2)
        if matches2:
            exe_url = matches2[0]
        else:
            exe_url = "https://github.com/obsidianmd/obsidian-releases/releases/download/v1.7.7/Obsidian-1.7.7.exe"
except Exception as e:
    print("Error fetching page:", e)
    exe_url = "https://github.com/obsidianmd/obsidian-releases/releases/download/v1.7.7/Obsidian-1.7.7.exe"

print(f"Target download URL: {exe_url}")
save_path = r"C:\Users\zzx05\Downloads\ObsidianSetup.exe"

print(f"Starting chunked stream download to {save_path}...")
try:
    with requests.get(exe_url, proxies=proxies, headers=headers, stream=True, timeout=30) as resp:
        resp.raise_for_status()
        total_size = int(resp.headers.get('content-length', 0))
        print(f"Total size: {total_size / (1024*1024):.2f} MB")
        downloaded = 0
        with open(save_path, 'wb') as f:
            for chunk in resp.iter_content(chunk_size=1024*1024):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    print(f"Downloaded: {downloaded / (1024*1024):.1f} MB / {total_size / (1024*1024):.1f} MB ({(downloaded/total_size)*100:.1f}%)", end='\r')
        print(f"\nSuccessfully downloaded Obsidian to {save_path}")
except Exception as e:
    print(f"\nDownload error: {e}")
