import requests
import os
import sys
import time

proxies = {
    'http': 'http://127.0.0.1:7897',
    'https': 'http://127.0.0.1:7897'
}
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

initial_url = "https://github.com/obsidianmd/obsidian-releases/releases/download/v1.14.4/Obsidian-1.14.4.exe"
save_path = r"C:\Users\zzx05\Downloads\ObsidianSetup.exe"

print("Resolving final download redirect URL...", flush=True)
r = requests.head(initial_url, headers=headers, proxies=proxies, allow_redirects=True, timeout=20)
print(f"Status: {r.status_code}, Final URL: {r.url[:60]}...", flush=True)

total_size = int(r.headers.get('content-length', 341331008))
print(f"Total size: {total_size / (1024*1024):.2f} MB", flush=True)

final_url = r.url
block_size = 15 * 1024 * 1024 # 15 MB per block

# Determine existing progress
existing_size = os.path.getsize(save_path) if os.path.exists(save_path) else 0
print(f"Existing file size: {existing_size / (1024*1024):.2f} MB", flush=True)

start_offset = existing_size
mode = 'ab' if existing_size > 0 else 'wb'

with open(save_path, mode) as f:
    while start_offset < total_size:
        end_offset = min(start_offset + block_size - 1, total_size - 1)
        cur_headers = headers.copy()
        cur_headers['Range'] = f"bytes={start_offset}-{end_offset}"
        
        success = False
        for retry in range(5):
            try:
                # Direct download for this specific chunk
                resp = requests.get(final_url, headers=cur_headers, proxies=proxies, timeout=25)
                if resp.status_code in [200, 206]:
                    f.write(resp.content)
                    f.flush()
                    start_offset = end_offset + 1
                    pct = (start_offset / total_size) * 100
                    print(f"Downloaded chunk up to {start_offset/(1024*1024):.1f} MB / {total_size/(1024*1024):.1f} MB ({pct:.1f}%)", flush=True)
                    success = True
                    break
                else:
                    print(f"Bad status code {resp.status_code}, retrying...", flush=True)
            except Exception as e:
                print(f"Chunk error at {start_offset}: {e}. Retrying...", flush=True)
                time.sleep(1)
        
        if not success:
            print("Failed to download block after 5 attempts.", flush=True)
            break

final_size = os.path.getsize(save_path)
print(f"Finished. Final size: {final_size / (1024*1024):.2f} MB of {total_size / (1024*1024):.2f} MB", flush=True)
