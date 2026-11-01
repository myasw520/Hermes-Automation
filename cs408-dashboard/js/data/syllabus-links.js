// 408 知识点链路与跨学科深度命题连线
export const allLinks = [
            {
                        "source": "408",
                        "target": "DS"
            },
            {
                        "source": "408",
                        "target": "COA"
            },
            {
                        "source": "408",
                        "target": "OS"
            },
            {
                        "source": "408",
                        "target": "CN"
            },
            {
                        "source": "DS",
                        "target": "DS_Linear"
            },
            {
                        "source": "DS_Linear",
                        "target": "DS_FastSlow"
            },
            {
                        "source": "DS_Linear",
                        "target": "DS_StackQueue"
            },
            {
                        "source": "DS_Linear",
                        "target": "DS_Matrix"
            },
            {
                        "source": "DS",
                        "target": "DS_Tree"
            },
            {
                        "source": "DS_Tree",
                        "target": "DS_Traversal"
            },
            {
                        "source": "DS_Tree",
                        "target": "DS_Huffman"
            },
            {
                        "source": "DS_Tree",
                        "target": "DS_BST_AVL"
            },
            {
                        "source": "DS_Tree",
                        "target": "DS_RBT"
            },
            {
                        "source": "DS",
                        "target": "DS_Graph"
            },
            {
                        "source": "DS_Graph",
                        "target": "DS_MST"
            },
            {
                        "source": "DS_Graph",
                        "target": "DS_ShortestPath"
            },
            {
                        "source": "DS_Graph",
                        "target": "DS_TopoCritical"
            },
            {
                        "source": "DS",
                        "target": "DS_Search"
            },
            {
                        "source": "DS_Search",
                        "target": "DS_BTree"
            },
            {
                        "source": "DS",
                        "target": "DS_Sort"
            },
            {
                        "source": "COA",
                        "target": "COA_Data"
            },
            {
                        "source": "COA_Data",
                        "target": "COA_IEEE754"
            },
            {
                        "source": "COA",
                        "target": "COA_Mem"
            },
            {
                        "source": "COA_Mem",
                        "target": "COA_Cache"
            },
            {
                        "source": "COA_Mem",
                        "target": "COA_VirtMem"
            },
            {
                        "source": "COA",
                        "target": "COA_Inst"
            },
            {
                        "source": "COA",
                        "target": "COA_Datapath"
            },
            {
                        "source": "COA",
                        "target": "COA_Pipeline"
            },
            {
                        "source": "COA",
                        "target": "COA_Bus"
            },
            {
                        "source": "COA_Bus",
                        "target": "COA_Interrupt"
            },
            {
                        "source": "COA_Bus",
                        "target": "COA_DMA"
            },
            {
                        "source": "OS",
                        "target": "OS_Process"
            },
            {
                        "source": "OS_Process",
                        "target": "OS_PV"
            },
            {
                        "source": "OS_Process",
                        "target": "OS_Deadlock"
            },
            {
                        "source": "OS",
                        "target": "OS_Mem"
            },
            {
                        "source": "OS",
                        "target": "OS_File"
            },
            {
                        "source": "OS_File",
                        "target": "OS_Disk"
            },
            {
                        "source": "CN",
                        "target": "CN_Arch"
            },
            {
                        "source": "CN_Arch",
                        "target": "CN_Physical"
            },
            {
                        "source": "CN",
                        "target": "CN_DataLink"
            },
            {
                        "source": "CN_DataLink",
                        "target": "CN_MAC"
            },
            {
                        "source": "CN",
                        "target": "CN_Network"
            },
            {
                        "source": "CN_Network",
                        "target": "CN_RouteProto"
            },
            {
                        "source": "CN",
                        "target": "CN_TCP"
            },
            {
                        "source": "CN_TCP",
                        "target": "CN_Congest"
            },
            {
                        "source": "CN",
                        "target": "CN_App"
            },
            {
                        "source": "COA_VirtMem",
                        "target": "OS_Mem",
                        "cross": true,
                        "label": "硬件页表与操作系统虚拟内存分页交互"
            },
            {
                        "source": "COA_Cache",
                        "target": "COA_VirtMem",
                        "cross": true,
                        "label": "TLB快表与Cache并发查询机制"
            },
            {
                        "source": "COA_Interrupt",
                        "target": "OS_Process",
                        "cross": true,
                        "label": "硬件中断引出系统调用与进程上下文切换"
            },
            {
                        "source": "COA_DMA",
                        "target": "OS_Disk",
                        "cross": true,
                        "label": "磁盘块直接内存存取传输"
            },
            {
                        "source": "DS_BTree",
                        "target": "OS_File",
                        "cross": true,
                        "label": "B+树在文件系统inode与数据库索引中的物理实现"
            },
            {
                        "source": "OS_Process",
                        "target": "CN_TCP",
                        "cross": true,
                        "label": "操作系统Socket套接字绑定与传输层端口通信"
            },
            {
                        "source": "DS_ShortestPath",
                        "target": "CN_RouteProto",
                        "cross": true,
                        "label": "Dijkstra算法在OSPF链路状态路由中的实际应用"
            }
];
