"""
Hermes-Automation: 计算机考研408深度备考资料全自动脱敏采编与归纳引擎 (cs_postgrad_intel_gatherer.py)
特性:
1. 100% 严格信息脱敏: 不携带任何本地路径、机器名、IP、用户身份或私人信息，纯学术与考试考纲交互
2. 调度免费高算力中转站 Key (DoCode grok-4.6 / gpt-6-sol + ChatAnywhere 备用)
3. 结构化构建 408 四大金刚核心考点图谱、高频大题算法模板、全年备战时间线与开源资料导航
4. 生成独立 Markdown 知识库归档并同步推送到 Telegram
"""

import sys, io, time, os, json, requests
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.append(r'C:\Users\zzx05\Hermes-Automation\services')

from wool_radar import send_telegram_text, TOPIC_WOOL_ID

BASE_DIR = r"C:\Users\zzx05\Hermes-Automation"
KEYS_POOL_FILE = os.path.join(BASE_DIR, "config", "keys_pool.json")
REPORT_FILE = os.path.join(BASE_DIR, "reports", "CS_Postgraduate_Exam_Guide.md")

# 纯净请求头，无任何敏感信息或环境指纹
SANITIZED_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Content-Type": "application/json"
}

def load_active_keys():
    """获取可用的中转站 Key"""
    if os.path.exists(KEYS_POOL_FILE):
        try:
            with open(KEYS_POOL_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return [k for k in data if k.get("is_alive", True)]
        except Exception:
            pass
    return []

def query_desensitized_ai(prompt, active_keys, max_tokens=2200):
    """
    纯脱敏请求调度:
    使用纯净 Prompt，轮询可用的中转站节点，绝不暴露客户端私人身份
    """
    for node in active_keys:
        burl = node.get("base_url")
        key = node.get("api_key")
        site_name = node.get("name", "Unknown")
        
        # 优选模型
        model = "gpt-4o-mini"
        if "docode" in burl.lower():
            model = "grok-4.6"
            
        print(f"[*] 正在调用 [{site_name}] ({model}) 处理模块任务...")
        endpoint = f"{burl.rstrip('/')}/chat/completions"
        headers = dict(SANITIZED_HEADERS)
        headers["Authorization"] = f"Bearer {key}"
        
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "你是一位计算机专业考研（408全国统考与自命题）资深辅导名师与高分上岸学长。请提供严谨、系统、干货极高且符合中国研招最新命题规律的专业资料与备考建议，使用结构清晰的 GitHub Markdown 格式回答。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": max_tokens,
            "temperature": 0.4
        }
        
        try:
            # 设置适度超时，防止单节点卡死
            resp = requests.post(endpoint, headers=headers, json=payload, timeout=35)
            if resp.status_code == 200:
                content = resp.json()["choices"][0]["message"]["content"]
                print(f"[+] [{site_name}] 生成成功 (字数: {len(content)})")
                return content
            else:
                print(f"[-] [{site_name}] 请求失败: {resp.status_code} - {resp.text[:80]}")
        except Exception as e:
            print(f"[-] [{site_name}] 异常: {e}")
            
    return None

