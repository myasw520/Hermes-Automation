import time
import email
import email.utils
import imaplib
import re
import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# ================= 配置区 =================
# 邮箱凭证统一从项目根 .env 读取（config_lib），不再硬编码
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from config_lib import GMAIL_USER, GMAIL_PASS, QQ_USER, QQ_PASS

GMAIL_HOST = "imap.gmail.com"
QQ_HOST = "imap.qq.com"

HTTP_PORT = 7864
# ==========================================

def get_latest_code(account="gmail", since_timestamp=0, max_wait_seconds=60):
    """
    等待并抓取自 since_timestamp 之后到达的新验证码
    :param account: 'gmail' 或 'qq'
    :param since_timestamp: 点击网页发送验证码的时间戳 (time.time())
    :param max_wait_seconds: 最长等待秒数
    :return: (code, subject, sender, timestamp) 或 (None, "", "", 0)
    """
    if account.lower() == "gmail":
        host, user, pwd = GMAIL_HOST, GMAIL_USER, GMAIL_PASS
    else:
        host, user, pwd = QQ_HOST, QQ_USER, QQ_PASS

    start_wait = time.time()
    # 允许 5 秒本地与邮件服务器时钟误差
    effective_since = since_timestamp - 5 if since_timestamp > 0 else 0

    print(f"[*] 正在监听 {account} 新邮件 (时间基准: {time.strftime('%H:%M:%S', time.localtime(effective_since))})...")

    while time.time() - start_wait < max_wait_seconds:
        mail = None
        try:
            mail = imaplib.IMAP4_SSL(host, 993)
            mail.login(user, pwd)
            mail.select("INBOX")

            status, data = mail.search(None, "ALL")
            if status == "OK" and data[0]:
                ids = data[0].split()
                # 倒序检查最新 5 封邮件
                for eid in reversed(ids[-5:]):
                    _, msg_data = mail.fetch(eid, "(RFC822)")
                    if not msg_data or not msg_data[0]:
                        continue
                        
                    msg = email.message_from_bytes(msg_data[0][1])
                    
                    # 1. 严格时间戳校验
                    email_date = msg.get("Date")
                    date_tuple = email.utils.parsedate_tz(email_date)
                    msg_time = email.utils.mktime_tz(date_tuple) if date_tuple else 0

                    if msg_time < effective_since:
                        # 这封邮件比我们点击网页的时间还早，属于旧邮件，直接忽略！
                        continue

                    subject = msg.get("Subject", "")
                    sender = msg.get("From", "")

                    # 2. 提取邮件正文
                    body = ""
                    for part in msg.walk():
                        if part.get_content_type() in ["text/plain", "text/html"]:
                            payload = part.get_payload(decode=True)
                            if payload:
                                body += payload.decode("utf-8", errors="ignore") + "\n"

                    # 3. 提取验证码模式（优先匹配带关键词的，保底匹配纯数字）
                    patterns = [
                        r'(?:code|verification|verify|验证码|校验码)[^\d\n\r]{0,20}(\b\d{4,6}\b)',
                        r'\b(\d{6})\b',
                        r'\b(\d{4})\b'
                    ]
                    
                    target_text = f"{subject}\n{body}"
                    for pat in patterns:
                        match = re.search(pat, target_text, re.IGNORECASE)
                        if match:
                            code = match.group(1)
                            print(f"[+] 成功捕获有效新验证码: {code} | 来自: {sender}")
                            mail.logout()
                            return code, subject, sender, msg_time
            mail.logout()
        except Exception as e:
            # 捕获网络抖动并重试
            pass

        time.sleep(2)

    print(f"[-] 等待验证码超时 ({max_wait_seconds}秒未收到新邮件)")
    return None, "", "", 0

# 兼顾油猴脚本的 HTTP 本地服务 Handler
class CodeServerHandler(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    def do_GET(self):
        if self.path.startswith("/api/code"):
            # 支持通过 query 参数传 ?since=1710000000&account=gmail
            params = {}
            if "?" in self.path:
                query = self.path.split("?", 1)[1]
                params = dict(qc.split("=", 1) for qc in query.split("&") if "=" in qc)

            since_t = float(params.get("since", time.time() - 120)) # 默认最近2分钟
            acc = params.get("account", "gmail")

            code, subj, sender, ts = get_latest_code(account=acc, since_timestamp=since_t, max_wait_seconds=15)
            
            resp = {
                "status": "ok" if code else "waiting",
                "code": code,
                "subject": subj,
                "sender": sender,
                "timestamp": ts
            }
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(resp, ensure_ascii=False).encode("utf-8"))
        else:
            self.send_response(404)
            self._cors()
            self.end_headers()

def start_http_service():
    server = HTTPServer(("0.0.0.0", HTTP_PORT), CodeServerHandler)
    print(f"[*] 验证码本地 HTTP 中继服务已启动: http://127.0.0.1:{HTTP_PORT}")
    server.serve_forever()

if __name__ == "__main__":
    # 单独运行时启动 HTTP 监听
    start_http_service()
