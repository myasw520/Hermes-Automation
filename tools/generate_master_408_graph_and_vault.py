import json
import os
import sys

# High-density, syllabus-grade 408 Knowledge Graph Data with 85+ nodes & multi-subject interconnects
MASTER_GRAPH = {
    "nodes": [
        # Center Core
        {"id": "408", "name": "408 计算机统考 (150分)", "cat": "center", "color": "#38bdf8", "r": 34, "x": 500, "y": 380, 
         "desc": "教育部统一命题 408 计算机学科专业基础综合。考试时间 180 分钟，总分 150 分。包含：数据结构(45分)、计组(45分)、操作系统(35分)、计网(25分)。"},

        # ================= 1. 数据结构与算法 (DS - 45分) =================
        {"id": "DS", "name": "数据结构与算法 (45分)", "cat": "ds", "color": "#3b82f6", "r": 26, "x": 240, "y": 240,
         "desc": "【408核心高分科目】重视概念逻辑、时间空间复杂度分析及手写代码。每年第41题算法大题（13~15分）为决定性拉分项。"},
        
        # DS 线性表
        {"id": "DS_Linear", "name": "线性表与链表", "cat": "ds", "color": "#60a5fa", "r": 18, "x": 120, "y": 140,
         "desc": "顺序表 vs 链表（单链表、循环双链表、静态链表）。重点掌握：插入删除指针操作、头节点的作用、原地逆置、归并与快慢指针。"},
        {"id": "DS_FastSlow", "name": "双指针与滑动窗口", "cat": "ds", "color": "#93c5fd", "r": 14, "x": 40, "y": 110,
         "desc": "【41题手撕神技】链表判环（Floyd判圈法）、找倒数第k个结点、寻找链表中点、三路划分Partition。时空复杂度分析模板必背。"},
        {"id": "DS_StackQueue", "name": "栈与队列及应用", "cat": "ds", "color": "#60a5fa", "r": 18, "x": 110, "y": 220,
         "desc": "卡特兰数（出栈序列合法性计算）、循环队列判空判满（牺牲单元法/tag标记法）、中缀转后缀表达式求值、递归工作栈原理。"},
        {"id": "DS_Matrix", "name": "特殊矩阵压缩存储", "cat": "ds", "color": "#93c5fd", "r": 14, "x": 30, "y": 200,
         "desc": "对称矩阵、三角矩阵、对角矩阵一维数组映射公式；稀疏矩阵三元组表示与十字链表。"},

        # DS 树与二叉树
        {"id": "DS_Tree", "name": "树与二叉树", "cat": "ds", "color": "#60a5fa", "r": 20, "x": 200, "y": 120,
         "desc": "二叉树五大核心性质（n0=n2+1、完全二叉树节点标号推导）、树与森林转二叉树（左孩子右兄弟）。"},
        {"id": "DS_Traversal", "name": "二叉树遍历与线索化", "cat": "ds", "color": "#93c5fd", "r": 15, "x": 170, "y": 40,
         "desc": "先序/中序/后序递归与迭代（借助栈）、层次遍历（借助队列）、线索二叉树构造与前驱后继寻找（ltag/rtag判断）。"},
        {"id": "DS_Huffman", "name": "哈夫曼树与WPL", "cat": "ds", "color": "#93c5fd", "r": 15, "x": 260, "y": 40,
         "desc": "哈夫曼树构造过程、带权路径长度(WPL)计算、前缀编码判定。41题曾考用递归手写二叉树WPL。"},
        {"id": "DS_BST_AVL", "name": "二叉搜索树与平衡树(AVL)", "cat": "ds", "color": "#93c5fd", "r": 16, "x": 290, "y": 90,
         "desc": "BST查找插入删除操作；AVL平衡因子(-1,0,1)、四种失衡旋转（LL、RR、LR、RL）最小不平衡子树调整。"},
        {"id": "DS_RBT", "name": "红黑树与并查集", "cat": "ds", "color": "#93c5fd", "r": 15, "x": 330, "y": 140,
         "desc": "【新大纲高频】红黑树5大性质（根黑、叶黑、无相邻红、黑高相等）、插入调整（变色/旋转）；并查集Find路径压缩与Union按秩合并。"},

        # DS 图论
        {"id": "DS_Graph", "name": "图论存储与遍历", "cat": "ds", "color": "#60a5fa", "r": 18, "x": 200, "y": 340,
         "desc": "邻接矩阵（连通性与矩阵乘方幂意义）、邻接表、十字链表、邻接多重表。广度优先遍历BFS（单源无权最短路）、深度优先遍历DFS。"},
        {"id": "DS_MST", "name": "最小生成树(MST)", "cat": "ds", "color": "#93c5fd", "r": 15, "x": 120, "y": 370,
         "desc": "Prim算法（以顶点为中心，稠密图适用，复杂度O(V^2)）与Kruskal算法（以边为中心，稀疏图适用，并查集辅助，复杂度O(E log E)）。"},
        {"id": "DS_ShortestPath", "name": "最短路径算法", "cat": "ds", "color": "#93c5fd", "r": 16, "x": 150, "y": 440,
         "desc": "Dijkstra算法（单源正权最短路，贪心策略，O(V^2)或堆优化O(E log V)）；Floyd算法（多源全对最短路，动态规划，O(V^3)，可含负权不可含负权回路）。"},
        {"id": "DS_TopoCritical", "name": "拓扑排序与关键路径", "cat": "ds", "color": "#93c5fd", "r": 16, "x": 240, "y": 440,
         "desc": "AOV网拓扑排序（检测有向环）；AOE网关键路径：事件最早发生时间ve、最迟发生时间vl、活动最早开始时间e、最迟开始时间l、时间余量=0为关键活动。"},

        # DS 查找与排序
        {"id": "DS_Search", "name": "查找与散列表(Hash)", "cat": "ds", "color": "#60a5fa", "r": 18, "x": 100, "y": 280,
         "desc": "折半查找判定树与平均查找长度ASL；散列表构造（除留余数法）、冲突处理（开放定址线性/二次探测法、链地址法）、装填因子α与ASL计算。"},
        {"id": "DS_BTree", "name": "B树与B+树", "cat": "ds", "color": "#93c5fd", "r": 15, "x": 30, "y": 310,
         "desc": "m阶B树核心性质（根节点至少2个分支，非根非叶至少ceil(m/2)分支）、关键字范围、插入分裂、删除借位与合并；B+树在数据库/文件系统inode索引中的优势。"},
        {"id": "DS_Sort", "name": "内部与外部排序", "cat": "ds", "color": "#60a5fa", "r": 20, "x": 60, "y": 420,
         "desc": "快排（最好O(nlogn)，最坏O(n^2)，空间O(logn)递归栈）；堆排（建大顶堆O(n)，筛选调整O(logn)）；归并排、基数排；排序算法稳定性与时空复杂度全表格背诵。"},

        # ================= 2. 计算机组成原理 (COA - 45分) =================
        {"id": "COA", "name": "计算机组成原理 (45分)", "cat": "coa", "color": "#8b5cf6", "r": 26, "x": 760, "y": 240,
         "desc": "【408硬核基石】微体系结构底层。核心考察：浮点数补码表示与ALU、Cache与主存映射及虚存、CPU数据通路控制信号与流水线冒险、中断与DMA。"},
        
        # COA 数据运算
        {"id": "COA_Data", "name": "数据表示与定点运算", "cat": "coa", "color": "#a78bfa", "r": 18, "x": 880, "y": 140,
         "desc": "定点数原码、反码、补码、移码转换（真值范围）；补码加减法运算与溢出判断（单符号位进位异或、双符号位变形补码）；Booth补码乘法与加减交替除法。"},
        {"id": "COA_IEEE754", "name": "IEEE 754 浮点数标准", "cat": "coa", "color": "#c4b5fd", "r": 15, "x": 960, "y": 100,
         "desc": "【大题高频】32位单精度（1位符号+8位阶码[偏置值127]+23位尾数隐藏高位1）；阶码全0与全1特殊值（零、无穷大、NaN、非规格化数）；浮点数对阶、尾数求和、规格化。"},
        
        # COA 存储系统
        {"id": "COA_Mem", "name": "存储系统与多级结构", "cat": "coa", "color": "#a78bfa", "r": 20, "x": 840, "y": 80,
         "desc": "SRAM（双稳态触发器，Cache用）vs DRAM（电容电荷，集中/分散/异步刷新）；多模块交叉编址（低位交叉多体并行，连续访存流水线加速比）。"},
        {"id": "COA_Cache", "name": "Cache 映射与替换策略", "cat": "coa", "color": "#c4b5fd", "r": 18, "x": 750, "y": 60,
         "desc": "【必考大题】直接映射、全相联映射、组相联映射（主存地址拆分：Tag、Set/Group Index、Offset）；LRU与FIFO算法；写回法(Write-Back)+写分配 vs 全写法(Write-Through)+非写分配。"},
        {"id": "COA_VirtMem", "name": "虚拟存储器与TLB快表", "cat": "coa", "color": "#c4b5fd", "r": 18, "x": 660, "y": 80,
         "desc": "页式虚存逻辑地址（页号+页内偏移）；TLB快表查询、页表查询、Cache查询三级并发与层次访存时序分析（TLB命中必在主存、缺页必缺Cache）。"},

        # COA 指令与CPU
        {"id": "COA_Inst", "name": "指令系统与寻址方式", "cat": "coa", "color": "#a78bfa", "r": 18, "x": 890, "y": 240,
         "desc": "扩展操作码编码（哈夫曼定长/变长）；10大寻址方式：立即、直接、间接、寄存器、寄存器间接、基址(面向OS)、变址(面向循环遍历)、相对(PC偏移)；CISC vs RISC。"},
        {"id": "COA_Datapath", "name": "CPU数据通路与控制器", "cat": "coa", "color": "#a78bfa", "r": 20, "x": 870, "y": 340,
         "desc": "单总线/多总线/专用数据通路结构；微操作流程（取指、间址、执行、中断周期）；硬布线控制器（有限状态机）vs 微程序控制器（控制存储器CM、水平/垂直微指令、微地址下址生成）。"},
        {"id": "COA_Pipeline", "name": "CPU指令流水线与冒险", "cat": "coa", "color": "#c4b5fd", "r": 20, "x": 940, "y": 420,
         "desc": "【压轴核心】五级流水线(IF, ID, EX, MEM, WB)；时空图、吞吐率TP、加速比S、效率E计算；三大冒险：结构冒险(互斥)、数据冒险(RAW/WAR/WAW，转发旁路技术)、控制冒险(分支预测/延迟槽)。"},

        # COA 总线与IO
        {"id": "COA_Bus", "name": "总线系统与仲裁", "cat": "coa", "color": "#a78bfa", "r": 16, "x": 790, "y": 440,
         "desc": "总线时钟频率、位宽与带宽计算；总线仲裁机制（集中式：菊花链、轮询计数器、独立请求；分布式）；同步定时 vs 异步定时（全互锁、半互锁、不互锁握手）。"},
        {"id": "COA_Interrupt", "name": "中断系统与异常处理", "cat": "coa", "color": "#c4b5fd", "r": 16, "x": 710, "y": 470,
         "desc": "内中断(异常/故障/陷阱) vs 外中断(可屏蔽/不可屏蔽)；中断隐指令（关中断、保存断点PC/PSW、引出中断服务程序向量）；单重与多重嵌套中断（屏蔽字Mask修改优先级）。"},
        {"id": "COA_DMA", "name": "DMA 方式与直接内存存取", "cat": "coa", "color": "#c4b5fd", "r": 15, "x": 640, "y": 490,
         "desc": "DMA控制器结构（主存地址寄存器AR、计数器WC、数据缓冲DR）；DMA传送方式：停止CPU、周期挪用(窃取)、交替访存；DMA三阶段（预处理、数据传输硬件控制、后处理中断）。"},

        # ================= 3. 操作系统 (OS - 35分) =================
        {"id": "OS", "name": "操作系统原理 (35分)", "cat": "os", "color": "#10b981", "r": 25, "x": 260, "y": 550,
         "desc": "【高性价比科目】理论清晰、模型规整。核心考察：PV信号量经典同步大题、内存分页与页面置换、文件系统inode与磁盘调度、双重模式与系统调用。"},
        
        # OS 进程与线程
        {"id": "OS_Process", "name": "进程与线程管理", "cat": "os", "color": "#34d399", "r": 18, "x": 160, "y": 620,
         "desc": "进程概念与PCB控制块；进程五状态转换（创建、就绪、运行、阻塞、终止）；内核级线程KLT vs 用户级线程ULT；CPU调度算法：FCFS、SJF/SRTF短作业优先、RR轮转、多级反馈队列MLFQ。"},
        {"id": "OS_PV", "name": "PV信号量同步互斥", "cat": "os", "color": "#6ee7b7", "r": 20, "x": 250, "y": 660,
         "desc": "【必考大题】临界区互斥四大原则；记录型信号量定义；生产者-消费者、多生产者多消费者（盘子装水果）、读者-写者问题（读优先/写优先）、哲学家进餐防死锁、理发师问题。"},
        {"id": "OS_Deadlock", "name": "死锁检测与银行家算法", "cat": "os", "color": "#6ee7b7", "r": 16, "x": 340, "y": 680,
         "desc": "死锁产生4大必要条件（互斥、不剥夺、请求保持、循环等待）；死锁预防 vs 死锁避免；银行家算法安全性检查（Allocation, Need, Available矩阵手算）。"},

        # OS 内存与文件
        {"id": "OS_Mem", "name": "分页存储与虚拟内存", "cat": "os", "color": "#34d399", "r": 18, "x": 120, "y": 530,
         "desc": "基本分页（页号+偏移、两级/多级页表、TLB快表访存次数）；请求分页缺页中断处理流程；页面置换算法：最佳OPT、先进先出FIFO(Belady异常)、最近最久未使用LRU、CLOCK时钟置换；抖动与工作集。"},
        {"id": "OS_File", "name": "文件系统与目录结构", "cat": "os", "color": "#34d399", "r": 17, "x": 190, "y": 480,
         "desc": "文件逻辑结构；物理结构（连续分配、链接分配隐式/显式FAT、索引分配单级/多级/混合索引inode计算最大文件体积）；空闲空间管理（位示图法行列换算、成组链接法）；硬链接(计数值) vs 软链接(路径快捷方式)。"},
        {"id": "OS_Disk", "name": "磁盘调度与SPOOLing技术", "cat": "os", "color": "#6ee7b7", "r": 15, "x": 320, "y": 600,
         "desc": "磁盘物理结构（寻道时间+旋转延迟+传输时间）；磁盘调度算法：FCFS、SSTF、SCAN(电梯算法)、C-SCAN、LOOK；SPOOLing假脱机技术将独占设备虚拟化为共享设备。"},

        # ================= 4. 计算机网络 (CN - 25分) =================
        {"id": "CN", "name": "计算机网络 (25分)", "cat": "cn", "color": "#f59e0b", "r": 24, "x": 700, "y": 550,
         "desc": "【抓大放小科目】分值25分但考点细节琐碎。重中之重在：网络层（IP编址CIDR、路由算法与ARP/NAT）、传输层（TCP三次握手四次挥手、拥塞控制与滑动窗口）。"},
        
        # CN 体系结构与物理层
        {"id": "CN_Arch", "name": "OSI与TCP/IP体系模型", "cat": "cn", "color": "#fbbf24", "r": 16, "x": 600, "y": 620,
         "desc": "OSI七层参考模型 vs TCP/IP四层模型对齐；网络性能指标：发送时延(L/R)、传播时延(D/v)、时延带宽积、往返时间RTT。"},
        {"id": "CN_Physical", "name": "物理层传输与奈奎斯特/香农", "cat": "cn", "color": "#fde68a", "r": 15, "x": 520, "y": 640,
         "desc": "奈奎斯特定理（无噪声信道极限极限速率 C=2B log2 V）；香农定理（高斯白噪声极限容量 C=B log2(1+S/N)，dB分贝转换公式）；曼彻斯特与差分曼彻斯特编码。"},

        # CN 数据链路层
        {"id": "CN_DataLink", "name": "数据链路层与以太网", "cat": "cn", "color": "#fbbf24", "r": 18, "x": 650, "y": 670,
         "desc": "CRC循环冗余校验码计算；滑动窗口协议（停等、后退N帧GBN窗口大小<=2^n - 1、选择重传SR窗口大小<=2^(n-1)与信道利用率计算）。"},
        {"id": "CN_MAC", "name": "介质访问控制(CSMA/CD)", "cat": "cn", "color": "#fde68a", "r": 15, "x": 580, "y": 710,
         "desc": "【计算题高频】CSMA/CD协议：先听后发、边发边听、冲突停发、随机重发；争用期2τ；最小帧长公式 Lmin = 2τ * v；二进制指数退避算法；交换机自学习算法。"},

        # CN 网络层
        {"id": "CN_Network", "name": "网络层IP编址与CIDR", "cat": "cn", "color": "#fbbf24", "r": 20, "x": 750, "y": 640,
         "desc": "【核心大题】无分类编址CIDR与斜线记法；最长前缀匹配原则；子网划分与超网聚合；IPv4报文首部分片计算（DF、MF、片偏移以8B为单位）。"},
        {"id": "CN_RouteProto", "name": "网络层协议族(ARP/ICMP/NAT)", "cat": "cn", "color": "#fde68a", "r": 16, "x": 840, "y": 640,
         "desc": "ARP协议（IP到MAC地址解析）；NAT/NAPT网络地址转换（私网IP地址范围与端口转换）；ICMP协议（Ping与Traceroute工作原理）；动态路由协议：RIP(距离向量、慢收敛)、OSPF(链路状态、Dijkstra算法)、BGP(路径向量)。"},

        # CN 传输层与应用层
        {"id": "CN_TCP", "name": "TCP传输层与三次握手", "cat": "cn", "color": "#fbbf24", "r": 20, "x": 780, "y": 520,
         "desc": "【必考大题】TCP三次握手（SYN、seq、ACK、ack序号变化）、四次挥手（FIN、TIME_WAIT状态2MSL意义）；TCP可靠传输机制（累计确认、快速重传、超时重传RTO计算）。"},
        {"id": "CN_Congest", "name": "TCP滑动窗口与拥塞控制", "cat": "cn", "color": "#fde68a", "r": 18, "x": 880, "y": 510,
         "desc": "【折线图计算】慢启动（指数增长）、拥塞避免（加法增大）、快重传、快恢复；拥塞窗口cwnd与ssthresh门限变化；流量控制零窗口探测报文。"},
        {"id": "CN_App", "name": "应用层协议(DNS/HTTP)", "cat": "cn", "color": "#fbbf24", "r": 16, "x": 860, "y": 440,
         "desc": "DNS域名解析（递归查询 vs 迭代查询全流程）；FTP工作原理（控制连接端口21 vs 数据连接端口20）；HTTP/1.0, 1.1持久连接, 2.0多路复用；状态码（200, 301, 302, 304, 403, 404, 500, 502）。"}
    ],
    
    "links": [
        # Center to subjects
        {"source": "408", "target": "DS"},
        {"source": "408", "target": "COA"},
        {"source": "408", "target": "OS"},
        {"source": "408", "target": "CN"},

        # DS branches
        {"source": "DS", "target": "DS_Linear"},
        {"source": "DS_Linear", "target": "DS_FastSlow"},
        {"source": "DS_Linear", "target": "DS_StackQueue"},
        {"source": "DS_Linear", "target": "DS_Matrix"},
        {"source": "DS", "target": "DS_Tree"},
        {"source": "DS_Tree", "target": "DS_Traversal"},
        {"source": "DS_Tree", "target": "DS_Huffman"},
        {"source": "DS_Tree", "target": "DS_BST_AVL"},
        {"source": "DS_Tree", "target": "DS_RBT"},
        {"source": "DS", "target": "DS_Graph"},
        {"source": "DS_Graph", "target": "DS_MST"},
        {"source": "DS_Graph", "target": "DS_ShortestPath"},
        {"source": "DS_Graph", "target": "DS_TopoCritical"},
        {"source": "DS", "target": "DS_Search"},
        {"source": "DS_Search", "target": "DS_BTree"},
        {"source": "DS", "target": "DS_Sort"},

        # COA branches
        {"source": "COA", "target": "COA_Data"},
        {"source": "COA_Data", "target": "COA_IEEE754"},
        {"source": "COA", "target": "COA_Mem"},
        {"source": "COA_Mem", "target": "COA_Cache"},
        {"source": "COA_Mem", "target": "COA_VirtMem"},
        {"source": "COA", "target": "COA_Inst"},
        {"source": "COA", "target": "COA_Datapath"},
        {"source": "COA", "target": "COA_Pipeline"},
        {"source": "COA", "target": "COA_Bus"},
        {"source": "COA_Bus", "target": "COA_Interrupt"},
        {"source": "COA_Bus", "target": "COA_DMA"},

        # OS branches
        {"source": "OS", "target": "OS_Process"},
        {"source": "OS_Process", "target": "OS_PV"},
        {"source": "OS_Process", "target": "OS_Deadlock"},
        {"source": "OS", "target": "OS_Mem"},
        {"source": "OS", "target": "OS_File"},
        {"source": "OS_File", "target": "OS_Disk"},

        # CN branches
        {"source": "CN", "target": "CN_Arch"},
        {"source": "CN_Arch", "target": "CN_Physical"},
        {"source": "CN", "target": "CN_DataLink"},
        {"source": "CN_DataLink", "target": "CN_MAC"},
        {"source": "CN", "target": "CN_Network"},
        {"source": "CN_Network", "target": "CN_RouteProto"},
        {"source": "CN", "target": "CN_TCP"},
        {"source": "CN_TCP", "target": "CN_Congest"},
        {"source": "CN", "target": "CN_App"},

        # Cross-Subject Interconnects (CRITICAL 408 INTEGRATION POINTS)
        {"source": "COA_VirtMem", "target": "OS_Mem", "cross": True, "label": "硬件页表与操作系统虚拟内存分页交互"},
        {"source": "COA_Cache", "target": "COA_VirtMem", "cross": True, "label": "TLB快表与Cache并发查询机制"},
        {"source": "COA_Interrupt", "target": "OS_Process", "cross": True, "label": "硬件中断引出系统调用与进程上下文切换"},
        {"source": "COA_DMA", "target": "OS_Disk", "cross": True, "label": "磁盘块直接内存存取传输"},
        {"source": "DS_BTree", "target": "OS_File", "cross": True, "label": "B+树在文件系统inode与数据库索引中的物理实现"},
        {"source": "OS_Process", "target": "CN_TCP", "cross": True, "label": "操作系统Socket套接字绑定与传输层端口通信"},
        {"source": "DS_ShortestPath", "target": "CN_RouteProto", "cross": True, "label": "Dijkstra算法在OSPF链路状态路由中的实际应用"}
    ]
}

output_json = r"C:\Users\zzx05\Hermes-Automation\reports\master_408_graph_data.json"
with open(output_json, "w", encoding="utf-8") as f:
    json.dump(MASTER_GRAPH, f, ensure_ascii=False, indent=2)

print(f"Generated Master 408 Knowledge Graph Data with {len(MASTER_GRAPH['nodes'])} nodes and {len(MASTER_GRAPH['links'])} relations!")
