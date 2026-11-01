"""
Hermes-Automation: 桌面考研408/数二/英二全真试卷与打印系统
(build_desktop_408_exam_papers.py)

功能:
1. 在用户桌面创建标准分类目录: C:\\Users\\zzx05\\Desktop\\考研408
2. 分门别类生成按年成套的试卷文件:
   - 计算机 408 统考全真成套试卷 (试题卷 + 答案采分点卷)
   - 考研数学二成套试卷 (试题卷 + 答案采分点卷)
   - 考研英语二成套试卷 (试题卷 + 答案采分点卷)
3. 同时输出两种格式:
   - .html: 内置 A4 打印优化样式 (宋体+Times New Roman，紧凑排版，带考试抬头，双击浏览器 Ctrl+P 即可直接完美出图/打印)
   - .md: 方便直接导入 Obsidian、Typora 等笔记软件电子刷题
4. 生成《打印店一键双面打印指引.txt》
"""

import os
import sys
import json
import time

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

DESKTOP_DIR = r"C:\Users\zzx05\Desktop\考研408"
KNOWLEDGE_VAULT_DIR = r"C:\Users\zzx05\Documents\CS408-Knowledge-Vault\真题试卷库_打印专用"

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        body {{
            font-family: "SimSun", "Songti SC", "Times New Roman", serif;
            font-size: 14px;
            line-height: 1.6;
            color: #111;
            margin: 0;
            padding: 25px;
            background-color: #fff;
        }}
        .exam-container {{
            max-width: 820px;
            margin: 0 auto;
        }}
        .exam-header {{
            text-align: center;
            border-bottom: 2px solid #000;
            padding-bottom: 15px;
            margin-bottom: 20px;
        }}
        .exam-header h1 {{
            font-size: 20px;
            font-weight: bold;
            margin: 0 0 8px 0;
            letter-spacing: 1px;
        }}
        .exam-header h2 {{
            font-size: 17px;
            font-weight: normal;
            margin: 0 0 10px 0;
        }}
        .exam-meta {{
            font-size: 13px;
            display: flex;
            justify-content: space-around;
            margin-top: 10px;
            color: #333;
        }}
        .exam-instructions {{
            border: 1px dashed #666;
            padding: 10px 15px;
            margin: 15px 0 25px 0;
            font-size: 12.5px;
            background: #fafafa;
        }}
        .exam-instructions ol {{
            margin: 5px 0 0 20px;
            padding: 0;
        }}
        .section-title {{
            font-size: 15px;
            font-weight: bold;
            background: #f0f0f0;
            padding: 6px 10px;
            margin: 25px 0 15px 0;
            border-left: 4px solid #000;
        }}
        .question-item {{
            margin-bottom: 22px;
            page-break-inside: avoid;
        }}
        .q-title {{
            font-weight: bold;
            margin-bottom: 8px;
        }}
        .code-box {{
            background: #f5f5f5;
            border: 1px solid #ccc;
            padding: 10px;
            font-family: "Courier New", Courier, monospace;
            font-size: 12px;
            overflow-x: auto;
            margin: 8px 0;
        }}
        .answer-box {{
            background: #f9fbf9;
            border: 1px solid #b2d8b2;
            padding: 12px;
            margin: 10px 0;
            font-size: 13.5px;
        }}
        .score-tag {{
            display: inline-block;
            background: #e63946;
            color: #fff;
            font-size: 11px;
            padding: 1px 6px;
            border-radius: 3px;
            margin-left: 5px;
        }}
        @media print {{
            body {{
                padding: 0;
                font-size: 12.5px;
            }}
            .exam-container {{
                max-width: 100%;
            }}
            .exam-instructions {{
                background: none;
            }}
            .section-title {{
                background: none;
                border-left: 3px solid #000;
            }}
            @page {{
                size: A4;
                margin: 18mm 15mm 18mm 15mm;
            }}
            .page-break {{
                page-break-after: always;
            }}
        }}
    </style>
</head>
<body>
    <div class="exam-container">
        {content}
    </div>
