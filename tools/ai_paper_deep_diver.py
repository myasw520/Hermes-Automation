#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Frontier Papers & Tech Reports Deep Diver (前沿 AI 顶级论文逐行精读与工程落地踩坑库)
====================================================================================
深度拆解行业里程碑级论文 (DeepSeek-R1/V3, vLLM, FlashAttention-3, MCP, Llama 3, BitNet):
- 核心破局点与数学公式推导
- 工业级真实工程踩坑指南 (CUDA/NCCL/显存碎片/量化溢出)
- 极简极客 Python/PyTorch 核心实现复现
- 架构设计与顶级面试金句总结
"""

import os
import sys
import json
import time
import argparse
import urllib.request
import urllib.error
from datetime import datetime

# Windows 终端 UTF-8 编码安全重置
try:
    if sys.stdout.encoding.lower() != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
    if sys.stderr.encoding.lower() != 'utf-8':
        sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

import functools
print = functools.partial(print, flush=True)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAPER_DIR = os.path.join(PROJECT_ROOT, "data", "ai_paper_vault")

GATEWAY_URL = os.environ.get("GATEWAY_URL", "http://100.114.18.45:7863/v1/chat/completions")
# 网关凭证统一从项目根 .env 读取（config_lib），不再硬编码
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "services"))
from config_lib import GATEWAY_KEY as _ENV_GATEWAY_KEY
GATEWAY_KEY = os.environ.get("GATEWAY_KEY") or _ENV_GATEWAY_KEY
MODEL_NAME = os.environ.get("MODEL_NAME", "workbuddy/glm-5.3-flash")

# 8 篇重塑当前 AI 工业界的里程碑级技术报告与论文
CURATED_PAPERS = [
    {
        "id": "deepseek_r1",
        "title": "DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning",
        "authors": "DeepSeek-AI",
        "date": "2025-01",
        "keywords": ["GRPO", "Pure RL", "Cold Start", "Distillation", "Aha Moment", "Reward Engineering"],
        "summary": "不依赖海量人工标注 SFT，通过纯强化学习（Pure RL）与组相对策略优化（GRPO）直接涌现复杂长思维链推理能力，并揭示蒸馏比大模型继续RL更具泛化性的惊天事实。"
    },
    {
        "id": "deepseek_v3",
        "title": "DeepSeek-V3 Technical Report",
        "authors": "DeepSeek-AI",
        "date": "2024-12",
        "keywords": ["MLA (Multi-head Latent Attention)", "DeepSeekMoE", "DualPipe", "FP8 Mixed Precision", "Multi-Token Prediction"],
        "summary": "开源最强 671B 基础大模型！用多头潜在注意力（MLA）把 KV Cache 压减数倍，辅以无额外辅助损失的负载均衡 MoE 与 DualPipe 计算通信掩盖，彻底颠覆训练成本。"
    },
    {
        "id": "vllm_paged_attention",
        "title": "vLLM: Efficient Memory Management for Large Language Model Serving with PagedAttention",
        "authors": "UC Berkeley (Woosuk Kwon et al.)",
        "date": "2023-09",
        "keywords": ["PagedAttention", "KV Cache Fragmentation", "Virtual Memory", "Continuous Batching", "Copy-on-Write"],
        "summary": "大模型高并发推理基础设施基石！借鉴操作系统虚拟内存分页机制解决 KV Cache 内部与外部碎片浪费，将服务并发吞吐提升 2~4 倍。"
    },
    {
        "id": "flash_attention_3",
        "title": "FlashAttention-3: Fast and Memory-Efficient Exact Attention with Asynchrony and Low-Precision",
        "authors": "Jay Shah, Tri Dao et al.",
        "date": "2024-07",
        "keywords": ["Hopper Architecture", "TMA (Tensor Memory Accelerator)", "Warp-Specialization", "Ping-pong GEMM", "FP8 Quantization"],
        "summary": "针对 NVIDIA Hopper 架构的极限硬件算力压榨，通过 Warp 专业化与异步张量加载（TMA）实现计算与数据搬运的完美重叠，速度比 FlashAttention-2 再翻一倍。"
    },
    {
        "id": "anthropic_mcp",
        "title": "Model Context Protocol (MCP) Architecture & Protocol Specification",
        "authors": "Anthropic",
        "date": "2024-11",
        "keywords": ["JSON-RPC 2.0", "stdio / SSE Transports", "Tools / Resources / Prompts", "Client-Host-Server", "Agent Standard"],
        "summary": "AI Agent 工具交互的“USB-C 工业标准”。解耦模型客户端与外部数据源工具，统一协议治理，彻底终结各个框架私有 tool_call 的混乱局面。"
    },
    {
        "id": "llama_3_herd",
        "title": "The Llama 3 Herd of Models",
        "authors": "Meta AI",
        "date": "2024-07",
        "keywords": ["15T Tokens Scaling", "Dense Decoder", "GQA", "Synthetic Data Quality Filtering", "DPO & PPO Annealing"],
        "summary": "目前最详尽的工业级万亿参数大模型训练全流程工程实录。详细披露了 1.6 万张 H100 集群故障治理、合成数据退火清洗与后训练对齐的细节。"
    },
    {
        "id": "bitnet_b158",
        "title": "The Era of 1-bit LLMs: All Large Language Models are in 1.58 Bits",
        "authors": "Microsoft Research",
        "date": "2024-02",
        "keywords": ["Ternary Weights {-1, 0, 1}", "BitLinear", "Multiplication-Free GEMM", "Energy Efficiency", "Edge Deployment"],
        "summary": "终结浮点乘法的激进探索！模型权重仅由三元值 {-1, 0, 1} 构成，将昂贵的矩阵乘法退化为纯整数加法，功耗与显存实现数量级暴降。"
    },
    {
        "id": "agentic_patterns",
        "title": "Agentic Design Patterns & Autonomous Multi-Agent Swarms",
        "authors": "Andrew Ng / Multi-Agent Community",
        "date": "2024-06",
        "keywords": ["Reflection", "Tool Use", "Planning", "Multi-Agent Collaboration", "Error Recovery Loop"],
        "summary": "超越单次 Prompt 调用的智能体范式总结。系统阐释自我反思（Reflection）、工具动态路由、多智能体层级编排（Orchestrator-Subagent）如何将任务成功率提升数倍。"
    }
]

def analyze_paper_with_llm(paper):
    prompt = f"""你是一位深耕大模型基础设施、对底层 CUDA/分布式训练/推理优化了如指掌的顶级 AI 首席架构师。
