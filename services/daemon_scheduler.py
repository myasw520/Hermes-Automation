"""
Hermes-Automation 自动化中央调度守护进程 (daemon_scheduler.py)
特性:
1. 7x24 小时静默后台运行 (由 pythonw.exe 执行，无任何黑框打扰)
2. 状态持久化 (scheduler_state.json)，即使电脑关机重启也不会错漏或重复执行
3. 严格遵循用户约定的低频、高信噪比排期:
   - GitHub AI 高星脱水研报: 每 7 天一次 (每周一早晨)
   - 官方游戏喜加一: 每 3 天一次 (不错过任何限免)
   - B站硬核技术速递: 每 3 天一次
   - 全网羊毛巡检 (带防送码过滤): 每 6 小时一次
   - 资产池 Key 健康检查与保活: 每 12 小时一次
4. 内置 HTTP REST API (监听 0.0.0.0:28987):
   - 同时作为单实例排他锁
   - 供 Hermes Agent (Docker) 与外部遥控调用:
     * GET  /status : 查看各任务下次执行倒计时与状态
     * GET  /keys   : 获取当前活态 Key 资产池 (敏感: 需 ?token=<API_ACCESS_TOKEN>)
     * GET  /tasks  : 列出支持调度的任务清单
     * POST /trigger/<task_name> 或 GET /trigger?task=<task_name> : 立即手动触发任务
     * GET  /logs   : 获取最近调度日志
     * GET  /data/* : 读取 data 目录 (敏感: 需 ?token=<API_ACCESS_TOKEN>)
"""

import sys
import os
import time
import json
import subprocess
import socket
import threading
from urllib.parse import urlparse, parse_qs, unquote
from http.server import HTTPServer, BaseHTTPRequestHandler

# 保证 Windows 下 pythonw 及无控制台环境下绝不报错
if sys.stdout is None:
    class DummyStream:
        def write(self, s): pass
        def flush(self): pass
        def reconfigure(self, **kwargs): pass
    sys.stdout = DummyStream()
    sys.stderr = DummyStream()
else:
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

BASE_DIR = r"C:\Users\zzx05\Hermes-Automation"
PYTHON_EXE = r"C:\Users\zzx05\AppData\Local\Programs\Python\Python311\python.exe"
STATE_FILE = os.path.join(BASE_DIR, "config", "scheduler_state.json")
LOG_FILE = os.path.join(BASE_DIR, "reports", "scheduler.log")
KEYS_FILE = os.path.join(BASE_DIR, "config", "keys_pool.json")
API_PORT = 28987
START_TIME = time.time()

# 敏感接口（/keys、/data）访问门禁：从项目根 .env 读取 API_ACCESS_TOKEN
sys.path.insert(0, os.path.join(BASE_DIR, "services"))
from config_lib import API_ACCESS_TOKEN as _SENSITIVE_TOKEN


def _check_sensitive_access(qs):
    """校验敏感接口访问令牌；通过返回 None，否则返回错误响应 dict。"""
    provided = qs.get("token", [""])[0]
    if _SENSITIVE_TOKEN and provided == _SENSITIVE_TOKEN:
        return None
    return {"error": "Forbidden: /keys 与 /data 为敏感接口，需携带 ?token=<API_ACCESS_TOKEN>（见项目根 .env）"}