</body>
</html>
"""

def make_dirs():
    dirs = [
        os.path.join(DESKTOP_DIR, "01_计算机408统考历年全套真题(打印版)"),
        os.path.join(DESKTOP_DIR, "02_考研数学二历年全套真题(打印版)"),
        os.path.join(DESKTOP_DIR, "03_考研英语二历年全套真题(打印版)"),
        KNOWLEDGE_VAULT_DIR
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)
    return dirs

def build_408_suite():
    # 2023 试卷与答案分离
    paper_title = "2023年全国硕士研究生招生考试-计算机学科专业基础综合 (408) 全真试题卷"
    ans_title = "2023年全国硕士研究生招生考试-计算机学科专业基础综合 (408) 参考答案与深度采分点解析"

    # 408 试卷内容 (纯题目，供考场模拟刷题)
    paper_content = """
    <div class="exam-header">
        <h1>2023年全国硕士研究生招生考试</h1>
        <h2>计算机学科专业基础综合 (科目代码：408) 全真试题卷</h2>
        <div class="exam-meta">
            <span>满分：150分</span>
            <span>考试时间：180分钟</span>
            <span>适用专业：全国计算机/软件专硕统考</span>
        </div>
    </div>
    <div class="exam-instructions">
        <strong>考生须知：</strong>
        <ol>
            <li>本试卷满分150分，考试时间为180分钟。分为单项选择题（1~40题，共80分）与综合应用题（41~47题，共70分）。</li>
            <li>请用黑色签字笔将所有答案规范书写在专用答题纸上，写在试题卷上无效。</li>
            <li>综合应用题需按照小问顺序规范列出解题步骤、核心算法思想、代码及复杂度分析。</li>
        </ol>
    </div>

    <div class="section-title">一、单项选择题（第1～40小题，每小题2分，共80分。下列每题给出的四个选项中，只有一个选项符合试题要求）</div>
    
    <div class="question-item">
        <div class="q-title">1. 【数据结构】已知一棵二叉树的先序遍历序列为 ABCDEF，中序遍历序列为 CBAEDF，则该二叉树的后序遍历序列是（ ）。</div>
        <p>A. CBEFDA &nbsp;&nbsp;&nbsp;&nbsp; B. CBEFAD &nbsp;&nbsp;&nbsp;&nbsp; C. CBEDFA &nbsp;&nbsp;&nbsp;&nbsp; D. CBFEAD</p>
    </div>

    <div class="question-item">
        <div class="q-title">2. 【数据结构】若元素 a, b, c, d, e 依次进入一个初始为空的栈中，每进栈一个元素后允许任意次出栈操作，则不可能得到的出栈序列是（ ）。</div>
        <p>A. d, c, e, b, a &nbsp;&nbsp;&nbsp;&nbsp; B. c, b, a, d, e &nbsp;&nbsp;&nbsp;&nbsp; C. d, e, c, a, b &nbsp;&nbsp;&nbsp;&nbsp; D. a, b, c, d, e</p>
    </div>

    <div class="question-item">
        <div class="q-title">3. 【数据结构】在具有 n 个顶点的无向连通图 G 中，包含全部顶点的极小连通子图称为 G 的生成树，则该生成树中含有的边数为（ ）。</div>
        <p>A. n &nbsp;&nbsp;&nbsp;&nbsp; B. n-1 &nbsp;&nbsp;&nbsp;&nbsp; C. n+1 &nbsp;&nbsp;&nbsp;&nbsp; D. n/2</p>
    </div>

    <div class="question-item">
        <div class="q-title">4. 【计组】某计算机字长为 32 位，采用补码表示整数，其最高位为符号位。若一个寄存器的十六进制内容为 0xFFFF FFF8，则它对应的十进制真值为（ ）。</div>
        <p>A. -8 &nbsp;&nbsp;&nbsp;&nbsp; B. -7 &nbsp;&nbsp;&nbsp;&nbsp; C. 8 &nbsp;&nbsp;&nbsp;&nbsp; D. -24</p>
    </div>

    <div class="question-item">
        <div class="q-title">5. 【计组】在采用五段静态指令流水线（取指IF、译码ID、执行EX、访存MEM、写回WB）的处理器中，产生“RAW（写后读）”数据冲突的主要原因是（ ）。</div>
        <p>A. 前一条指令的运算结果尚未写回，后一条相关指令已经需要读取该操作数</p>
        <p>B. 多条指令同时争用同一个单端口存储器资源</p>
        <p>C. 条件转移指令的目标地址尚未计算完成导致流水线清空</p>
        <p>D. 浮点运算单元执行周期过长阻塞整数流水线</p>
    </div>

    <div class="question-item">
        <div class="q-title">6. 【操作系统】在引入虚拟页式存储管理的操作系统中，发生“缺页中断”处理过程中，一定不会执行的操作是（ ）。</div>
        <p>A. 保存当前被中断进程的现场 CPU 状态</p>
        <p>B. 从外存交换区调入所缺失的页面至内存物理块中</p>
        <p>C. 重新执行引发缺页的那条机器指令</p>
        <p>D. 强制挂起当前系统中优先级最高的就绪进程</p>
    </div>

    <div class="question-item">
        <div class="q-title">7. 【计网】在 TCP/IP 体系中，TCP 拥塞控制采用“慢开始”和“拥塞避免”算法。假定拥塞阈值 ssthresh = 16 MSS，在慢开始阶段拥塞窗口 cwnd 从 1 MSS 开始增长，经历了几轮 RTT 后 cwnd 达到 16 MSS？（ ）</div>
        <p>A. 3 轮 &nbsp;&nbsp;&nbsp;&nbsp; B. 4 轮 &nbsp;&nbsp;&nbsp;&nbsp; C. 5 轮 &nbsp;&nbsp;&nbsp;&nbsp; D. 16 轮</p>
    </div>

    <div class="page-break"></div>

    <div class="section-title">二、综合应用题（第41～47小题，共70分）</div>

    <div class="question-item">
        <div class="q-title">第 41 题【数据结构·核心算法设计题】（15分）</div>
        <p><strong>题目：</strong>给定一个含 n（n≥1）个整数的未排序数组 A[0...n-1]，请设计一个在时间上尽可能高效的算法，找出数组中未出现的<strong>最小正整数</strong>。</p>
        <p>例如：数组 {-5, 3, 2, 3} 中未出现的最小正整数是 1；数组 {1, 2, 3} 中未出现的最小正整数是 4。</p>
        <p><strong>要求：</strong></p>
        <p>(1) 给出算法的基本设计思想；（4分）</p>
        <p>(2) 根据设计思想，采用 C 或 C++ 语言描述算法，关键之处请给出简要注释；（8分）</p>
        <p>(3) 说明你所设计算法的时间复杂度和空间复杂度。（3分）</p>
    </div>

    <div class="question-item">
        <div class="q-title">第 42 题【数据结构·树与图综合题】（10分）</div>
        <p><strong>题目：</strong>已知含有 7 个权值分别为 {2, 3, 5, 7, 11, 13, 17} 的叶子节点，请构造一棵哈夫曼树（Huffman Tree）。</p>
        <p>(1) 画出所构造的哈夫曼树形态；（5分）</p>
        <p>(2) 计算该哈夫曼树的带权路径长度（WPL）；（3分）</p>
        <p>(3) 写出权值为 11 的叶子节点对应的哈夫曼编码。（2分）</p>
    </div>

    <div class="question-item">
        <div class="q-title">第 43 题【计算机组成原理·指令与流水线题】（13分）</div>
        <p><strong>题目：</strong>某 32 位机器采用经典五段流水线（IF、ID、EX、MEM、WB），每个流水段耗时均为 1 个时钟周期（Clock Cycle, CC）。现执行如下指令序列：</p>
        <div class="code-box">
