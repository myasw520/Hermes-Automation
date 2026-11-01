# -*- coding: utf-8 -*-
"""
Hermes 考研独立智能终端助手 (Hermes Terminal Assistant)
- 独立运行，不消耗主会话额度
- 自动挂载 keys_pool.json 稳定高可用中转站密钥 (ChatAnywhere)
- 内置 408 知识库联动、流式响应、多轮对话记忆
"""

import os
import sys
import json
import time
import requests

# Windows 控制台 ANSI 颜色与 UTF-8 编码支持
os.system('')
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stdin, 'reconfigure'):
    sys.stdin.reconfigure(encoding='utf-8')

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

KEYS_POOL_FILE = r"C:\Users\zzx05\Hermes-Automation\config\keys_pool.json"
VAULT_DIR = r"C:\Users\zzx05\Documents\CS408-Knowledge-Vault"

SYSTEM_PROMPT = (
    "你是由 Hermes 自动化引擎驱动的计算机考研（408统考、数学一二、英语一二及择校复试）专属智能辅导专家。\n"
    "你的回答要求：\n"
    "1. 严谨、专业、结构清晰，紧扣考纲要求与命题风格。\n"
    "2. 代码示例默认优先使用规范 C/C++（数据结构手撕算法标准写法）。\n"
    "3. 遇到择校与复试问题，客观指出真实报录比、初复试比例与歧视风险，杜绝套话鸡汤。"
)

def load_active_key():
    if not os.path.exists(KEYS_POOL_FILE):
        return None
    try:
        with open(KEYS_POOL_FILE, 'r', encoding='utf-8') as f:
            pool = json.load(f)
        for item in pool:
            if item.get('is_alive', True) and item.get('base_url'):
                return item
        return pool[0] if pool else None
    except Exception as e:
        print(f"{Colors.RED}[错误] 加载密钥池失败: {e}{Colors.END}")
        return None

def stream_chat(base_url, api_key, model, messages):
    url = f"{base_url.rstrip('/')}/chat/completions"
    headers = {
        'Authorization': f"Bearer {api_key}",
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) HermesAssistant/1.0'
    }
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.5,
        "stream": True
    }
    
    resp = requests.post(url, headers=headers, json=payload, stream=True, timeout=90)
    resp.raise_for_status()
    
    full_text = ""
    for line in resp.iter_lines():
        if not line:
            continue
        line_str = line.decode('utf-8', errors='ignore')
        if line_str.startswith('data: '):
            data_content = line_str[6:].strip()
            if data_content == '[DONE]':
                break
            try:
                chunk = json.loads(data_content)
                delta = chunk.get('choices', [{}])[0].get('delta', {}).get('content', '')
                if delta:
                    full_text += delta
                    sys.stdout.write(delta)
                    sys.stdout.flush()
            except Exception:
                continue
    print()
    return full_text

def list_vault():
    print(f"\n{Colors.CYAN}=== 📂 本地 408 知识库笔记列表 ==={Colors.END}")
    if not os.path.exists(VAULT_DIR):
        print(f"{Colors.RED}知识库目录不存在: {VAULT_DIR}{Colors.END}")
        return
    files = [f for f in os.listdir(VAULT_DIR) if f.endswith('.md')]
    for idx, f in enumerate(files, 1):
        print(f"  [{idx}] {f}")
    print(f"{Colors.CYAN}提示: 输入 /view <编号> 可以快速查阅笔记内容{Colors.END}\n")

def view_note(arg):
    if not os.path.exists(VAULT_DIR):
        return
    files = [f for f in os.listdir(VAULT_DIR) if f.endswith('.md')]
    try:
        idx = int(arg) - 1
        if 0 <= idx < len(files):
            target = os.path.join(VAULT_DIR, files[idx])
            print(f"\n{Colors.GREEN}--- 📄 正在阅读: {files[idx]} ---{Colors.END}")
            with open(target, 'r', encoding='utf-8') as f:
                content = f.read()
            # 打印前 40 行预览
            lines = content.split('\n')
            preview = '\n'.join(lines[:40])
            print(preview)
            if len(lines) > 40:
                print(f"{Colors.YELLOW}\n... (共 {len(lines)} 行，完整内容请在 Obsidian 中查阅){Colors.END}\n")
        else:
            print(f"{Colors.RED}编号超出范围 (1-{len(files)}){Colors.END}")
    except ValueError:
        print(f"{Colors.RED}请输入有效编号，例如 /view 1{Colors.END}")

def main():
    print(f"{Colors.HEADER}{Colors.BOLD}===================================================={Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}   🎓 Hermes 考研 408 独立智能辅导终端 (v1.0)       {Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}===================================================={Colors.END}")
    
    key_info = load_active_key()
    if not key_info:
        print(f"{Colors.RED}未检测到可用的 API Key，请检查 keys_pool.json{Colors.END}")
        sys.exit(1)
        
    base_url = key_info.get('base_url', 'https://api.chatanywhere.tech/v1')
    api_key = key_info.get('api_key', '')
    site_name = key_info.get('name') or 'ChatAnywhere'
    model = 'gpt-4o-mini'
    
    print(f"{Colors.GREEN}✓ 节点状态: {site_name} (在线){Colors.END}")
    print(f"{Colors.GREEN}✓ 接入端点: {base_url}{Colors.END}")
    print(f"{Colors.GREEN}✓ 调度模型: {model} (高速流式响应){Colors.END}")
    print(f"{Colors.YELLOW}✓ 计费隔离: 完全独立，不消耗主会话额度{Colors.END}")
    print(f"{Colors.CYAN}✓ 知识库挂载: {VAULT_DIR}{Colors.END}")
    print(f"\n常用指令:")
    print(f"  {Colors.BOLD}/vault{Colors.END}   查看本地 408 笔记列表")
    print(f"  {Colors.BOLD}/view n{Colors.END}  快速预览第 n 篇笔记")
    print(f"  {Colors.BOLD}/clear{Colors.END}   清空当前对话上下文记忆")
    print(f"  {Colors.BOLD}/exit{Colors.END}    退出终端")
    print(f"{Colors.CYAN}----------------------------------------------------{Colors.END}\n")
    
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    while True:
        try:
            user_input = input(f"{Colors.BOLD}{Colors.BLUE}你 > {Colors.END}").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n再见，祝考研一战成硕！")
            break
            
        if not user_input:
            continue
            
        if user_input in ('/exit', 'exit', 'quit', ':q'):
            print("再见，祝考研一战成硕！")
            break
        elif user_input == '/clear':
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            print(f"{Colors.YELLOW}对话记忆已清空。{Colors.END}\n")
            continue
        elif user_input == '/vault':
            list_vault()
            continue
        elif user_input.startswith('/view'):
            parts = user_input.split()
            if len(parts) > 1:
                view_note(parts[1])
            else:
                list_vault()
            continue
        elif user_input == '/help':
            print("输入问题直接向 Hermes 提问；输入 /vault 浏览考研笔记库；输入 /clear 重置上下文。")
            continue
            
        messages.append({"role": "user", "content": user_input})
        
        print(f"\n{Colors.GREEN}{Colors.BOLD}Hermes 导师 > {Colors.END}", end='', flush=True)
        try:
            reply = stream_chat(base_url, api_key, model, messages)
            messages.append({"role": "assistant", "content": reply})
            print()
        except Exception as e:
            print(f"\n{Colors.RED}[请求出错]: {e}{Colors.END}\n")
            # 出错时剔除最后一个问题，允许重试
            messages.pop()

if __name__ == '__main__':
    main()
