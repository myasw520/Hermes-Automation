# -*- coding: utf-8 -*-
"""
Hermes-Automation 统一配置加载库 (config_lib.py)
================================================
单一事实来源：从项目根 .env 读取凭证并注入 os.environ，向所有脚本暴露常量。
用法（tools/ 或 services/ 下的脚本）:
    from config_lib import BOT_TOKEN, CHAT_ID, TOPIC_WOOL_ID, GATEWAY_URL, GATEWAY_KEY
注意:
- 本文件不含任何明文密钥；密钥只存放在 .env（已被 .gitignore 排除）。
- .env 缺失时回退到 os.environ（允许外部环境变量注入），再缺失则取空值并打印告警。
"""
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load_dotenv(path):
    """极简 .env 解析器（不依赖 python-dotenv），KEY=VALUE 按行读取，# 开头为注释。"""
    loaded = {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            for raw in f:
                line = raw.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key and key not in os.environ:
                    os.environ[key] = value
                loaded[key] = value
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"[config_lib] 解析 {path} 失败: {e}", file=sys.stderr)
    return loaded


_load_dotenv(os.path.join(PROJECT_ROOT, ".env"))


def _get(name, warn=True):
    value = os.environ.get(name, "")
    if not value and warn:
        print(f"[config_lib] 缺少环境变量 {name}，请检查项目根 .env", file=sys.stderr)
    return value


# ---------- Telegram ----------
BOT_TOKEN = _get("TELEGRAM_BOT_TOKEN")
CHAT_ID = _get("TELEGRAM_CHAT_ID")
TOPIC_WOOL_ID = int(_get("TELEGRAM_TOPIC_WOOL", warn=False) or 3)
TOPIC_GITHUB_ID = int(_get("TELEGRAM_TOPIC_GITHUB", warn=False) or 4)
TOPIC_CHAT_ID = int(_get("TELEGRAM_TOPIC_CHAT", warn=False) or 5)

# ---------- Hermes Agent (Docker) ----------
HERMES_API_URL = _get("HERMES_API_URL", warn=False)
HERMES_API_KEY = _get("HERMES_API_KEY", warn=False)

# ---------- ZeroGate ZCode 网关 (LLM 兜底节点) ----------
GATEWAY_URL = _get("OPENAI_BASE_URL", warn=False)
GATEWAY_KEY = _get("OPENAI_API_KEY", warn=False)
GATEWAY_MODEL = _get("FLASH_MODEL", warn=False) or "zcode/glm-5.3-flash"

# ---------- 守护进程 API 门禁 ----------
# 访问 /keys、/data 等敏感接口需要携带 ?token=<API_ACCESS_TOKEN>
API_ACCESS_TOKEN = _get("API_ACCESS_TOKEN", warn=False)

# ---------- 邮箱接码 (mail_receiver) ----------
GMAIL_USER = _get("GMAIL_USER", warn=False)
GMAIL_PASS = _get("GMAIL_PASS", warn=False)
QQ_USER = _get("QQ_USER", warn=False)
QQ_PASS = _get("QQ_PASS", warn=False)

# ---------- 注册 / 下载 ----------
REGISTER_PASSWORD = _get("REGISTER_PASSWORD", warn=False)
GITHUB_TOKEN = _get("GITHUB_TOKEN", warn=False)