# 任务定义与执行间隔 (单位: 秒)
TASKS = {
    "weekly_github": {
        "name": "GitHub 高星脱水周报",
        "script": os.path.join(BASE_DIR, "tools", "weekly_github_digest.py"),
        "args": [],
        "interval": 7 * 86400  # 7 天一次
    },
    "freegames": {
        "name": "游戏限免喜加一巡检",
        "script": os.path.join(BASE_DIR, "tools", "cn_intel_search.py"),
        "args": ["--freegames"],
        "interval": 3 * 86400  # 3 天一次
    },
    "bili_intel": {
        "name": "B站硬核技术与API速递",
        "script": os.path.join(BASE_DIR, "tools", "cn_intel_search.py"),
        "args": ["--bili", "免费API"],
        "interval": 3 * 86400  # 3 天一次
    },
    "wool_radar": {
        "name": "全网基建羊毛雷达扫描",
        "script": os.path.join(BASE_DIR, "services", "wool_radar.py"),
        "args": ["--once"],
        "interval": 6 * 3600   # 6 小时一次
    },
    "welfare_harvester": {
        "name": "公益中转站活态Key收割与测活",
        "script": os.path.join(BASE_DIR, "tools", "batch_welfare_harvester.py"),
        "args": [],
        "interval": 12 * 3600  # 12 小时一次
    },
    "daily_checkin": {
        "name": "每日中转站自动签到与额度巡检",
        "script": os.path.join(BASE_DIR, "tools", "daily_wool_checkin.py"),
        "args": [],
        "interval": 24 * 3600  # 24 小时一次
    },
    "postgrad_papers": {
        "name": "计算机专硕【408+数二+英二】真题与精解提纯",
        "script": os.path.join(BASE_DIR, "tools", "postgrad_exam_papers_harvester.py"),
        "args": [],
        "interval": 3 * 86400  # 3 天一次更新或按需触发
    },
    "build_print_papers": {
        "name": "生成桌面【考研408】打印店专用全套试卷",
        "script": os.path.join(BASE_DIR, "tools", "fetch_official_full_pdf_papers.py"),
        "args": [],
        "interval": 7 * 86400  # 7 天一次或按需触发
    },
    "xhh_comments_sentinel": {
        "name": "小黑盒文章恶评与带节奏实时巡检",
        "script": os.path.join(BASE_DIR, "tools", "xhh_comment_sentinel.py"),
        "args": [],
        "interval": 600  # 每 10 分钟巡检一次
    },
    "content_inventory": {
        "name": "内容库存每日提醒（推文时效/囤稿/巡检池）",
        "script": os.path.join(BASE_DIR, "tools", "content_inventory.py"),
        "args": [],
        "interval": 86400  # 每日一次，只读扫描 + TG 提醒
    }
    # "xhs_probe": 已完成 214 条有效爆款样本采集并正式交付归档，停止后台周期探测
}

_state_lock = threading.Lock()
_running_tasks = set()
_tasks_lock = threading.Lock()

def log(msg):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    try:
        if sys.stdout is not None:
            print(line)
    except Exception:
        pass
    try:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass

def load_state():
    with _state_lock:
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

def save_state(state):
    with _state_lock:
        try:
            os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
            with open(STATE_FILE, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            log(f"保存调度状态失败: {e}")

def run_task(task_key, task_cfg, state=None):
    with _tasks_lock:
        if task_key in _running_tasks:
            log(f"⚠️ 任务【{task_cfg['name']}】已在运行中，跳过重复调度。")
            return {"task": task_key, "name": task_cfg["name"], "success": False, "output": "任务已在执行中"}
        _running_tasks.add(task_key)

    # 关键修复：触发的第一时间立即更新并持久化 last_run 时间戳
    # 彻底解决 next_run_in_seconds 永远为 0 以及调度器在任务执行期间频繁重复拉起的 Bug
    now_ts = time.time()
    s = load_state()
    s[task_key] = now_ts
    save_state(s)

    log(f"🚀 触发任务: 【{task_cfg['name']}】 ...")
    cmd = [PYTHON_EXE, task_cfg["script"]] + task_cfg["args"]
    res = {"task": task_key, "name": task_cfg["name"], "success": False, "output": ""}
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600,
            encoding="utf-8",
            errors="replace"
        )
        if proc.returncode == 0:
            log(f"✅ 任务【{task_cfg['name']}】执行完毕！")
            res["success"] = True
            res["output"] = (proc.stdout or "")[-500:]
        else:
            err_msg = f"返回码: {proc.returncode}, 错误信息: {proc.stderr[:300]}"
            log(f"[-] 任务【{task_cfg['name']}】异常: {err_msg}")
            res["output"] = err_msg
    except Exception as e:
        err_msg = str(e)
        log(f"[-] 任务【{task_cfg['name']}】抛出异常: {err_msg}")
        res["output"] = err_msg
    finally:
        with _tasks_lock:
            _running_tasks.discard(task_key)
        # 任务结束时再次刷新时间戳
        s = load_state()
        s[task_key] = time.time()
        save_state(s)

    return res


