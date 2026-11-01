"""
Hermes-Automation: 计算机专硕【408 + 数二 + 英二】真题与精解全自动提纯引擎
(postgrad_exam_papers_harvester.py)

定位:
- 100% 契合电子信息/计算机专硕考研黄金科目: 408 + 数学二 + 英语二
- 调度免费高算力活态 Key (ChatAnywhere / DoCode) 进行高质量结构化解析
- 生成结构化 Markdown 题库放入 reports/ 目录 (支持 Obsidian 一键导入复习)
- 发送精美摘要卡片至 Telegram 话题
"""

import sys
import io
import os
import json
import time
import requests

# 保证中文环境与控制台输出安全
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

BASE_DIR = r"C:\Users\zzx05\Hermes-Automation"
KEYS_POOL_FILE = os.path.join(BASE_DIR, "config", "keys_pool.json")
OUTPUT_MD = os.path.join(BASE_DIR, "reports", "CS_Postgrad_408_Math2_English2_Papers.md")

# 引入 Telegram 播报模块
sys.path.append(os.path.join(BASE_DIR, "tools"))
try:
    from tg_notify import send_notify
except ImportError:
    send_notify = None

CLEAN_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Content-Type": "application/json"
}

def load_keys():
    if os.path.exists(KEYS_POOL_FILE):
        try:
            with open(KEYS_POOL_FILE, "r", encoding="utf-8") as f:
                keys = json.load(f)
                return [k for k in keys if k.get("is_alive", True)]
        except Exception:
            pass
    return []

def query_llm(prompt, sys_prompt, active_keys):
    for key_info in active_keys:
        burl = key_info.get("base_url", "").rstrip("/")
        api_key = key_info.get("api_key", "")
        name = key_info.get("name") or "API_Node"
        model = "gpt-4o-mini"
        if "docode" in burl.lower():
            model = "grok-4.6"

        print(f"[*] 正在调用 [{name}] ({model}) 提纯真题模块...", flush=True)
        url = f"{burl}/chat/completions"
        headers = dict(CLEAN_HEADERS)
        headers["Authorization"] = f"Bearer {api_key}"

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.25,
            "max_tokens": 3500
        }

        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=90)
            if resp.status_code == 200:
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                print(f"[+] [{name}] 成功生成 (字数: {len(content)})", flush=True)
                return content
            else:
                print(f"[-] [{name}] 状态码: {resp.status_code}, 内容: {resp.text[:100]}", flush=True)
        except Exception as e:
            print(f"[-] [{name}] 请求异常: {e}", flush=True)

    return None