现在请对以下行业里程碑级论文/技术报告进行极其详尽、干货拉满的【逐行精读与工程落地踩坑剖析】：

【论文信息】
- 论文标识: {paper['id']}
- 论文标题: {paper['title']}
- 作者/机构: {paper['authors']} ({paper['date']})
- 核心关键词: {', '.join(paper['keywords'])}
- 官方摘要/背景: {paper['summary']}

【深度剖析要求】
请撰写一份万字级硬核技术指南（Markdown 格式），绝不讲宽泛概念，必须直击底层工程核心，包含以下五个核心板块：

### 1. 核心破局动机与痛点推演
- 传统主流方案（旧范式）到底死在什么地方？（用具体的显存公式、通信延迟、或算力瓶颈说话）。
- 本文提出了什么颠覆性的设计思想？用最通俗直白的底层物理逻辑把它讲透。

### 2. 数学公式与算法底层推导
- 挑选本文最关键的 2~3 个核心公式（如 MLA 的降维低秩投影矩阵运算、GRPO 的无 Critic 目标函数、PagedAttention 的块映射寻址）。
- 详细推导变量含义、维度变化与计算复杂度，写出每一步推导的物理直觉。

### 3. 工业界真实落地工程踩坑避雷指南 (极客重点)
- 在真实显卡集群（H100/A100）或工业级微调/推理部署时，有哪些文献里轻描淡写但实际会“踩大雷”的深坑？
  - 显存碎片与对齐坑（Memory Alignment / Bank Conflicts）。
  - 分布式通信坑（All-to-All / NCCL 通信死锁与流水线气泡 Bubble）。
  - 数值精度与溢出坑（FP8 下溢、梯度爆炸、量化掉点）。
  - 动态调度与吞吐崩塌坑。

