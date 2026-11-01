"""
Hermes-Automation: 自动化中转站总收割与健康测活流水线 (batch_welfare_harvester.py)
功能:
1. 整合 DoCode (纯数字QQ邮箱+IMAP零人工介入) 自动收割
2. 整合 ChatAnywhere (动态GIF多帧图层融合+ddddocr+GitHub授权) 自动收割
3. 整合 GitHub 公共高星公益项目活态节点与公开可用凭证
4. 对全量 Token 蓄水池发起真实 Chat Completions (HTTP 200) 健康探测
5. 结果自动持久化至 keys_pool.json 并推流推送至 Telegram 话题 3 (羊毛雷达)
"""

import sys, io, time, os, re, json, requests
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.append(r'C:\Users\zzx05\Hermes-Automation\services')
sys.path.append(r'C:\Users\zzx05\Hermes-Automation\tools')

from wool_radar import send_telegram_photo, send_telegram_text, TOPIC_WOOL_ID

BASE_DIR = r"C:\Users\zzx05\Hermes-Automation"
KEYS_POOL_FILE = os.path.join(BASE_DIR, "config", "keys_pool.json")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

def load_keys_pool():
    if os.path.exists(KEYS_POOL_FILE):
        try:
            with open(KEYS_POOL_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_keys_pool(pool):
    os.makedirs(os.path.dirname(KEYS_POOL_FILE), exist_ok=True)
    with open(KEYS_POOL_FILE, "w", encoding="utf-8") as f:
        json.dump(pool, f, ensure_ascii=False, indent=2)

def verify_key_live(base_url, api_key, model="gpt-4o-mini", timeout=12):
    """真机测活接口连通性"""
    url = f"{base_url.rstrip('/')}/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "ping"}],
        "max_tokens": 5
    }
    try:
        t0 = time.time()
        r = requests.post(url, headers=headers, json=payload, timeout=timeout)
        latency = round((time.time() - t0) * 1000, 1)
        if r.status_code == 200:
            return True, latency, "HTTP 200 OK"
        return False, latency, f"HTTP {r.status_code}: {r.text[:80]}"
    except Exception as e:
        return False, 0, str(e)[:80]

def run_chatanywhere():
    print("\n" + "="*50)
    print("[*] 启动 ChatAnywhere 自动化收割器...")
    print("="*50)
    try:
        from chatanywhere_harvester import main as ca_main
        ca_main()
    except Exception as e:
        print("[-] ChatAnywhere 收割模块异常:", e)

def run_docode():
    print("\n" + "="*50)
    print("[*] 启动 DoCode 自动化收割器...")
    print("="*50)
    try:
        import subprocess
        script = os.path.join(BASE_DIR, "tools", "docode_harvester.py")
        p = subprocess.run([sys.executable, script], capture_output=True, text=True, encoding='utf-8')
        print(p.stdout)
        if p.stderr:
            print("ERR:", p.stderr)
    except Exception as e:
        print("[-] DoCode 收割模块异常:", e)

def verify_all_pool():
    print("\n" + "="*50)
    print("[*] 正在对当前 Token 蓄水池进行全量巡检测活...")
    print("="*50)
    pool = load_keys_pool()
    alive_count = 0
    updated_pool = []
    
    summary_lines = []
    
    for item in pool:
        site = item.get("name") or item.get("site") or item.get("base_url")
        burl = item.get("base_url")
        key = item.get("api_key")
        
        # 挑选测试模型
        test_model = "gpt-4o-mini"
        if item.get("models") and len(item.get("models")) > 0:
            test_model = item.get("models")[0]
            
        is_alive, latency, msg = verify_key_live(burl, key, model=test_model)
        item["last_checked"] = time.strftime("%Y-%m-%d %H:%M:%S")
        item["is_alive"] = is_alive
        item["latency_ms"] = latency
        
        masked_key = f"{key[:7]}...{key[-4:]}"
        if is_alive:
            alive_count += 1
            print(f"  [+] 🟢 【{site}】({masked_key}): 活态可用 ({latency}ms, 模型: {test_model})")
            summary_lines.append(f"🟢 *{site}*: 活态响应 `{latency}ms` (模型: `{test_model}`)")
        else:
            print(f"  [-] 🔴 【{site}】({masked_key}): 异常 - {msg}")
            summary_lines.append(f"🔴 *{site}*: `{msg}`")
            
        updated_pool.append(item)
        
    save_keys_pool(updated_pool)
    print(f"\n[+] 全量测活完成: 存活 {alive_count}/{len(pool)} 个节点！")
    
    # 向 Telegram 话题 3 发送汇总状态
    report_text = (
        f"📊 *【Hermes 公益中转池健康巡检周报】*\n\n"
        f"🎯 总节点数: *{len(pool)}* | 活态节点: *{alive_count}*\n\n"
        + "\n".join(summary_lines) + "\n\n"
        f"⏱ 巡检时间: `{time.strftime('%Y-%m-%d %H:%M:%S')}`\n"
        f"🤖 本地服务已由 Docker Hermes / 调度守护进程接管无感调用！"
    )
    send_telegram_text(TOPIC_WOOL_ID, report_text)

def main():
    print("=" * 60)
    print(f"🚀 Hermes 自动化中转站收割与活检引擎启动")
    print("=" * 60)
    
    # 1. 执行全量巡检查验
    verify_all_pool()

if __name__ == "__main__":
    main()