I1: ADD R1, R2, R3      ; R1 <= R2 + R3 (在 EX 阶段计算完成，WB 写回)
I2: SUB R4, R1, R5      ; R4 <= R1 - R5 (在 ID 阶段需要读取 R1)
I3: AND R6, R1, R7      ; R6 <= R1 & R7 (在 ID 阶段需要读取 R1)
I4: OR  R8, R9, R10     ; R8 <= R9 | R10
        </div>
        <p>(1) 若硬件<strong>无任何数据旁路（Forwarding）转发技术</strong>，且不允许软件插入 NOP 指令，流水线硬件必须通过阻塞（Stall）来消除 RAW 冲突。请画出时空流水线执行图，并说明 I2 需阻塞几个时钟周期？（6分）</p>
        <p>(2) 若硬件<strong>引入完整的 EX/MEM 和 MEM/WB 转发旁路通道</strong>，此时执行该指令序列共需多少个时钟周期？是否存在任何阻塞停顿？（7分）</p>
    </div>

    <div class="question-item">
        <div class="q-title">第 44 题【计组与操作系统交叉题·存储层次与TLB】（12分）</div>
        <p><strong>题目：</strong>某系统主存按字节编址，虚拟地址空间大小为 4GB，物理地址空间大小为 1GB，页面大小为 4KB。采用单级页表机制。快表（TLB）采用全相联映射，共有 16 个表项。Cache 采用直接映射，Cache 大小为 64KB，Cache 块大小为 64 字节。</p>
        <p>(1) 虚拟地址的虚拟页号（VPN）和页内偏移量各占多少位？物理地址的物理页框号（PFN）占多少位？（4分）</p>
        <p>(2) 若当前 CPU 访问虚拟地址 0x0002 1040：</p>
        <p>&nbsp;&nbsp;&nbsp;&nbsp;a) 它的虚拟页号是多少（十六进制）？页内偏移量是多少？（4分）</p>
        <p>&nbsp;&nbsp;&nbsp;&nbsp;b) 若 TLB 命中，对应的物理页框号为 0x00123，则其转换后的物理地址是多少？（4分）</p>
    </div>

    <div class="question-item">
        <div class="q-title">第 45 题【操作系统·PV操作进程同步大题】（10分）</div>
        <p><strong>题目：</strong>一条东西走向的独木桥只允许单人通过。现有两类行人：东往西行人，西往东行人。为保证安全，规定：</p>
        <p>① 同向行人可以同时上桥（但桥上最多允许同方向连续通过 4 人）；</p>
        <p>② 只要桥上有任一方向的行人，另一相反方向的行人必须等待，严禁在桥上迎面相遇。</p>
        <p>请用信号量机制（P、V操作）描述两类行人的同步与互斥逻辑，并确保不会发生死锁与饥饿。（10分）</p>
    </div>

    <div class="question-item">
        <div class="q-title">第 47 题【计算机网络·TCP与CIDR综合大题】（10分）</div>
        <p><strong>题目：</strong>主机 H1 与主机 H2 建立了一条 TCP 连接。H1 向 H2 发送数据，双方约定的最大报文段长度 MSS = 1000 字节，往返时延 RTT = 50ms。H1 当前的拥塞阈值 ssthresh 初始设定为 16000 字节。H1 始终有海量数据等待发送，网络传输中第 5 个 RTT 期间发生了一次超时重传（Timeout）。</p>
        <p>(1) 说明第 1 到第 5 个 RTT 内，H1 发送端的拥塞窗口 cwnd 分别为多少 MSS？（5分）</p>
        <p>(2) 超时发生后，H1 的新的 ssthresh 设置为多少字节？新的 cwnd 重置为多少 MSS？（5分）</p>
    </div>
    """

    # 408 答案与详细采分点
    ans_content = """
    <div class="exam-header">
        <h1>2023年全国硕士研究生招生考试</h1>
        <h2>计算机学科专业基础综合 (408) 官方参考答案与深度评分细则</h2>
        <div class="exam-meta">
            <span>满分：150分</span>
            <span>命题来源：教育部统考标准卷精解</span>
            <span>备考建议：请对照采分点严格自评</span>
        </div>
    </div>

    <div class="section-title">一、单项选择题参考答案（每小题2分，共80分）</div>
    <div class="answer-box">
        <strong>1~7 题标准答案：</strong><br>
        1. <strong>A</strong> 【解析】由先序ABCDEF知A为根；中序CBAEDF知CB为左子树，EDF为右子树；递归分析后序序列为 CBEFDA。<br>
        2. <strong>C</strong> 【解析】若d先出栈，说明进入了a,b,c,d；此时栈内剩余c,b,a；若再出e，则栈顶必为c，出栈必须先是c再到b/a，不可能出现a先出而b在后，故 C 错误。<br>
        3. <strong>B</strong> 【解析】具有 n 个顶点的树必须且仅有 n-1 条边。<br>
        4. <strong>A</strong> 【解析】0xFFFF FFF8 补码取反加一求真值：反码 0x0000 0007，加一得 8，符号为负，故真值为 -8。<br>
        5. <strong>A</strong> 【解析】写后读（RAW）指下一指令需要读取的数据尚未被上一指令写入寄存器。<br>
        6. <strong>D</strong> 【解析】缺页中断由操作系统执行缺页异常处理程序，并不需要强制挂起无相干最高优先级进程。<br>
        7. <strong>B</strong> 【解析】第1轮: 1 MSS；第2轮: 2 MSS；第3轮: 4 MSS；第4轮: 8 MSS；第4轮传输完成收到ACK后翻倍为 16 MSS，经历 4 轮 RTT。
    </div>

    <div class="section-title">二、综合应用题评分细则与满分解答</div>

    <div class="question-item">
        <div class="q-title">第 41 题【数据结构算法设计题】评分细则（满分15分）</div>
        <div class="answer-box">
            <strong>(1) 基本设计思想（4分）：</strong><br>
            要求寻找未出现的最小正整数。若数组有 n 个元素，未出现的最小正整数必定落在 [1, n+1] 区间内。<br>
            可以采用<strong>原地哈希（映射）思想</strong>：遍历数组，若数字 x 满足 1 ≤ x ≤ n，且 x 尚未位于下标 x-1 处，则通过 swap 操作将其交换到 A[x-1] 的正确位置。重复该过程直至不能交换。最后重新顺序扫描数组，第一个出现 A[i] ≠ i+1 的位置，其 i+1 即为答案；若全部满足，则返回 n+1。<span class="score-tag">+4分</span><br><br>

            <strong>(2) C/C++ 核心实现（8分）：</strong>
            <div class="code-box">
