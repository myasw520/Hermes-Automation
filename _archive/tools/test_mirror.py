import requests
import sys

mirrors = [
    'https://mirror.ghproxy.com/https://github.com/obsidianmd/obsidian-releases/releases/download/v1.14.4/Obsidian-1.14.4.exe',
    'https://gh-proxy.com/https://github.com/obsidianmd/obsidian-releases/releases/download/v1.14.4/Obsidian-1.14.4.exe',
    'https://github.com/obsidianmd/obsidian-releases/releases/download/v1.14.4/Obsidian-1.14.4.exe',
]

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

for m in mirrors:
    print(f"Testing: {m} (direct without proxy)...")
    try:
        r = requests.head(m, headers=headers, timeout=5, allow_redirects=True)
        print(f"Direct Status: {r.status_code}, Length: {r.headers.get('content-length')}")
        if r.status_code == 200:
            print("Found working direct mirror:", m)
            sys.exit(0)
    except Exception as e:
        print(f"Direct failed: {e}")

# Try with local proxy
proxies = {'http': 'http://127.0.0.1:7897', 'https': 'http://127.0.0.1:7897'}
for m in mirrors:
    print(f"Testing with proxy: {m}...")
    try:
        r = requests.head(m, headers=headers, proxies=proxies, timeout=5, allow_redirects=True)
        print(f"Proxy Status: {r.status_code}, Length: {r.headers.get('content-length')}")
    except Exception as e:
        print(f"Proxy failed: {e}")
