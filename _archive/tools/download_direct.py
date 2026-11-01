import requests
import os
import time

url = "https://github.com/obsidianmd/obsidian-releases/releases/download/v1.14.4/Obsidian-1.14.4.exe"
save_path = r"C:\Users\zzx05\Downloads\ObsidianSetup.exe"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

max_retries = 20
retry_count = 0

print("Starting direct download (no proxy)...")

while retry_count < max_retries:
    existing_size = os.path.getsize(save_path) if os.path.exists(save_path) else 0
    cur_headers = headers.copy()
    if existing_size > 0:
        cur_headers['Range'] = f"bytes={existing_size}-"
        print(f"Resuming download from byte {existing_size} ({existing_size/(1024*1024):.2f} MB)...", flush=True)
    else:
        print("Starting fresh download...", flush=True)

    try:
        # Note: proxies=None to download directly
        with requests.get(url, headers=cur_headers, stream=True, timeout=30) as resp:
            if resp.status_code == 416: # Completed
                print("Download completed!", flush=True)
                break
            resp.raise_for_status()

            if resp.status_code == 206:
                content_range = resp.headers.get('content-range', '')
                total_size = int(content_range.split('/')[-1]) if '/' in content_range else existing_size + int(resp.headers.get('content-length', 0))
            else:
                total_size = int(resp.headers.get('content-length', 0))
                existing_size = 0

            mode = 'ab' if existing_size > 0 else 'wb'
            with open(save_path, mode) as f:
                downloaded = existing_size
                last_report = time.time()
                for chunk in resp.iter_content(chunk_size=1024*1024):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if time.time() - last_report > 1.0 or downloaded >= total_size:
                            pct = (downloaded / total_size) * 100 if total_size else 0
                            print(f"Progress: {downloaded/(1024*1024):.1f} MB / {total_size/(1024*1024):.1f} MB ({pct:.1f}%)", flush=True)
                            last_report = time.time()

            final_size = os.path.getsize(save_path)
            if final_size >= total_size:
                print(f"\nDownload fully complete! Total size: {final_size/(1024*1024):.2f} MB", flush=True)
                break

    except Exception as e:
        print(f"\nTransient error: {e}. Retrying in 2 seconds...", flush=True)
        retry_count += 1
        time.sleep(2)

print("Finished download script.", flush=True)