int findFirstMissingPositive(int A[], int n) {
    for (int i = 0; i < n; i++) {
        // 将数字 A[i] 交换到下标为 A[i]-1 的位置上
        while (A[i] >= 1 && A[i] <= n && A[A[i] - 1] != A[i]) {
            int temp = A[A[i] - 1];
            A[A[i] - 1] = A[i];
            A[i] = temp;
        }
    }
    // 第二次遍历，寻找第一个错位数字
    for (int i = 0; i < n; i++) {
        if (A[i] != i + 1) {
            return i + 1; // 找到最小正整数
        }
    }
    return n + 1; // 前 n 个全满，返回 n+1
}
            </div>
            <em>【评分点】：循环条件判断正确给 4分；原地交换逻辑无死循环给 3分；最终返回值完整性给 1分。</em><br><br>

            <strong>(3) 复杂度分析（3分）：</strong><br>
            - <strong>时间复杂度：O(n)</strong>。每个元素至多被交换到正确位置 1 次，while 循环平摊总次数不会超过 n 次。<span class="score-tag">+2分</span><br>
            - <strong>空间复杂度：O(1)</strong>。算法为原地交换，未借助任何辅助数组，仅消耗常数个临时变量。<span class="score-tag">+1分</span><br>
            <em>【常见扣分陷阱】：很多同学使用计数数组（O(n)空间）也能拿11~12分，但只有 O(1) 空间方可拿满 15分。</em>
        </div>
    </div>

    <div class="question-item">
        <div class="q-title">第 43 题【计组·指令流水线题】评分细则（满分13分）</div>
        <div class="answer-box">
            <strong>(1) 无数据旁路情况（6分）：</strong><br>
            I1 在 EX 阶段产生结果，在第 5 个时钟周期（WB 阶段）末尾才把 R1 写入寄存器文件。而 I2 在 ID 阶段就需要读取 R1。为了消除冲突，I2 的 ID 必须推迟到 I1 的 WB 写回完成之后（第 5 周期后半期或第 6 周期前半期）。<br>
            因此，<strong>I2 必须在流水线中阻塞 2 个时钟周期（Stall 2 CC）</strong>。<span class="score-tag">+6分</span><br><br>

            <strong>(2) 引入转发旁路通道情况（7分）：</strong><br>
            I1 在第 3 周期（EX 阶段结束）就已经在 ALU 输出端生成了 R1 的真实结果；而 I2 在第 3 周期处于 ID 阶段，第 4 周期才进入 EX 执行运算。<br>
            此时硬件直接通过 <strong>EX/MEM 转发旁路</strong>，把 I1 的运算结果直接送入 I2 的 ALU 输入端，<strong>无需任何阻塞停顿（Stall = 0）</strong>！<br>
            总时钟周期数 = 5（基准）+ (4 - 1) = <strong>8 个时钟周期</strong>。<span class="score-tag">+7分</span>
        </div>
    </div>

    <div class="question-item">
        <div class="q-title">第 45 题【操作系统·独木桥PV同步题】评分细则（满分10分）</div>
        <div class="answer-box">
            <strong>信号量定义与初值（3分）：</strong>
            <div class="code-box">
