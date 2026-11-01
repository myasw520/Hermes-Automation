import sys, io, time, os, re, json, urllib.request
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.append(r'C:\Users\zzx05\Hermes-Automation\services')
sys.path.append(r'C:\Users\zzx05\Hermes-Automation\tools')

from tg_notify import send_notify

KEYS_POOL_FILE = r"C:\Users\zzx05\Hermes-Automation\config\keys_pool.json"
PROXY = "http://127.0.0.1:7897"

def fetch_github_free_api_sources():
    """从 GitHub 公开知名公益项目中拉取真实的免费中转站与可用 Key"""
    print("[1] 正在从 GitHub 开发者开源社区检索公网免费 API 节点...")
    sources = [
        "https://raw.githubusercontent.com/chatanywhere/GPT_API_free/main/README.md",
    ]
    
    found_endpoints = []
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({'https': PROXY, 'http': PROXY}))
    
    for url in sources:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with opener.open(req, timeout=10) as r:
                text = r.read().decode('utf-8')
                
                # 提取其中的免费 API 转发地址
                base_urls = re.findall(r'https?://[a-zA-Z0-9\-\.]+(?:/v1)?', text)
                for b in base_urls:
                    if any(k in b for k in ["chatanywhere", "api.chat", "api."]) and "github.com" not in b:
                        clean_url = b.rstrip('/')
                        if not clean_url.endswith('/v1'):
                            clean_url += '/v1'
                        if clean_url not in found_endpoints:
                            found_endpoints.append(clean_url)
                            
                # 提取公开附带的测试/公益 Key
                keys = re.findall(r'sk-[a-zA-Z0-9]{32,64}', text)
                print(f"[+] 从 {url} 提取到 {len(found_endpoints)} 个转发节点，{len(keys)} 个公开可用凭证！")
                return found_endpoints, keys
        except Exception as e:
            print(f"[-] 抓取来源异常 {url}: {e}")
            
    # 备用知名国内免翻/公网可达公益中转节点
    return ["https://api.chatanywhere.tech/v1", "https://api.chatanywhere.org/v1"], []

def test_and_verify_key(base_url, api_key, model="gpt-4o-mini"):
    """对抓取到的真实公网 Key 发起真机测活"""
    print(f"[*] 正在对公网节点发测试请求: {base_url} (模型: {model}) ...")
    test_url = f"{base_url.rstrip('/')}/chat/completions"
    
    payload = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": "请只回复两个字：收到"}],
        "max_tokens": 10
    }).encode("utf-8")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({'https': PROXY, 'http': PROXY}))
    start_t = time.time()
    try:
        req = urllib.request.Request(test_url, data=payload, headers=headers)
        with opener.open(req, timeout=15) as resp:
            latency = round((time.time() - start_t) * 1000, 1)
            data = json.loads(resp.read().decode("utf-8"))
            reply = data["choices"][0]["message"]["content"].strip()
            print(f"🎉 测活大成功！响应延迟: {latency}ms | 真实回复: {reply}")
            return True, latency, reply
    except Exception as e:
        print(f"[-] 该 Key 测活失败或额度已耗尽: {e}")
        return False, 0, ""

def save_to_pool(base_url, api_key, latency, note=""):
    pool = []
    if os.path.exists(KEYS_POOL_FILE):
        try:
            with open(KEYS_POOL_FILE, "r", encoding="utf-8") as f:
                pool = json.load(f)
        except Exception:
            pool = []
            
    pool.append({
        "base_url": base_url,
        "api_key": api_key,
        "latency_ms": latency,
        "note": note,
        "verified_at": time.strftime("%Y-%m-%d %H:%M:%S")
    })
    
    with open(KEYS_POOL_FILE, "w", encoding="utf-8") as f:
        json.dump(pool, f, ensure_ascii=False, indent=2)
    print(f"[+] 真实有效 Key 已入库: {KEYS_POOL_FILE}")

def run_harvest():
    print("==================================================")
    print("🚀 启动公网真实公益 API 自动收割与测活流水线...")
    print("==================================================")
    
    endpoints, keys = fetch_github_free_api_sources()
    
    verified_count = 0
    
    # 遍历测活
    for base in endpoints[:3]:
        for k in keys[:3]:
            ok, lat, reply = test_and_verify_key(base, k)
            if ok:
                verified_count += 1
                save_to_pool(base, k, lat, "GitHub 公益项目自动验证")
                
                # 推送捷报到 Telegram 话题 3
                msg = (
                    f"🎉 *【成功捕获一枚公网在线可用 API Key】*\n\n"
                    f"🌐 *转发地址*: `{base}`\n"
                    f"🔑 *API Key*: `{k}`\n"
                    f"⚡ *实测延迟*: `{lat} ms`\n"
                    f"💬 *实测回复*: {reply}\n\n"
                    f"已收录进本地 Token 池，随时可调配使用！"
                )
                send_notify(msg, topic="3")
                print("[+] 已推送到 Telegram 羊毛情报话题！")
                break
        if verified_count > 0:
            break
            
    if verified_count == 0:
        print("[-] 本轮抓取的公网临时公开 Key 可能已达单日调用上限，稍后可自动换源轮询。")

if __name__ == "__main__":
    run_harvest()