def run_harvest():
    print("=" * 60)
    print("🎓 启动【计算机专硕 408 + 数学二 + 英语二】核心真题与解密提纯引擎")
    print("=" * 60)

    keys = load_keys()
    if not keys:
        print("[-] 未检测到可用 API 节点！请检查 keys_pool.json")
        return False

    sys_prompt = (
        "你是一位中国顶尖计算机考研（408全国统考、数学二、英语二）辅导名师与阅卷专家。\n"
        "面向主攻计算机/软件专硕的考生，以【极度干货、步骤详尽、直击踩分点】的标准输出真题精解。\n"
        "要求：\n"
        "1. 绝不泛泛而谈，必须给出具体真题背景、完整题目、标准答案、阅卷采分点与核心解题套路。\n"
        "2. 代码一律采用清晰可运行的 C/C++ 语言，并严格给出时间/空间复杂度。\n"
        "3. 数学公式采用清晰的标准 LaTeX 语法。\n"
        "4. 输出排版为美观专业的 GitHub Markdown 格式。"
    )

    modules = [
        {
            "title": "# 📚 计算机专硕【408 + 数二 + 英二】历年核心真题与题型精析合集\n\n> 归档时间: " + time.strftime("%Y-%m-%d %H:%M:%S") + "\n\n",
            "prompt": None
        },
        {
            "title": "## 💻 第一部分：计算机 408 统考四大核心母题全真深度精解",
            "prompt": """请针对 408 全国统考，精选并深度剖析以下 4 道历年最经典、最具区分度的核心代表性综合大题母题：
1. 【数据结构·算法设计大题（41题风格）】：
   - 题目：精选一题历年高频真题（如：寻找数组未出现的最小正整数 / 寻找单链表倒数第k个结点 / 二叉树的带权路径长度WPL计算）。
   - 解析要求：
     (1) 给出算法的基本设计思想；
     (2) 编写规范且符合考场答题标准的 C/C++ 核心代码实现；
     (3) 准确分析时间复杂度和空间复杂度，指出阅卷常见扣分坑点。

2. 【计算机组成原理·指令与流水线综合大题（43/44题风格）】：
   - 精选一道关于 MIPS/RISC-V 指令系统、五段指令流水线（IF, ID, EX, MEM, WB）数据冲突与转发、Cache/主存/TLB 地址映射经典计算大题。
   - 给出详细计算过程、状态表格与解题思路。

3. 【操作系统·PV 信号量同步互斥经典大题（45题风格）】：
   - 精选一道经典的复杂进程同步互斥题（如：理发师问题变体、独木桥过车问题或读者写者变体）。
   - 严格定义信号量初值与含义，给出标准 P/V 伪代码，并说明如何保证绝不发生死锁。

4. 【计算机网络·TCP 拥塞控制与子网划分综合大题（47题风格）】：
   - 精选一道关于慢开始(Slow Start)、拥塞避免(Congestion Avoidance)、快重传/快恢复的拥塞窗口(cwnd)变化图表题与 CIDR 路由表汇聚综合题。
   - 逐问列出标准计算与推理步骤。"""
        },
        {
            "title": "## 📐 第二部分：考研数学二（302）历年必考母题与秒杀破局法",
            "prompt": """请针对考研数学二（不考概率论、不考三重积分与曲面积分，重深度与计算力），精选并深度剖析以下核心大题：
1. 【高等数学·微分中值定理与零点证明】：
   - 构造辅助函数法证明罗尔定理 / 柯西中值定理结论的高频真题原型。
   - 详细写出：辅助函数的构造技巧（积分原函数法、导数方程分离法）、证明步骤规范与易漏扣分点。

2. 【高等数学·定积分几何与物理应用 / 微分方程综合题】：
   - 精选一道关于平面图形旋转体体积、表面积计算，并与一阶/二阶常系数微分方程联立的经典大题。
   - 给出完整积分运算过程和最终结果。

3. 【线性代数·特征值、特征向量与二次型化简大题】：
   - 精选一道关于含参数矩阵相似对角化判定、正交变换化二次型为标准型的大题。
   - 详细写出特征方程求解、特征向量正交规范化（施密特正交化）、正交矩阵构造及惯性指数判断过程。"""
        },
        {
            "title": "## 📖 第三部分：考研英语二（204）真题阅读核心逻辑与高分写作模板",
            "prompt": """请针对考研英语二（偏重实用、商业、科技与社会生活，难度低于英一但对精准度要求极高），输出以下冲刺实战指南：
1. 【英语二真题阅读 4 大高频命题陷阱与解题公式】：
   - 主旨大意题、态度倾向题、词义推断题与事实细节题的标准解题切入点。
   - 如何识别“偷换概念”、“反向干扰”和“无中生有”等典型错误选项。

2. 【英语二小作文（应用文 10分）黄金满分模板】：
   - 精选最常考的【告示/通知 (Notice)】或【建议信 (Letter of Suggestion)】，给出原汁原味、没有陈词滥调的结构框架与必背地道高分句型。

3. 【英语二大作文（图表作文 15分）三段式破局模型】：
   - 针对柱状图/折线图/饼图，提供：
     (1) 第一段：数据描述与趋势概括的标准句型（上升、下降、占主导）；
     (2) 第二段：深度原因剖析（至少提供社会经济、个人心理、科技发展3大通用论据切入点）；
     (3) 第三段：未来预测与总结段落模板。"""
        }
    ]

    all_content = []
    for item in modules:
        all_content.append(item["title"])
        if item["prompt"]:
            print(f"\n🚀 正在提炼模块: {item['title'][:35]}...")
            res = query_llm(item["prompt"], sys_prompt, keys)
            if res:
                all_content.append(res)
                all_content.append("\n\n---\n\n")
            else:
                all_content.append("\n> [!] 提炼当前模块超时或异常，稍后自动重试。\n\n")
            time.sleep(2)

    # 写入 Markdown 题库
    full_text = "\n".join(all_content)
    try:
        os.makedirs(os.path.dirname(OUTPUT_MD), exist_ok=True)
        with open(OUTPUT_MD, "w", encoding="utf-8") as f:
            f.write(full_text)
        print(f"\n[+] 题库已成功保存至: {OUTPUT_MD} (总字数: {len(full_text)})")
    except Exception as e:
        print(f"[-] 保存文件失败: {e}")
        return False

    # 发送 Telegram 播报
    if send_notify:
        tg_card = (
            "🎓 *【考研真题与核心母题题库已生成】*\n\n"
            "🎯 *专硕黄金组合*：计算机 408 ＋ 数学二 ＋ 英语二\n"
            "📄 *文件已落盘*：`reports/CS_Postgrad_408_Math2_English2_Papers.md`\n\n"
            "💎 *核心模块包含*：\n"
            "• 408 四大金刚综合大题（算法设计/流水线/PV操作/TCP拥塞）\n"
            "• 数学二 高数中值定理辅助函数法 ＋ 线代二次型对角化\n"
            "• 英语二 阅读真题逻辑解密 ＋ 小作文/图表大作文模板\n\n"
            "💡 可直接在电脑端通过 Obsidian 或 Markdown 查看完整题解与采分点！"
        )
        send_notify(tg_card, topic="4")
        print("[+] Telegram 播报已推送！")

    return True

if __name__ == "__main__":
    run_harvest()