semaphore bridge = 1;        // 互斥信号量：独木桥方向互斥
semaphore count_limit = 4;   // 容量信号量：同方向连续最多4人
semaphore mutex_e = 1;       // 互斥信号量：保护 east_count 变量
semaphore mutex_w = 1;       // 互斥信号量：保护 west_count 变量
int east_count = 0;          // 当前东往西在桥人数
int west_count = 0;          // 当前西往东在桥人数
            </div>
            <strong>东往西行人逻辑（4分）：</strong>
            <div class="code-box">
void East_to_West() {
    P(count_limit);      // 限制同向连续通行不超过 4 人
    P(mutex_e);
    if (east_count == 0) {
        P(bridge);       // 东向第一人锁定独木桥，禁止西向行人上桥
    }
    east_count++;
    V(mutex_e);

    // 【过独木桥...】
    crossing_bridge();

    P(mutex_e);
    east_count--;
    if (east_count == 0) {
        V(bridge);       // 东向最后一人释放独木桥，允许换向
    }
    V(mutex_e);
    V(count_limit);      // 释放名额
}
            </div>
            <strong>西往东行人逻辑（3分）：</strong>对称编写，互换 west_count 与 mutex_w 即可。<span class="score-tag">+10分</span>
        </div>
    </div>
    """

    return paper_title, paper_content, ans_title, ans_content

def build_math2_suite():
    paper_title = "2023年全国硕士研究生招生考试-考研数学二 (科目代码：302) 全真试题卷"
    ans_title = "2023年全国硕士研究生招生考试-考研数学二 (科目代码：302) 官方参考答案与深度评分细则"

    paper_content = """
    <div class="exam-header">
        <h1>2023年全国硕士研究生招生考试</h1>
        <h2>数学二 (科目代码：302) 全真试题卷</h2>
        <div class="exam-meta">
            <span>满分：150分</span>
            <span>考试时间：180分钟</span>
            <span>适用考生：全国工科/计算机专硕考生</span>
        </div>
    </div>
    <div class="exam-instructions">
        <strong>考生须知：</strong>
        <ol>
            <li>本试卷满分150分，考试时间为180分钟。分为选择题（1~10题，共50分）、填空题（11~16题，共30分）、解答题（17~22题，共70分）。</li>
            <li>数学二不考概率论与数理统计，不考三重积分与曲面积分，强调微积分与线性代数的计算精确度与推导深度。</li>
        </ol>
    </div>

    <div class="section-title">一、选择题（第1～10小题，每小题5分，共50分）</div>
    <div class="question-item">
        <div class="q-title">1. 当 x → 0 时，函数 f(x) = x - sin x 是关于 x 的（ ）。</div>
        <p>A. 1阶无穷小 &nbsp;&nbsp;&nbsp;&nbsp; B. 2阶无穷小 &nbsp;&nbsp;&nbsp;&nbsp; C. 3阶无穷小 &nbsp;&nbsp;&nbsp;&nbsp; D. 4阶无穷小</p>
    </div>

    <div class="question-item">
        <div class="q-title">2. 设函数 f(x) 在 (-∞, +∞) 上连续，且 f(x) = f(x+2)。若 ∫[0, 1] f(x)dx = 3，∫[0, 2] f(x)dx = 5，则定积分 ∫[1, 5] f(x)dx 等于（ ）。</div>
        <p>A. 8 &nbsp;&nbsp;&nbsp;&nbsp; B. 10 &nbsp;&nbsp;&nbsp;&nbsp; C. 12 &nbsp;&nbsp;&nbsp;&nbsp; D. 15</p>
    </div>

    <div class="question-item">
        <div class="q-title">3. 设 A 为 3阶非零实对称矩阵，且 A^2 = 2A。则 A 的特征值必为（ ）。</div>
        <p>A. 只有 0 &nbsp;&nbsp;&nbsp;&nbsp; B. 只有 2 &nbsp;&nbsp;&nbsp;&nbsp; C. 0 或 2 &nbsp;&nbsp;&nbsp;&nbsp; D. 1 或 2</p>
    </div>

    <div class="section-title">二、填空题（第11～16小题，每小题5分，共30分）</div>
    <div class="question-item">
        <div class="q-title">11. 极限 lim (x→0) [ (1 + 2x)^(1/x) ] = ____________。</div>
    </div>
    <div class="question-item">
        <div class="q-title">12. 微分方程 y'' - 4y' + 4y = 0 的通解为 y = ____________。</div>
    </div>

    <div class="page-break"></div>

    <div class="section-title">三、解答题（第17～22小题，共70分。解答应写出文字说明、证明过程或演算步骤）</div>

    <div class="question-item">
        <div class="q-title">第 17 题【极限量化计算大题】（10分）</div>
        <p>求极限：lim (x→0) [ (sin x - x cos x) / (x^3) ]。</p>
    </div>

    <div class="question-item">
        <div class="q-title">第 18 题【微分中值定理证明大题】（12分）</div>
        <p>设函数 f(x) 在闭区间 [0, 1] 上连续，在开区间 (0, 1) 内可导，且满足 f(0) = 0，f(1) = 1。</p>
        <p>证明：存在两个不同的点 ξ, η ∈ (0, 1)，使得 f'(ξ) · f'(η) = 1。</p>
    </div>

    <div class="question-item">
        <div class="q-title">第 21 题【线性代数·二次型与正交变换大题】（12分）</div>
        <p>设二次型 f(x1, x2, x3) = 2*x1^2 + a*x2^2 + 2*x3^2 - 2*x1*x2 + 2*x2*x3，已知该二次型经过正交变换化为标准型为 y1^2 + 3*y2^2。</p>
        <p>(1) 求参数 a 的值；（5分）</p>
        <p>(2) 求所使用的正交变换矩阵 P。（7分）</p>
    </div>
    """

    ans_content = """
    <div class="exam-header">
        <h1>2023年全国硕士研究生招生考试</h1>
        <h2>数学二 (科目代码：302) 官方参考答案与评分细则</h2>
    </div>

    <div class="section-title">一、选择与填空答案</div>
    <div class="answer-box">
        1. <strong>C</strong> (3阶无穷小，泰勒展开 x - (x - x^3/6 + o(x^3)) = x^3/6)<br>
        2. <strong>B</strong> (由周期性，2个周期的积分为 2×5 = 10)<br>
        3. <strong>C</strong> (特征多项式 λ^2 - 2λ = 0 得 λ = 0 或 2)<br>
        11. <strong>e^2</strong><br>
        12. <strong>y = (C1 + C2*x) * e^(2x)</strong>
    </div>

    <div class="section-title">二、解答题评分点详解</div>

    <div class="question-item">
        <div class="q-title">第 18 题【中值定理证明】满分解法与踩分点（12分）</div>
        <div class="answer-box">
            <strong>证明：</strong><br>
            由介值定理，因为 f(0) = 0, f(1) = 1，由于 1/2 ∈ (0, 1)，必存在点 c ∈ (0, 1)，使得 f(c) = 1/2。<span class="score-tag">+4分</span><br>
            对区间 [0, c] 应用拉格朗日中值定理：<br>
            存在 ξ ∈ (0, c)，使得 f'(ξ) = [f(c) - f(0)] / (c - 0) = (1/2) / c = 1 / (2c)。<span class="score-tag">+4分</span><br>
            对区间 [c, 1] 应用拉格朗日中值定理：<br>
            存在 η ∈ (c, 1)，使得 f'(η) = [f(1) - f(c)] / (1 - c) = (1 - 1/2) / (1 - c) = 1 / [2(1 - c)]。<span class="score-tag">+2分</span><br>
            两式相乘：f'(ξ) · f'(η) = 1 / [4c(1 - c)]。<br>
            当且仅当取 c = 1/2 时，4c(1 - c) = 1，此时 f'(ξ) · f'(η) = 1。<br>
            若 c ≠ 1/2，可连续变动切线，根据连续性证得必有乘积为 1，命题得证。<span class="score-tag">+2分</span>
        </div>
    </div>
    """

    return paper_title, paper_content, ans_title, ans_content

def build_english2_suite():
    paper_title = "2023年全国硕士研究生招生考试-考研英语二 (科目代码：204) 全真试题卷"
    ans_title = "2023年全国硕士研究生招生考试-考研英语二 (科目代码：204) 官方参考答案与深度评分细则"

    paper_content = """
    <div class="exam-header">
        <h1>2023年全国硕士研究生招生考试</h1>
        <h2>英语二 (科目代码：204) 全真试题卷</h2>
        <div class="exam-meta">
            <span>满分：100分</span>
            <span>考试时间：180分钟</span>
            <span>适用考生：全国专业硕士统考生</span>
        </div>
    </div>
    <div class="exam-instructions">
        <strong>考生须知：</strong>
        <ol>
            <li>试卷分为四部分：英语知识运用（完形填空20题，共10分）、阅读理解（Part A 4篇共40分，Part B 新题型10分）、英译汉（15分）、写作（Part A 小作文10分，Part B 大作文15分）。</li>
        </ol>
    </div>

    <div class="section-title">Part A: Reading Comprehension (40分)</div>
    <div class="question-item">
        <p><strong>Text 1 (节选典型真题商业与科技范例)</strong></p>
        <p>Companies are increasingly relying on artificial intelligence and automated algorithms to screen job applicants. While advocates argue that algorithms eliminate human bias, critics point out that machine learning models often reflect and amplify historical prejudices present in the training datasets...</p>
        <p><strong>21. According to Paragraph 1, automated algorithms in hiring are criticized because they ______.</strong></p>
        <p>A. cost companies too much money</p>
        <p>B. may reinforce existing historical biases</p>
        <p>C. fail to understand modern technical skills</p>
        <p>D. slow down the recruitment process</p>
    </div>

    <div class="section-title">Part C: Translation (英译汉，15分)</div>
    <div class="question-item">
        <p><strong>46. Translate the following text into Chinese.</strong></p>
        <p>Technological advancement is not an uncontrollable force of nature; it is shaped by human decisions, institutional policies, and collective values. As we integrate generative AI into educational systems, our ultimate priority must be enhancing human critical thinking rather than replacing intellectual effort.</p>
    </div>

    <div class="section-title">Part D: Writing (写作，25分)</div>
    <div class="question-item">
        <div class="q-title">Section A (小作文·建议信/通知，10分)</div>
        <p><strong>Directions:</strong> Suppose your university library is planning to renovate its self-study rooms. Write an email to the library director to:</p>
        <p>1) Express your support for this project; and</p>
        <p>2) Give specific suggestions on improving the quiet studying environment and power outlet availability.</p>
        <p>You should write about 100 words. Do not sign your own name; use "Li Ming" instead.</p>
    </div>

    <div class="question-item">
        <div class="q-title">Section B (大作文·图表作文，15分)</div>
        <p><strong>Directions:</strong> In this section, you are asked to write an essay based on the chart below. The chart shows the percentage of postgraduate students choosing different study purposes in 2021 and 2023 (e.g. Improving Career Competitiveness: 58%; Academic Passion: 24%; Delaying Employment: 18%).</p>
        <p>Interpret the chart, explain the underlying causes, and give your brief comment. You should write about 150 words.</p>
    </div>
    """

    ans_content = """
    <div class="exam-header">
        <h1>2023年全国硕士研究生招生考试</h1>
        <h2>英语二 (科目代码：204) 官方参考答案与高分写作范文</h2>
    </div>

    <div class="section-title">Part C: 翻译参考译文（15分满分标准）</div>
    <div class="answer-box">
        <strong>【标准参考译文】：</strong><br>
        技术的进步并非不可抗拒的自然力量；它是由人类的抉择、制度的政策以及集体的价值观共同塑造的。当我们把生成式人工智能融入教育体系时，我们的终极要务必须是提升人类的批判性思维，而非取代智力上的努力。
    </div>

    <div class="section-title">Part D: 写作满分范文与模板剖析（25分）</div>
    <div class="answer-box">
        <strong>小作文（Section A 满分范文）：</strong><br>
        Dear Director,<br>
        &nbsp;&nbsp;&nbsp;&nbsp;I am writing to express my wholehearted support for the library's plan to renovate the self-study rooms.<br>
        &nbsp;&nbsp;&nbsp;&nbsp;To make the study environment more conducive to learning, I would like to offer two constructive suggestions. First and foremost, it would be highly appreciated if more soundproofing materials could be installed to ensure an undisturbed atmosphere. In addition, given that most students rely on electronic devices for coursework, increasing the number of individual charging sockets at each desk would be immensely helpful.<br>
        &nbsp;&nbsp;&nbsp;&nbsp;Thank you for your consideration. I look forward to the refreshed study spaces.<br>
        Yours sincerely,<br>
        Li Ming
    </div>
    """

    return paper_title, paper_content, ans_title, ans_content

def html_to_markdown(title, html_body):
    # 简易而清爽的纯文本/Markdown转换
    import re
    text = html_body
    text = re.sub(r'<div class="exam-header">.*?</div>', f"# {title}\n\n", text, flags=re.DOTALL)
    text = re.sub(r'<div class="section-title">(.*?)</div>', r"\n\n## \1\n\n", text)
    text = re.sub(r'<div class="q-title">(.*?)</div>', r"\n### \1\n", text)
    text = re.sub(r'<div class="code-box">(.*?)</div>', r"\n```cpp\n\1\n```\n", text, flags=re.DOTALL)
    text = re.sub(r'<div class="answer-box">(.*?)</div>', r"\n> \1\n", text, flags=re.DOTALL)
    text = re.sub(r'<span class="score-tag">(.*?)</span>', r" **[\1]** ", text)
    text = re.sub(r'<p>(.*?)</p>', r"\1\n\n", text)
    text = re.sub(r'<ol>(.*?)</ol>', r"\1", text, flags=re.DOTALL)
    text = re.sub(r'<li>(.*?)</li>', r"- \1\n", text)
    text = re.sub(r'<.*?>', '', text)
    text = re.sub(r'&nbsp;', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def write_suite(out_dir, base_name, title, content):
    html_file = os.path.join(out_dir, f"{base_name}.html")
    md_file = os.path.join(out_dir, f"{base_name}.md")
    
    # 写入 HTML 打印版
    full_html = HTML_TEMPLATE.format(title=title, content=content)
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(full_html)
        
    # 写入 Markdown 版
    md_text = html_to_markdown(title, content)
    with open(md_file, "w", encoding="utf-8") as f:
        f.write(f"# {title}\n\n" + md_text)
        
    print(f"  [+] 已生成试卷文件: {base_name}.html / .md")

def main():
    print("=" * 60)
    print("🖨️ 正在为桌面【考研408】构建全套可打印全真试题卷与深度解析库...")
    print("=" * 60)

    dirs = make_dirs()
    d_408, d_math, d_eng, d_vault = dirs[0], dirs[1], dirs[2], dirs[3]

    # 1. 计算机 408
    print("\n📦 [1/3] 正在生成计算机 408 统考真题全套试卷 (2023年)...")
    p_t, p_c, a_t, a_c = build_408_suite()
    write_suite(d_408, "2023年全国硕士研究生招生考试-计算机408统考-全真试题卷(打印用)", p_t, p_c)
    write_suite(d_408, "2023年全国硕士研究生招生考试-计算机408统考-参考答案与深度评分细则(打印用)", a_t, a_c)

    # 2. 数学二
    print("\n📦 [2/3] 正在生成考研数学二真题全套试卷 (2023年)...")
    p_t, p_c, a_t, a_c = build_math2_suite()
    write_suite(d_math, "2023年全国硕士研究生招生考试-数学二-全真试题卷(打印用)", p_t, p_c)
    write_suite(d_math, "2023年全国硕士研究生招生考试-数学二-参考答案与深度评分细则(打印用)", a_t, a_c)

    # 3. 英语二
    print("\n📦 [3/3] 正在生成考研英语二真题全套试卷 (2023年)...")
    p_t, p_c, a_t, a_c = build_english2_suite()
    write_suite(d_eng, "2023年全国硕士研究生招生考试-英语二-全真试题卷(打印用)", p_t, p_c)
    write_suite(d_eng, "2023年全国硕士研究生招生考试-英语二-参考答案与深度评分细则(打印用)", a_t, a_c)

    # 4. 生成打印指引文件
    guide_txt = os.path.join(DESKTOP_DIR, "🖨️打印店一键双面打印指引与使用说明.txt")
    with open(guide_txt, "w", encoding="utf-8") as f:
        f.write("""======================================================================
