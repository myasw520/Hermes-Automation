import requests
import os
import sys
import time

direct_url = "https://release-assets.githubusercontent.com/github-production-release-asset/262342594/26e4bceb-a34e-40c9-bbbd-7d06064a0939?sp=r&sv=2018-11-09&sr=b&spr=https&se=2026-10-21T03%3A34%3A39Z&rscd=attachment%3B+filename%3DObsidian-1.14.4.exe&rsct=application%2Foctet-stream&skoid=96c2d410-5711-43a1-aedd-ab1947aa7ab0&sktid=398a6654-997b-47e9-b12b-9515b896b4de&skt=2026-10-21T02%3A34%3A28Z&ske=2026-10-21T03%3A34%3A39Z&sks=b&skv=2018-11-09&sig=UyHvXe12HpqYStqIX3WaouUmI0WF%2BpAJGeSz4Esa7yQ%3D&jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmVsZWFzZS1hc3NldHMuZ2l0aHVidXNlcmNvbnRlbnQuY29tIiwia2V5Ijoia2V5MSIsImV4cCI6MTc5MjU1NDU3MiwibmJmIjoxNzkyNTUwOTcyLCJwYXRoIjoicmVsZWFzZWFzc2V0cHJvZHVjdGlvbi5ibG9iLmNvcmUud2luZG93cy5uZXQifQ.2jzT1yOmyE7WxLYtNdPvqp2p-TrJJwEnu3OwJB11HAE&response-content-disposition=attachment%3B%20filename%3DObsidian-1.14.4.exe&response-content-type=application%2Foctet-stream"

save_path = r"C:\Users\zzx05\Downloads\ObsidianSetup.exe"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
}
proxies = {
    'http': 'http://127.0.0.1:7897',
    'https': 'http://127.0.0.1:7897'
}

total_size = 341331008
block_size = 15 * 1024 * 1024 # 15 MB chunks

existing_size = os.path.getsize(save_path) if os.path.exists(save_path) else 0
print(f"Resuming from {existing_size / (1024*1024):.2f} MB...", flush=True)

with open(save_path, 'ab' if existing_size > 0 else 'wb') as f:
    start = existing_size
    while start < total_size:
        end = min(start + block_size - 1, total_size - 1)
        h = headers.copy()
        h['Range'] = f"bytes={start}-{end}"
        
        success = False
        for attempt in range(4):
            try:
                r = requests.get(direct_url, headers=h, proxies=proxies, timeout=20)
                if r.status_code in [200, 206]:
                    f.write(r.content)
                    f.flush()
                    start = end + 1
                    pct = (start / total_size) * 100
                    print(f"Downloaded: {start/(1024*1024):.1f} MB / {total_size/(1024*1024):.1f} MB ({pct:.1f}%)", flush=True)
                    success = True
                    break
                else:
                    print(f"Status {r.status_code}, retrying...", flush=True)
            except Exception as e:
                print(f"Retry {attempt+1} on {start}: {e}", flush=True)
                time.sleep(1)
        
        if not success:
            print("Failed block. Exiting.", flush=True)
            break

final_size = os.path.getsize(save_path)
print(f"Download complete: {final_size == total_size} (Final: {final_size} bytes)", flush=True)