def get_all_xhs_notes():
    data_dir = os.path.join(BASE_DIR, "data")
    notes = []
    if not os.path.exists(data_dir):
        return notes
    for fname in sorted(os.listdir(data_dir)):
        if fname.startswith("notes_") and fname.endswith(".jsonl"):
            fpath = os.path.join(data_dir, fname)
            try:
                with open(fpath, "r", encoding="utf-8", errors="replace") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            item = json.loads(line)
                            if "url" not in item and "note_id" in item:
                                item["url"] = f"https://www.xiaohongshu.com/explore/{item['note_id']}"
                            notes.append(item)
                        except Exception:
                            pass
            except Exception:
                pass
    return notes


class DaemonAPIHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # 屏蔽默认 HTTP 访问终端打扰
        pass

    def _send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = unquote(parsed.path.rstrip("/"))
        qs = parse_qs(parsed.query)

        if path in ("", "/status", "/health"):
            state = load_state()
            now = time.time()
            task_status = {}
            for k, cfg in TASKS.items():
                last_run = state.get(k, 0)
                next_in = max(0, int(cfg["interval"] - (now - last_run))) if last_run > 0 else 0
                task_status[k] = {
                    "name": cfg["name"],
                    "interval_hours": round(cfg["interval"] / 3600, 1),
                    "last_run": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(last_run)) if last_run else "从未执行",
                    "next_run_in_seconds": next_in
                }
            self._send_json({
                "status": "running",
                "service": "Hermes-Automation Host Daemon",
                "uptime_seconds": int(now - START_TIME),
                "running_tasks": list(_running_tasks),
                "tasks": task_status
            })

        elif path == "/keys":
            denied = _check_sensitive_access(qs)
            if denied:
                self._send_json(denied, status=403)
                return
            if os.path.exists(KEYS_FILE):
                try:
                    with open(KEYS_FILE, "r", encoding="utf-8") as f:
                        keys_data = json.load(f)
                    self._send_json({"success": True, "count": len(keys_data), "keys": keys_data})
                    return
                except Exception as e:
                    self._send_json({"error": f"读取Key池失败: {e}"}, status=500)
                    return
            self._send_json({"success": True, "count": 0, "keys": []})

        elif path == "/tasks":
            tasks_list = [{"id": k, "name": v["name"], "interval_hours": round(v["interval"] / 3600, 1)} for k, v in TASKS.items()]
            self._send_json({"tasks": tasks_list})

        elif path == "/trigger":
            task_key = qs.get("task", [""])[0]
            if not task_key or task_key not in TASKS:
                self._send_json({"error": f"无效的任务名称，支持的任务: {list(TASKS.keys())}"}, status=400)
                return
            
            # 是否同步等待结果
            is_sync = qs.get("sync", ["0"])[0] in ("1", "true")
            task_cfg = TASKS[task_key]
            if is_sync:
                res = run_task(task_key, task_cfg)
                self._send_json(res)
            else:
                threading.Thread(target=run_task, args=(task_key, task_cfg), daemon=True).start()
                self._send_json({"success": True, "message": f"任务【{task_cfg['name']}】已异步触发在后台执行"})

        elif path == "/logs":
            lines_count = int(qs.get("n", ["40"])[0])
            if os.path.exists(LOG_FILE):
                try:
                    with open(LOG_FILE, "r", encoding="utf-8", errors="replace") as f:
                        all_lines = f.readlines()
                    self._send_json({"logs": all_lines[-lines_count:]})
                    return
                except Exception as e:
                    self._send_json({"error": str(e)}, status=500)
                    return
            self._send_json({"logs": []})

        elif path in ("/xhs_status", "/xhs_log"):
            xhs_log_file = os.path.join(BASE_DIR, "data", "collection_log.md")
            if os.path.exists(xhs_log_file):
                try:
                    with open(xhs_log_file, "r", encoding="utf-8") as f:
                        self._send_json({"success": True, "report": f.read()})
                    return
                except Exception as e:
                    self._send_json({"error": str(e)}, status=500)
                    return
            self._send_json({"success": False, "message": "尚未生成采集日志"}, status=404)

        elif path in ("/xhs_notes", "/notes", "/xhs_dump"):
            notes = get_all_xhs_notes()
            domain_filter = qs.get("domain", [""])[0].strip()
            if domain_filter:
                notes = [n for n in notes if domain_filter in n.get("domain", "")]
            
            total_count = len(notes)
            offset = max(0, int(qs.get("offset", ["0"])[0]))
            limit_val = int(qs.get("limit", ["100"])[0])
            
            sliced_notes = notes[offset:] if limit_val <= 0 else notes[offset:offset + limit_val]
            self._send_json({
                "success": True,
                "total": total_count,
                "count": len(sliced_notes),
                "offset": offset,
                "limit": limit_val,
                "notes": sliced_notes
            })

        elif path == "/data" or path.startswith("/data/"):
            denied = _check_sensitive_access(qs)
            if denied:
                self._send_json(denied, status=403)
                return
            data_root = os.path.abspath(os.path.join(BASE_DIR, "data"))
            if path in ("/data", "/data/"):
                items = []
                for entry in os.listdir(data_root):
                    epath = os.path.join(data_root, entry)
                    items.append({
                        "name": entry,
                        "is_dir": os.path.isdir(epath),
                        "size": os.path.getsize(epath) if os.path.isfile(epath) else 0
                    })
                self._send_json({"success": True, "data_dir": items})
                return
            
            rel_subpath = path[len("/data/"):].strip("/")
            target_file = os.path.abspath(os.path.join(data_root, rel_subpath))
            # 防路径遍历
            if not target_file.startswith(data_root):
                self._send_json({"error": "Forbidden: Path traversal forbidden"}, status=403)
                return
            if not os.path.exists(target_file):
                self._send_json({"error": f"File not found: {rel_subpath}"}, status=404)
                return
            if os.path.isdir(target_file):
                files = os.listdir(target_file)
                self._send_json({"success": True, "dir": rel_subpath, "files": files})
                return
            try:
                with open(target_file, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
                if target_file.endswith(".jsonl"):
                    items = [json.loads(line) for line in content.splitlines() if line.strip()]
                    self._send_json({"success": True, "file": rel_subpath, "total": len(items), "data": items})
                elif target_file.endswith(".json"):
                    self._send_json({"success": True, "file": rel_subpath, "data": json.loads(content)})
                else:
                    self._send_json({"success": True, "file": rel_subpath, "content": content})
            except Exception as e:
                self._send_json({"error": f"Failed reading file: {e}"}, status=500)

        else:
            self._send_json({"error": f"未知路径: {path}"}, status=404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        if path.startswith("/trigger/"):
            task_key = path.replace("/trigger/", "").strip()
            if task_key not in TASKS:
                self._send_json({"error": f"未知任务: {task_key}，支持: {list(TASKS.keys())}"}, status=400)
                return
            task_cfg = TASKS[task_key]
            threading.Thread(target=run_task, args=(task_key, task_cfg), daemon=True).start()
            self._send_json({"success": True, "message": f"任务【{task_cfg['name']}】已异步触发在后台执行"})
        else:
            self._send_json({"error": "仅支持 POST /trigger/<task_name>"}, status=404)


class ReusableHTTPServer(HTTPServer):
    allow_reuse_address = True

def start_api_server():
    try:
        server = ReusableHTTPServer(("0.0.0.0", API_PORT), DaemonAPIHandler)
        log(f"🌐 调度守护进程 REST API 已就绪: 0.0.0.0:{API_PORT}")
        server.serve_forever()
    except Exception as e:
        log(f"[-] API Server 启动或运行异常: {e}")


def main_loop():
    # 尝试绑定端口以实现单实例排他与对外 API 服务
    try:
        t_api = threading.Thread(target=start_api_server, daemon=True)
        t_api.start()
        time.sleep(1)
    except Exception as e:
        log(f"[-] 端口 {API_PORT} 绑定失败或已被占用，确认是否已有实例在跑: {e}")
        sys.exit(0)

    log("==================================================")
    log("🦙 Hermes-Automation 自动化中央调度守护进程已启动！")
    log("==================================================")
    
    state = load_state()
    
    # 首次若无记录，记录当前时间戳防密集轰炸
    now = time.time()
    for k in ["weekly_github", "freegames", "bili_intel"]:
        if k not in state:
            state[k] = now
    save_state(state)

    while True:
        now = time.time()
        current_state = load_state()
        for task_key, task_cfg in TASKS.items():
            last_run = current_state.get(task_key, 0)
            elapsed = now - last_run
            if elapsed >= task_cfg["interval"]:
                run_task(task_key, task_cfg, current_state)
                time.sleep(5)
                
        # 每隔 60 秒检查一次轮询
        time.sleep(60)


if __name__ == "__main__":
    main_loop()