### 4. 极简极客源码复现 (Minimal Reproducible PyTorch/Python 实现)
- 提供一段约 60~100 行、纯粹、高可读性的最小核心代码实现（例如：纯 PyTorch 手写 MLA 投影、手写 PagedAttention 模拟逻辑、手写 GRPO 优势度计算）。
- 关键代码必须包含详细行内中文注解。

### 5. 顶尖大厂技术评审与架构设计必问考核题
- 提炼出 3 道如果去 OpenAI、DeepSeek 或大厂 AI Infra 团队面试时，首席科学家最可能刁难你的硬核追问及满分标准答案。
"""

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }
    data_bytes = json.dumps(payload).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GATEWAY_KEY}"
    }

    try:
        t0 = time.time()
        req = urllib.request.Request(GATEWAY_URL, data=data_bytes, headers=headers)
        with urllib.request.urlopen(req, timeout=150) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            elapsed = time.time() - t0
            content = result["choices"][0]["message"]["content"].strip()
            tokens = result.get("usage", {}).get("total_tokens", 0)
            return content, tokens, elapsed
    except Exception as e:
        print(f"[-] 论文精读请求失败 [{paper['id']}]: {e}")
        return None, 0, 0

def run_paper_pipeline(target_papers=None):
    os.makedirs(PAPER_DIR, exist_ok=True)
    papers = CURATED_PAPERS
    if target_papers:
        papers = [p for p in CURATED_PAPERS if p["id"] in target_papers]

    total = len(papers)
    print(f"[*] 🚀 启动前沿 AI 顶级论文逐行精读引擎 (共 {total} 篇工业界里程碑文献)")
    print(f"[*] 驱动模型: {MODEL_NAME} | 目标目录: {PAPER_DIR}")

    accum_tokens = 0
    catalog_entries = []

    for idx, paper in enumerate(papers, 1):
        print(f"\n[{idx}/{total}] 📖 正在深度精读拆解: [{paper['id']}] {paper['title']} ...")
        content, tokens, elapsed = analyze_paper_with_llm(paper)

        if content:
            accum_tokens += tokens
            out_filename = f"{paper['id']}_deep_guide.md"
            out_path = os.path.join(PAPER_DIR, out_filename)
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(f"# 📘 顶级 AI 论文精读: {paper['title']}\n")
                f.write(f"> 作者: {paper['authors']} ({paper['date']}) | 标签: `{'` `'.join(paper['keywords'])}`\n\n---\n\n")
                f.write(content)

            print(f"    [+] 精读指南已生成: {out_path} (耗时: {elapsed:.1f}s | 消耗 Token: {tokens} | 累计已烧: {accum_tokens})")
            catalog_entries.append((paper, out_filename))
        else:
            print(f"    [-] 精读失败，跳过。")
        time.sleep(2)

    # 汇总生成总目录
    catalog_path = os.path.join(PAPER_DIR, "AI_FRONTIER_PAPERS_CATALOG.md")
    with open(catalog_path, "w", encoding="utf-8") as f:
        f.write("# 📚 前沿 AI 顶级技术报告与论文「逐行精读与工程落地踩坑库」全景索引\n")
        f.write(f"> *生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')} | 精读文献: {len(catalog_entries)} 篇 | 累计消耗 Token: {accum_tokens}*\n\n---\n\n")
        f.write("| 论文标识 | 论文全名 | 作者/机构 | 核心技术关键词 | 精读手册入口 |\n")
        f.write("| :--- | :--- | :---: | :--- | :---: |\n")
        for p, fname in catalog_entries:
            f.write(f"| **`{p['id']}`** | {p['title']} | `{p['authors']}` | `{'` `'.join(p['keywords'][:3])}` | [📖 点击阅读]({fname}) |\n")
        f.write("\n---\n\n### 💡 核心学习方法\n")
        f.write("每篇精读指南均拒绝空谈概念，重点关注**数学推导、真实 CUDA/显存踩坑经验、最小复现代码以及大厂架构考核题**。\n")

    print(f"\n🎉 论文批次精读完毕！全景索引已更新: {catalog_path}")
    print(f"🔥 本次论文库累计消耗 Token: {accum_tokens}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Frontier Papers Deep Diver")
    parser.add_argument("--papers", nargs="+", help="指定论文 ID 列表 (如 deepseek_r1 deepseek_v3)")
    args = parser.parse_args()
    run_paper_pipeline(target_papers=args.papers)