def build_cs_postgrad_guide():
    print("=" * 60)
    print("🎓 启动计算机考研408深度备考资料脱敏采集流水线")
    print("=" * 60)
    
    active_keys = load_active_keys()
    if not active_keys:
        print("[-] 未检测到可用 API 节点！")
        return
        
    modules = [
        {
            "title": "一、408 统考四大专业课核心考点全景图谱与高频考题透视",
            "prompt": """
请详细梳理中国计算机考研【408 计算机学科专业基础】四大科目（数据结构 45分、计算机组成原理 45分、操作系统 35分、计算机网络 25分）的核心知识框架与近几年命题重点：
1. 数据结构：线性表/栈队列、树与二叉树（遍历/线索/AVL/哈夫曼）、图（拓扑排序/关键路径/Dijkstra/Prim）、排序与查找的核心算法与考查形式。
2. 计算机组成原理：浮点数IEEE 754表示与运算、存储层次Cache映射与主存虚存设计、指令系统寻址方式、CPU数据通路与五段流水线（冒险处理）、总线与I/O中断与DMA。
3. 操作系统：进程线程模型、经典同步互斥信号量PV操作、死锁检测与避免、内存分页分段与虚拟内存置换算法、文件系统FCB/索引节点与磁盘调度。
4. 计算机网络：OSI与TCP/IP体系、子网划分CIDR与路由汇聚、TCP三次握手四次挥手/滑动窗口/拥塞控制阶段算法、DNS与HTTP协议工作流。
重点标出考生最容易失分的综合大题题型。
"""
        },
        {
            "title": "二、计算机考研全年科学备战复习规划与时间线安排",
            "prompt": """
请为计算机考研考生制定一份科学的【全年复习时间线与备战节奏方案】（涵盖 408 专业课 + 数学一/二 + 英语 + 政治）：
1. 基础轮（3月 - 6月）：各科复习优先级、第一轮教材/视频学习深度、避免盲目做题的建议。
2. 强化轮（7月 - 9月/暑假黄金期）：大题专项攻坚、错题集提炼、真题前的知识闭环。
3. 真题冲刺轮（10月 - 11月）：2009-最新年408真题套卷计时模考使用方法、如何复盘与考点溯源。
4. 押题模考与背诵轮（12月）：防丢分策略、专业课手写代码防失误要点、考场应试时间分配（单选 vs 综合大题）。
同时说明跨考同学与科班同学在时间分配上的差异化应对策略。
"""
        },
        {
            "title": "三、经典权威参考教材、优质开源项目与备考资源导航",
            "prompt": """
请汇总计算机考研备战中最受公认的【权威参考教材、开源备考资料与网课刷题资源】：
1. 核心教材与教辅推荐：
   - 王道考研系列 408 单科书与真题全解特点。
   - 经典大学本科教材参考书目（严蔚敏《数据结构》、唐朔飞/袁春风《计组》、汤小丹《操作系统》、谢希仁《计算机网络》、黑书《深入理解计算机系统 CSAPP》的阅读取舍）。
2. GitHub 上高赞计算机考研开源项目推荐与检索关键词（例如历年真题汇总、笔记脑图、手写算法代码库、择校经验贴汇总）。
3. 官方权威渠道：研招网、中国计算机学会(CCF)竞赛与考研关联性。
"""
        },
        {
            "title": "四、408 核心大题解题套路与高频手撕算法必背模板",
            "prompt": """
请整理 408 综合应用题（尤其是算法题与系统设计题）的【高频解题模板与答题规范】：
1. 数据结构算法设计大题（41题）标准答题四步法（算法基本思想、C/C++代码实现、时间复杂度分析、空间复杂度分析），并给出一个最经典的快慢指针或二叉树算法代码标准模板。
2. 操作系统 PV 信号量操作大题的规范书写范式（信号量定义、初值含义、互斥与同步锁放置规则）。
3. 计组与计网综合计算题得分关键：写出计算步骤公式、单位转换（B vs b、1024 vs 1000）、绘图规范。
"""
        },
        {
            "title": "五、择校选型决策与学硕(0812) vs 专硕(0854)解析",
            "prompt": """
请为计算机考研学子提供【科学择校选型与考研政策深度解析】：
1. 408 统考大趋势：为什么越来越多高校将专业课统考改为 408？考 408 与自命题高校相比有何优劣势？
2. 学硕（0812 计算机科学与技术） vs 专硕（0854 电子信息/软件工程）：
   - 考试科目差异（数学一+英语一 vs 数学二+英语二 或 数一英一）。
   - 学制、学费、读博导向与找工作就业认受度差异。
3. 985/211/双非典型梯队初试复试线评估方法、如何查阅高校历年录取名单、报录比与调剂信息，防止踩坑。
"""
        }
    ]
    
    collected_sections = []
    
    for i, mod in enumerate(modules, 1):
        print(f"\n--- [{i}/{len(modules)}] 正在采集: {mod['title']} ---")
        content = query_desensitized_ai(mod["prompt"], active_keys)
        if content:
            collected_sections.append(f"## {mod['title']}\n\n{content}\n")
        else:
            collected_sections.append(f"## {mod['title']}\n\n*该模块获取超时，可在下一次自动轮询中补全。*\n")
        time.sleep(2)
        
    # 组装完整知识库 Markdown
    now_str = time.strftime("%Y-%m-%d %H:%M:%S")
    header = f"""# 📚 计算机专业考研（408统考与自命题）全景备战与核心资料宝典

> **生成说明**：本资料库由 Hermes-Automation 自动调度公网 AI 算力集群进行**全隐私脱敏采编整理**。
> **编制时间**：{now_str}
> **内容定位**：涵盖 408 核心知识图谱、全年时间线规划、权威教材与开源项目推荐、大题手撕模板与择校分析。

---

"""
    full_document = header + "\n\n---\n\n".join(collected_sections)
    
    # 写入报告文件
    os.makedirs(os.path.dirname(REPORT_FILE), exist_ok=True)
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(full_document)
        
    print(f"\n🎉 计算机考研资料库整理完毕！已保存至本地: {REPORT_FILE}")
    print(f"📊 总字数: {len(full_document)} 字符")
    
    # 向 Telegram 话题 3 推送简报通知
    tg_msg = (
        f"📖 *【计算机考研 408 核心备考资料库编制完成】*\n\n"
        f"🛡 *隐私状态*: 100% 匿名脱敏 (零个人/环境信息外泄)\n"
        f"🤖 *算力来源*: 自动化中转站 Key 集群 (DoCode Grok-4.6 / GPT-6)\n"
        f"📝 *资料模块*: 5 大核心考点与规划专题\n"
        f"📁 *本地归档*: `reports/CS_Postgraduate_Exam_Guide.md`\n"
        f"⏱ *生成时间*: `{now_str}`\n\n"
        f"包含 408 四门科目重点、高频大题算法模板、权威书单与全年时间线，已就绪供查阅！"
    )
    send_telegram_text(TOPIC_WOOL_ID, tg_msg)

if __name__ == "__main__":
    build_cs_postgrad_guide()