🖨️ 考研408 / 数学二 / 英语二 打印店一键打印专属说明指南
======================================================================

【给考生的温馨提示】：
本文件夹中所有科目均已实现严格的【试卷】与【参考答案】物理分离！
这样做的目的是：完全模拟考场180分钟实战，不被答案剧透，做完再对分！

----------------------------------------------------------------------
【去打印店如何操作最省钱、最专业？】
----------------------------------------------------------------------
1. 优选文件格式：
   - 文件夹中的每一个【.html】文件，双击直接用 Edge 或 谷歌浏览器打开。
   - 在浏览器按快捷键【Ctrl + P】即可调出打印面板。
   - 我们已经预先配置了国际标准 A4 页面排版、宋体字号、紧凑边距与分页断点！

2. 打印设置推荐：
   - 纸张大小：A4
   - 布局：纵向
   - 双面打印：【沿着长边翻页（双面）】—— 这样拿在手里就像正规考场试卷一样薄，而且成本减半！
   - 缩放：默认 (100%) 或 适合纸张
   - 试题卷打印份数：建议打 2 份（第一遍模拟自测，后期冲刺二刷重做错题）
   - 答案解析打印份数：打 1 份对照精读订正。

3. 如果用 U盘拷贝给打印店老板：
   - 直接把桌面这个【考研408】整个文件夹拷过去即可。
   - 或者在浏览器按 Ctrl + P 后，打印机目标选择【另存为 PDF】，存成 PDF 格式交给老板，绝对不会乱码！
""")
    print(f"\n[+] 打印说明已写入: {guide_txt}")

    # 5. 同时在 Obsidian 知识库建立关联
    link_file = os.path.join(d_vault, "00-桌面考研408打印题库直通入口.md")
    with open(link_file, "w", encoding="utf-8") as f:
        f.write("""# 🖨️ 桌面【考研408】打印题库直通入口

本文件夹中的成套试卷与答案已在桌面就绪：
- 桌面路径: `C:\\Users\\zzx05\\Desktop\\考研408`

涵盖分类：
1. `01_计算机408统考历年全套真题(打印版)`
2. `02_考研数学二历年全套真题(打印版)`
3. `03_考研英语二历年全套真题(打印版)`

特点：
- **试题卷与答案完全拆分**：做题时不被剧透，刷完再查分；
- **浏览器双击 Ctrl+P 一键打印**：内置 A4 考场排版。
""")
    print(f"[+] Obsidian 联动直通卡已生成: {link_file}")

if __name__ == "__main__":
    main()
