"""
每周 GitHub 高星 AI/开源项目深度脱水周报
执行频率: 每周一上午 09:00 或按需触发
推送频道: Telegram 话题 4 (GitHub 高星)
"""

import sys, os, time, json, urllib.request, urllib.parse, requests

# 确保在 Windows 控制台输出 UTF-8 不报错
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
sys.path.append(r'C:\Users\zzx05\Hermes-Automation\services')
from wool_radar import send_telegram_text, TOPIC_GITHUB_ID
from config_lib import BOT_TOKEN, CHAT_ID, GATEWAY_URL, GATEWAY_KEY, GATEWAY_MODEL

# 动态自动挂载 keys_pool.json 中最强活态节点 (优先 ZeroGate/ZCode 25亿Token池)
def get_best_llm_node():
    pool_file = r"C:\Users\zzx05\Hermes-Automation\config\keys_pool.json"
    if os.path.exists(pool_file):
        try:
            with open(pool_file, "r", encoding="utf-8") as f:
                pool = json.load(f)
                alive = [x for x in pool if x.get("is_alive", True)]
                if alive:
                    for node in alive:
                        if "zerogate" in (node.get("name") or "").lower() or "zcode" in (node.get("name") or "").lower():
                            burl = node.get("base_url", "").rstrip("/")
                            return f"{burl}/chat/completions", node.get("api_key"), node.get("default_model") or "zcode/glm-5.3-flash"
                    n = alive[0]
                    burl = n.get("base_url", "").rstrip("/")
                    return f"{burl}/chat/completions", n.get("api_key"), n.get("default_model") or "gpt-4o-mini"
        except Exception:
            pass
    return f"{GATEWAY_URL.rstrip('/')}/chat/completions", GATEWAY_KEY, GATEWAY_MODEL

API_URL, API_KEY, MODEL_NAME = get_best_llm_node()

def get_weekly_trending():
    """通过 GitHub API 搜索本周星标增长最猛的 AI/Agent/LLM 项目"""
    # 搜索最近 7 天创建或最火的 AI 仓库
    date_since = time.strftime("%Y-%m-%d", time.localtime(time.time() - 7 * 86400))
    query = f"stars:>500 created:>{date_since} (ai OR llm OR agent OR automation)"
    url = f"https://api.github.com/search/repositories?q={urllib.parse.quote(query)}&sort=stars&order=desc&per_page=5"
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("items", [])
    except Exception as e:
        print("[-] GitHub API 搜索异常:", e)
        # 兜底查询通用 trending 热门高星
        fallback_url = "https://api.github.com/search/repositories?q=stars:>1000+topic:ai&sort=updated&order=desc&per_page=5"
        try:
            req = urllib.request.Request(fallback_url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data.get("items", [])
        except Exception:
            return []

def get_repo_readme(full_name):
    """抓取仓库的 README 文本"""
    url = f"https://api.github.com/repos/{full_name}/readme"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "application/vnd.github.v3.raw"
    }
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.read().decode("utf-8", errors="ignore")[:3000]
    except Exception:
        return ""

def summarize_with_ai(repo):
    """用反代模型深度精读并脱水"""
    readme_text = get_repo_readme(repo["full_name"])
    
    prompt = (
        f"请作为资深技术架构师，对以下本周 GitHub 爆火项目进行【深度脱水解析】：\n\n"
        f"项目名: {repo['full_name']}\n"
        f"描述: {repo.get('description', '')}\n"
        f"Stars: {repo.get('stargazers_count', 0)}\n"
        f"README 核心片段:\n{readme_text[:2000]}\n\n"
        f"请用极其精炼、干货的中文输出以下 4 个维度（每个维度 1-2 句话，拒绝空话套话）：\n"
        f"1. 🎯 解决什么核心痛点？\n"
        f"2. ⚡ 核心架构与技术亮点？\n"
        f"3. 💰 实用与商业/落地价值？\n"
        f"4. 🛠️ 体验与部署门槛？\n"
    )

    try:
        use_proxies = None if any(h in API_URL for h in ["192.168.", "127.0.0.1", "localhost"]) else {"http": "http://127.0.0.1:7897", "https": "http://127.0.0.1:7897"}
        r = requests.post(
            API_URL,
            headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
            json={
                "model": MODEL_NAME,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 500,
                "temperature": 0.2
            },
            proxies=use_proxies,
            timeout=20
        )
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print("[-] AI 分析异常:", e)
    return repo.get("description", "无描述")

def generate_weekly_report():
    print("==================================================")
    print("📊 正在生成本周 GitHub 高星 AI 脱水周报...")
    print("==================================================")
    
    repos = get_weekly_trending()
    if not repos:
        print("[-] 未能抓取到仓库列表")
        return

    report_lines = [
        f"🌟 *【本周 GitHub 精选高星 AI 深度周报】*",
        f"📅 时间基准: {time.strftime('%Y-%m-%d')}\n"
    ]

    for idx, repo in enumerate(repos[:4], 1):
        print(f"[{idx}] 正在深度精读项目: {repo['full_name']} (Stars: {repo['stargazers_count']})...")
        ai_summary = summarize_with_ai(repo)
        
        block = (
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"🔥 *No.{idx} [{repo['name']}]({repo['html_url']})* ⭐ {repo['stargazers_count']}\n"
            f"{ai_summary}\n"
            f"🔗 链接: {repo['html_url']}"
        )
        report_lines.append(block)

    final_report = "\n\n".join(report_lines)
    
    # 推送至 Telegram 话题 4
    send_telegram_text(TOPIC_GITHUB_ID, final_report)
    print("🚀 周报已成功推送到 Telegram 话题 4！")

if __name__ == "__main__":
    generate_weekly_report()
