import requests
import os
import time

url = "https://github.com/obsidianmd/obsidian-releases/releases/download/v1.14.4/Obsidian-1.14.4.exe"
save_path = r"C:\Users\zzx05\Downloads\ObsidianSetup.exe"

proxies = {
    'http': 'http://127.0.0.1:7897',
    'https': 'http://127.0.0.1:7897'
}
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

max_retries = 30
retry_count = 0

while retry_count < max_retries:
    existing_size = os.path.getsize(save_path) if os.path.exists(save_path) else 0
    cur_headers = headers.copy()
    if existing_size > 0:
        cur_headers['Range'] = f"bytes={existing_size}-"
        print(f"Resuming download from byte {existing_size} ({existing_size/(1024*1024):.2f} MB)...")
    else:
        print("Starting fresh download...")

    try:
        with requests.get(url, headers=cur_headers, proxies=proxies, stream=True, timeout=25) as resp:
            if resp.status_code == 416: # Range not satisfiable (already finished)
                print("Download already complete!")
                break
            resp.raise_for_status()

            # Handle total size
            if resp.status_code == 206:
                content_range = resp.headers.get('content-range', '')
                total_size = int(content_range.split('/')[-1]) if '/' in content_range else existing_size + int(resp.headers.get('content-length', 0))
            else:
                total_size = int(resp.headers.get('content-length', 0))
                existing_size = 0

            mode = 'ab' if existing_size > 0 else 'wb'
            with open(save_path, mode) as f:
                downloaded = existing_size
                for chunk in resp.iter_content(chunk_size=1024*1024):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        pct = (downloaded / total_size) * 100 if total_size else 0
                        print(f"Progress: {downloaded/(1024*1024):.1f} MB / {total_size/(1024*1024):.1f} MB ({pct:.1f}%)", end='\r')

            final_size = os.path.getsize(save_path)
            if final_size >= total_size:
                print(f"\nDownload fully complete! Total size: {final_size/(1024*1024):.2f} MB")
                break

    except Exception as e:
        print(f"\nConnection hiccup: {e}. Retrying in 2 seconds...")
        retry_count += 1
        time.sleep(2)

print("Finished download process.")
