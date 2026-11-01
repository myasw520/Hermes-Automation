# 📘 顶级 AI 论文精读: DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning
> 作者: DeepSeek-AI (2025-01) | 标签: `GRPO` `Pure RL` `Cold Start` `Distillation` `Aha Moment` `Reward Engineering`

---

# DeepSeek-R1 逐行精读与工程落地踩坑剖析

## ——纯强化学习点燃推理涌现的底层架构深拆

> **阅读对象**：具备分布式训练实战经验、想搞懂 R1 为何能"Pure RL + Cold Start + Distill"三连击打穿 o1 护城河的 Infra/算法工程师。
> **本文风格**：不背摘要，只讲公式怎么推、显存怎么爆、集群怎么死锁。

---

# 1. 核心破局动机与痛点推演

## 1.1 旧范式的三重死亡陷阱

### 陷阱一：过程监督标注的"人力黑洞"

OpenAI 的 o1 路线早期依赖 PRM（Process Reward Model）+ 大量人工 CoT 标注。这在工程上意味着：

- 一条高质量数学 CoT 平均 2k~8k token，人工标注一条成本约 $3~$10；
- 训练一个 671B MoE 的推理能力，所需标注量级在 10⁵~10⁶ 条，人力成本百万美元级；
- 更致命的是 **PRM 的 Reward Hacking**：奖励模型本身是神经网络，策略会系统性地找到 PRM 的判别盲区。文献中 lightbulb reward 的实验证明，用 MCTS 强制的 step-level score 做 RL，策略会学会"复读标签词"刷分。

**底层物理逻辑**：任何基于神经网络的稠密 reward 都是可被梯度攻击的对抗面。Reward 信号越密集、越精细，被 hack 的表面积越大。

### 陷阱二：MCTS + 的搜索树爆炸

试图用 MCTS 生成 CoT 蒸馏的路线（如 rStar、早期 AlphaMath）死在算力上：

- 设每个节点扩展 b=5 个分支，深度 d=10，单条轨迹需要 5¹⁰ ≈ 10⁷ 次 value 评估；
- 每次评估 = 一次 67B 模型前向 ≈ 134GB FLOPs（2×67×10⁹×2k token）；
- 单条轨迹 ≈ 1.3 PFLOPs，生成 10 万条轨迹 = 1.3×10²⁰ FLOPs ≈ 相当于 512 张 H100 跑 3 天（按 1979 TFLOPS·FP16、MFU 40% 算）。

而 R1 证明：**这些轨迹可以被 RL 自主涌现出来**，成本转移为在线 rollout 的 GPU 时，且可复用训练集群的算力，边际成本骤降。

### 陷阱三：传统 PPO + Critic 在 MoE 超大模型上的显存灾难

PPO 需要 Critic 网络（与 Policy 同规模）来估 baseline。对一个 671B MoE（激活 37B）模型做 PPO：

```
单 GPU 显存占用（FP16 + ZeRO-1 估算，以 Policy+Critic+Ref+RM 四模型为例）：

Policy 权重:      671B × 2B = 1342 GB（分片后均摊）
Critic 权重:      同规模 ≈ +1342 GB（哪怕只分片，也翻倍通信量）
Ref Policy:       +1342 GB（RLHF 冻结参考，防 reward hacking）
Optimizer states: AdamW 两个 FP32 动量 + FP32 master weights
                  = 671B × 12B = 8052 GB（分摊）

关键爆点：Critic 前向需要完整激活值
  Critic 激活 ≈ batch × seq × hidden × layers × 常数
  671B 模型 hidden=7168, layers=61，激活值在 32k seq 下
  单卡塞不下任何合理 batch → 必须 TP 切 → TP 通信开销线性放大
```

GRPO 的破局：**用"同 prompt 组内采样的均值"替代 Critic**。baseline 从"学出来的价值函数"退化为"统计量"，省掉整个 Critic 模型（约省 40% 集群显存与通信），这正是 DeepSeek-Math 论文里 GRPO 的原始动机，R1 直接继承。

## 1.2 R1 的颠覆性设计思想：三条物理直觉

**直觉 1：Reward 稀疏 ≠ 信号弱，规则化 reward 是不可 hack 的最小对抗面。**

R1-Zero 的 reward 只有两条规则：
- Accuracy reward：答案对不对（数学用规则验证器，代码用编译器+测试用例）；
- Format reward：`<think>...</think><answer>...</answer>` 格式对不对。

都是**可判定的符号逻辑**，不是神经网络打分。策略无法通过"说漂亮话"骗分，只能通过真正提升推理正确性得分。这就是 Aha Moment 能出现的根因——优化压力全部传导到"推理质量"这一个自由度上。

**直觉 2：探索空间用"温度 + 组采样"打开，而非用先验 SFT 注入。**

Pure RL 的问题是小模型难以自发出长 CoT。R1-Zero 用 base 模型（DeepSeek-V3-Base，本身预训练质量极高）+ 高温度采样，让组内多样本中偶然出现正确长推理，GRPO 的相对优势会放大这些"幸运轨迹"。物理上相当于：以组为单位的 importance sampling，自动把概率质量从短错误链迁移到长正确链。

**直觉 3：蒸馏的知识熵比 RL 自探索的熵低。**

R1 最惊人的结论：对若干 1.5B~70B dense 模型，用 R1 生成的 80 万条 CoT 数据做纯 SFT 蒸馏，效果**优于**同款小模型直接跑大规模 RL。解释：大模型 RL 产出的分布已是"筛选过的高熵→低熵收敛"轨迹，小模型直接模仿这个低熵分布，等价于站在 RL 的终点做 supervised imitation，跳过了自己漫长的探索期；而小模型自己跑 RL，探索信噪比太低（小模型 rollout 正确率太低，GRPO 组内全错时优势全为 0，梯度消失）。

---

# 2. 数学公式与算法底层推导

## 2.1 GRPO 无 Critic 目标函数

GRPO 对每个问题 q 从旧策略 $\pi_{\theta_{old}}$ 采样一组 $G$ 个响应 $\{o_1,...,o_G\}$，组内归一化得到优势：

$$
\hat{A}_{i,t} = \frac{r_i - \text{mean}(\{r_1,\dots,r_G\})}{\text{std}(\{r_1,\dots,r_G\}) + \epsilon}
$$

注意：**组内所有 token 共享同一优势值**（outcome-level credit assignment，R1 不做 step-level），$r_i$ 是第 i 条响应的整体 reward。

策略目标（token 级 clip 目标 + KL 正则）：

$$
\mathcal{J}_{GRPO}(\theta) = \mathbb{E}_{q \sim P(Q),\ \{o_i\} \sim \pi_{\theta_{old}}}\Bigg[\frac{1}{G}\sum_{i=1}^{G}\frac{1}{|o_i|}\sum_{t=1}^{|o_i|}\Big(\min\big(\rho_{i,t}\hat A_{i,t},\ \text{clip}(\rho_{i,t}, 1-\epsilon, 1+\epsilon)\hat A_{i,t}\big) - \beta\, \mathbb{D}_{KL}[\pi_\theta \| \pi_{ref}]\Big)\Bigg]
$$

其中重要性采样比 $\rho_{i,t} = \dfrac{\pi_\theta(o_{i,t}\mid q, o_{i,<t})}{\pi_{\theta_{old}}(o_{i,t}\mid q, o_{i,<t})}$。

**KL 无偏估计器**（这是 GRPO 的精妙工程细节）：

$$
\mathbb{D}_{KL}[\pi_\theta \| \pi_{ref}] = \frac{\pi_{ref}(o_{i,t}|q,o_{i,<t})}{\pi_\theta(o_{i,t}|q,o_{i,<t})} - \log\frac{\pi_{ref}(o_{i,t}|q,o_{i,<t})}{\pi_\theta(o_{i,t}|q,o_{i,<t})} - 1
$$

**逐项拆解与物理直觉**：

| 量 | 维度 | 复杂度 | 物理含义 |
|---|---|---|---|
| $q$ | prompt batch | — | 问题分布，R1-Zero 直接从预训练数据重采 |
| $o_i$ | $\le$ 32k token（R1 训练中逐步拉长） | rollout 是主要算力消耗：G×len 次自回归解码 | 探索样本 |
| $\hat A_{i,t}$ | 标量广播到每个 token | O(G) | 组内相对排名，天然 batch 内 baseline，零参数 |
| $\rho_{i,t}$ | 每 token 标量 | 一次额外前向（旧策略概率缓存） | PPO 式 trust region |
| KL 项 | 每 token 标量 | ref 模型一次前向 | 详见下 |

**KL 估计器为何写成这个奇怪形式**：它是逐 token 无偏的（基于单样本），而经典 $p\log p - p\log q$ 形式需要 $\log\pi_\theta$ 与 $\log\pi_{ref}$ 的两个张量做逐点组合，在序列上偏差大。记 $s = \pi_{ref}/\pi_\theta$，估计器 $s - \log s - 1 \ge 0$ 恒成立（凸函数在 s=1 处取最小值 0），在 s→1 时泰勒展开 ≈ $(s-1)^2/2$，即把 KL 变成一个"概率比偏移量的二次惩罚"——对训练更平滑。

**省 Critic 的显存账**：以 671B MoE 为例，Critic 若同规模，FP16 权重 1.34TB + 激活。GRPO 只需 Policy + Ref（Ref 可用 rollout 时缓存的 logits 近似或分片常驻），集群等效吞吐提升约 1.5~2 倍。

## 2.2 Cold Start SFT 的作用：熵与格式锚定

R1 正式版放弃纯 R1-Zero 路线的原因（工程痛点）：

1. R1-Zero 输出可读性差、中英混杂、`<think>` 内格式混乱；
2. Pure RL 在 base 模型上前期 **entropy 崩塌/震荡**，语言一致性需要额外 reward；
3. 冷启动数据只需数千条（论文：几千条）长 CoT，先 SFT 一轮，把格式和初始推理模式锚定，再 RL 收敛更快更稳。

数学上：SFT 提供了低熵初始分布 $\pi_0$，RL 的探索半径 $\epsilon$（clip 范围）固定时，从低熵合理分布出发，策略更新落回"高质量区域"的概率更高。等价于把 RL 的有效信噪比从 $\frac{\text{reward方差}}{\text{轨迹方差}}$ 提升了一个量级。

## 2.3 蒸馏 > 小模型 RL 的概率论解释

设小模型 rollout 单题正确率为 p。GRPO 组内全对或全错时优势为 0（std=0 或组内无区分度），有效梯度信号 ∝ 组内方差。对 p<0.1 的难题（数学竞赛级别），G=16 的组内期望正确数 1.6，出现"组内有对有错"的区分性样本概率随 p 指数衰减——小模型 RL 的有效 batch 塌缩。

蒸馏路线则是：直接对 R1 生成的、已验证正确的轨迹 $D=\{(q, o^*)\}$ 做极大似然：

$$
\mathcal{L}_{distill} = -\mathbb{E}_{(q,o^*)\sim D}\sum_t \log \pi_\theta(o_t^* \mid q, o_{<t}^*)
$$

每条轨迹都携带满梯度信号，无探索浪费。**80 万条（DeepSeek 官方公开 R1 蒸馏集：~800k）轨迹的监督密度，远超小模型自身能采到的有效 RL 信号**。这就是"蒸馏比 RL 便宜且好"的数学本质。

---

# 3. 工业界真实落地工程踩坑避雷指南

> 以下均为复现 R1 类 RL 训练时高频翻车点，来自真实集群经验。

## 3.1 显存坑：Rollout 与训练的显存撕裂

**坑 A：vLLM/SGLang rollout 与 FSDP 训练进程的显存共存。**

R1 类训练标准架构是：Actor（FSDP/Megatron）+ vLLM rollout engine + Ref + （可选）RM 同节点共存。vLLM 的 PagedAttention 默认 `gpu_memory_utilization=0.9`，会把剩余显存吃光 → Actor 权重 offload 回来时 OOM。

**避雷**：
- rollout 后必须 `torch.cuda.empty_cache()` + vLLM `sleep(level=1)`（释放 KV cache 权重）；
- 实测：32k seq、G=16 组、micro-batch 1 时，logits 张量 `[1, 32768, vocab≈129k]` FP32 = **16.9 GB 单条**！这是 RLHF 训练最大的隐形显存杀手。

**避雷**：绝对不要物化全 vocab logits 做 loss。必须用 chunked cross-entropy / fused linear+CE（如 Liger Kernel / Cut Cross Entropy），逐 chunk 计算 log-prob，把 logits 显存从 O(seq×vocab) 降到 O(chunk×vocab)。

**坑 B：PyTorch 显存碎片化。**

RL 训练中序列长度剧烈波动（短 response 200 token、长 response 30k token），PyTorch caching allocator 会出现大量小于 2MB 的碎片块，`nvidia-smi` 显示显存被占但实际不可用。长序列 batch 进来时 OOM，但重跑又能过。

**避雷**：
- `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`（H100/A100 均可用），碎片率可从 15%+ 降到 <2%；
- 按 sequence length 做 bucketing + length-grouped batching，避免长短混 batch。

**坑 C：Bank Conflicts 与对齐。**

自研 fused kernel（如 GRPO 的 advantage 广播、KL 计算）时，若按 token 维度连续写 advantage 而线程按 32 lane 读 stride=1，无冲突；但若按 `[G, seq]` 转置访问，stride=seq_len 非 2 的幂时发生 bank conflict，吞吐掉 8~32 倍。避雷：padding seq 维到 16 的倍数，或用 `__ldg`/shared memory swizzle。

## 3.2 分布式通信坑

**坑 A：All-to-All 死锁（MoE + EP）。**

671B MoE 用 EP（Expert Parallel）时，dispatch/combine 的 All-to-All 若与 TP 的 AllReduce 交叠，且不同 rank 的 micro-batch 数不一致（RL rollout 长度不均导致 DP rank 间 batch 数不同），NCCL 会在缺少对端 op 时挂死。

**避雷**：强制所有 DP rank pad 到相同 micro-batch 数（用 dummy batch 参与前向但 loss 置 0）；NCCL 设置 `NCCL_ASYNC_ERROR_HANDLING=1` + watchdog timeout，避免永久挂死浪费整夜集群。

**坑 B：Pipeline Bubble × RL 长尾。**

RL 的 response 长度方差远大于 SFT。PP 划分下，长尾 sample 让某个 DP 副本晚 finish，pipeline bubble 从理论 15% 恶化到 40%+。

**避雷**：RL 场景下优先用纯 DP+TP+EP（ZeRO 风格），慎用 PP；若必须 PP，用 1F1B + 动态按长度重排 micro-batch（最长的先发，降低 straggler）。

**坑 C：Rollout→Train 权重同步的隐形 PCIe 瓶颈。**

Colocate 架构下每步 RL 要把更新后的权重灌回 vLLM。671B FP16 = 1.34TB，走 NVLink 约 900GB/s 也要 1.5s，但很多人配置走了 PCIe host 中转（先 CPU 再 GPU），掉到 25GB/s → **单次同步 54 秒**，一步训练 40% 时间在搬权重。

**避雷**：用 `CUDA IPC` 直接 GPU-GPU 拷贝（vLLM 0.6+ 的 collective rpc / DeepSeek 3FS 类方案），或把 rollout 引擎与 trainer 做在同一 NVLink 域。

## 3.3 数值精度坑

**坑 A：FP16 下 long-CoT log-prob 下溢。**

30k token response 的序列 log-prob 求和，FP16 累加在 -65504 边界必然溢出；且 `exp(advantage)` 在 advantage 大时上溢。

**避雷**：一切 log-prob 用 FP32 累加；ratio 用 log-domain 计算 `exp(logp_new - logp_old)`，且对 `logp_old` 做 stop-gradient 前先 clamp（参考 verl 的实现：`logits.clamp(-20, 20)` 前置）。

**坑 B：BF14/BF16 训练中 KL 项的数值噪声。**

KL 估计器 $s - \log s - 1$ 在 $s \approx 1$ 时是两个大数相减（catastrophic cancellation），BF16 只有 8 位尾数，噪声会淹没有效 KL 梯度 → 策略漂移出 ref 分布而 KL 监控显示为 0。

**避雷**：KL 项计算强制 FP32，或直接用 `log(s)` 形式（torch.log 保持相对精度）。

**坑 C：GRPO advantage 归一化的除零/极端值。**

组内 reward 全相同时 std≈0，归一化后 advantage 爆炸。必须 `std + 1e-6` 防护，且实践上加 clip（如 `adv.clamp(-10, 10)`）；另外 mask 掉 padding token 后再算 mean/std，否则组间长度差会污染统计量。

## 3.4 动态调度与吞吐崩塌坑

**坑 A：reward 是"长序列偏好"的隐式 hack。**

只按 accuracy 给 reward 时，RL 早期会发现"把答案猜对的多采样几次比认真推理更划算"——length 开始失控增长（R1-Zero 论文图里 response 长度自发暴涨也部分源于此：更长的思考链更容易在末尾自我纠正）。不是一直好：训练后期可能出现**无限复读**。

**避雷**：R1 的语言一致性 reward + 长度惩罚（如过 32k 直接 0 分）、KL 锚定、以及 reward 里去掉任何与长度正相关的项。

**坑 B：验证器本身成为瓶颈。**

数学 rule-based verifier（比如 sympy 等价性判断）单题可耗时秒级，rollout 吞吐 10k samples/步时 verifier 队列堵塞整个 pipeline。

**避雷**：verifier 做成异步分布式服务（Ray actor pool），与下一轮 rollout 流水重叠。

**坑 C：蒸馕数据的灾难性遗忘。**

R1 蒸馏 800k CoT 直接 SFT 小模型，若混入比例不当（纯 CoT 100%），小模型的通用能力（问答、写作）崩掉。官方做法是 SFT 多阶段多轮 + 通用数据混合；自己复现时通用：CoT 数据混 20~40% 通用 instruction 数据。

---

# 4. 极简极客源码复现：纯 PyTorch 手写 GRPO 核心

以下 ~90 行代码完整实现 GRPO 的优势计算、KL 估计、clip 目标与最小训练循环（`pip install transformers torch` 即可跑一个小 GPT-2 上的 demo 概念验证）：

```python
import torch, torch.nn.functional as F

def grpo_advantages(rewards: torch.Tensor, eps: float = 1e-6) -> torch.Tensor:
    """组相对优势计算。rewards: [G] 每条响应的整体标量 reward。
    核心思想：用组内均值当 baseline（替代 Critic 网络），std 归一化稳定梯度尺度。
    物理直觉：一条响应的优势 = 它在'同题组内'的相对排名 z-score。"""
    mean = rewards.mean()                          # 组内均值，即零参数 baseline
    std = rewards.std() + eps                      # 防除零（组内全对/全错时 std≈0）
    adv = (rewards - mean) / std                   # [G]，outcome-level，组内 token 共享
    return adv.clamp(-10.0, 10.0)                  # 实战坑：极端 advantage 会让 exp 上溢

def grpo_token_logprobs(model, prompts_ids, resp_ids):
    """计算 log pi(resp | prompt) 的逐 token 对数概率。
    关键工程点：拼接 prompt+response 一次前向，响应部分 shifted 取值；
    绝不物化全 [B, seq, vocab] logits —— 真实训练必须用 chunked cross-entropy。"""
    input_ids = torch.cat([prompts_ids, resp_ids], dim=1)          # [B, P+R]
    out = model(input_ids).logits                                   # [B, P+R, V]
    # 响应 token t 的预测 logits 位于位置 t-1（自回归 shift）
    logits = out[:, prompts_ids.size(1)-1:-1, :]                    # [B, R, V]
    logp_all = F.log_softmax(logits.float(), dim=-1)                # FP32 防 long-CoT 下溢
    token_logp = logp_all.gather(-1, resp_ids.unsqueeze(-1)).squeeze(-1)  # [B, R]
    return token_logp                                               # [B, R]

def k3_kl_estimator(logp_theta, logp_ref):
    """GRPO 的逐 token 无偏 KL 估计器: s - log s - 1, s = exp(logp_ref - logp_theta)。
    恒 >=0，s≈1 时退化为二次惩罚，比传统 KL 公式更平滑且只需两个 logp 张量。"""
    log_ratio = logp_ref - logp_theta               # log s，用 log 域保相对精度
    return torch.exp(log_ratio) - log_ratio - 1.0   # [B, R]，恒非负

def grpo_loss(policy_logp, ref_logp, old_logp, adv, resp_mask,
              clip_eps=0.2, kl_beta=0.04):
    """GRPO 目标函数（负号转 loss）。所有输入: [B, R]。
    policy_logp 不带梯度缓存 old_logp：PPO 式 trust region，
    允许一次 rollout 做多轮 minibatch 更新而不崩。"""
    ratio = torch.exp(policy_logp - old_logp)                       # 重要性采样比 ρ
    adv_b = adv.unsqueeze(1)                                        # [G]->[B,1] 广播到每 token
    surr = ratio * adv_b                                            # 未裁剪的代理目标
    clipped = torch.clamp(ratio, 1-clip_eps, 1+clip_eps) * adv_b    # trust region 裁剪
    pg = -torch.min(surr, clipped)                                  # 取悲观侧（PPO 核心）
    kl = k3_kl_estimator(policy_logp, ref_logp)                     # 防策略漂移远离 ref
    loss = (pg + kl_beta * kl) * resp_mask                          # mask 掉 padding
    return loss.sum() / resp_mask.sum().clamp(min=1)                # token 级归一化

# ---------------- 最小训练循环示意 ----------------
def grpo_step(model, ref_model, tokenizer, questions, rewards_fn,
              G=8, lr=1e-6, max_new_tokens=256):
    opt = torch.optim.AdamW(model.parameters(), lr=lr)
    model.eval()  # rollout 阶段关 dropout
    with torch.no_grad():
        # 1) 组采样：每个问题重复 G 次，高温探索
        reps = []
        for q in questions:
            ids = tokenizer(q, return_tensors="pt").input_ids.cuda()
            for _ in range(G):
                out = model.generate(ids, max_new_tokens=max_new_tokens,
                                     temperature=1.0, do_sample=True)
                reps.append((ids, out[:, ids.size(1):]))            # (prompt, response)
        # 2) 规则化 reward：不可被 hack 的符号验证（真实场景=答案校验/编译测试）
        rewards = torch.tensor([rewards_fn(tok.decode(r)) for _, r in reps],
                               device="cuda")
        # 3) 组内相对优势
        adv = grpo_advantages(rewards.view(-1, G)).view(-1)         # 按组归一化
        # 4) 缓存 old/ref 的 logp（一次前向，之后复用）
        P = torch.cat([grpo_token_logprobs(model, p, r) for p, r in reps])
        R_ = torch.cat([grpo_token_logprobs(ref_model, p, r) for p, r in reps])
        old, ref, mask = P.detach(), R_, (P != 0).float()
    # 5) 策略更新（此处 1 个 minibatch，真实场景切多个迭代复用同一批 rollout）
    model.train()
    new_logp = torch.cat([grpo_token_logprobs(model, p, r) for p, r in reps])
    loss = grpo_loss(new_logp, ref, old, adv, mask)
    loss.backward(); torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
    opt.step(); opt.zero_grad()
    return {"loss": loss.item(), "mean_reward": rewards.mean().item(),
            "mean_len": float(mask.sum() / mask.size(0))}  # 监控 response 长度漂移
```

**代码对应的论文映射**：`grpo_advantages` = 论文 Eq.(3)（去掉 Critic 的组归一化）；`k3_kl_estimator` = 论文 Eq.(4) 的无偏 KL；`grpo_loss` = Eq.(1)+(2) 的 clip 目标；`rewards_fn` = R1-Zero 的 rule-based reward（format + accuracy）。

---

# 5. 顶尖大厂技术评审必问考核题

### Q1：GRPO 去掉 Critic 后，outcome-level 的优势让每个 token 共享同一个 reward，为什么不会因 credit assignment 粗糙而学不动？什么时候会崩，怎么补？

**满分答案要点**：
- 语言模型的生成过程可视为以序列级 reward 为叶节点的随机过程；对 token 级参数的梯度 $\nabla\log\pi(o_t)\cdot\hat A$ 中，$\hat A$ 是常数不改变梯度方向，只改步长——真正的 credit assignment 由 $\log\pi(o_t|o_{<t})$ 对每个 token 的条件概率差异隐式完成：错误 token 出现概率被压低，等价于隐式的 token 级信号。
- 崩溃场景：①组内 reward 无区分度（全对/全错，std≈0），长尾难题上梯度消失——这正是小模型 RL 弱于蒸馏的原因；②超长序列中单个错误 token 被 $1/|o|$ 平均稀释——可用早期 RC（约 100k step 后才加）的语言/格式 reward、或结合 step-level 信号（如 DAPO/PRIME 类改进）补。
- 追问延伸：与 RLOO（REINFORCE leave-one-out）对比——GRPO 用组均值做 baseline 是有偏的（自身包含在均值中），RLOO 用 leave-one-out 无偏但方差略高；G 大时两者趋同。

### Q2：RL 训练中 rollout（推理）和 training（训练）是两类完全不同的负载，如果你来设计 512 卡的 R1 训练系统，怎么编排这两类负载的算力、显存和通信？

**满分答案要点**：
- **两种架构**：①Colocate（同卡复用，DeepSeek/verl 主流）：每卡既跑 trainer 又跑 vLLM，通过 sleep/wake 释放显存、CUDA IPC 零拷贝传权重，省卡但显存紧张、有同步开销；②Disaggregated（分离）：rollout 集群与训练集群物理分开，通过参数服务器/3FS 类高速存储同步权重，吞吐高但 671B 模型权重同步代价大。
- 负载画像差异：rollout 是 memory-bandwidth-bound 自回归解码（batch 大、低 MFU、32k 长 KV cache），训练是 compute-bound（高 MFU、大 TP/EP 通信）。Colocate 架构下时间线 = rollout → (ref/reward 前向) → 权重同步 → train → 循环；要用 Ray 编排各阶段 GPU 角色切换。
- 关键数字：显示懂比例——512 卡 H800 跑 671B RL，rollout 占比通常 40~60%，优化重心在 vLLM 并发调度（partial rollout、动态 batch）与权重同步零拷贝；通信坑在 EP All-to-All 与 NCCL 通信组在两种角色间的重建（必须显式 destroy/重建 process group，否则 rank 状态残留导致死锁）。

### Q3：R1 论文说"蒸馏比小模型直接 RL 更有效"，这句话的边界条件是什么？如果给你一个 7B 模型和无限算力，你还会选蒸馏吗？

**满分答案要点**：
- 边界条件：①蒸馏上限被 teacher 分布封顶——7B 永远无法超越 R1 的推理范式边界；②需要 teacher 高质量数据可获取（R1 恰好 RL 后分布收敛、轨迹正确率极高，蒸馏信号纯净）；③小模型 RL 有效的前提是 base 模型 rollout 正确率不能太低（探索信号存在），DeepSeek 用 R1-Zero 证明 ≥某个能力阈值（V3-Base 级别）时 Pure RL 可行，1.5B 直接 RL 效果差。
- 无限算力下的选择：**混合策略**——先蒸馏冷启动（拿到低熵高起点），再用 RL 突破 teacher 上限（self-improvement 只在 RL 阶段发生，蒸馏无法产生超出 teacher 的新能力）。这恰好也是 R1 官方技术路线：小模型 R1-Distill 后，社区和 DeepSeek 后续工作证明蒸馏模型再跑 RL 仍有增益。
- 加分项：指出该结论对算力分布不均的世界有战略意义——蒸馏让开源小模型生态在一天内获得 o1 级数学能力（R1-Distill-Qwen-7B 在 AIME 上超过 GPT-4o），这是算法民主化的关键论据。

---

## 总结：R1 的三层遗产

1. **算法层**：GRPO + 规则 reward 证明"可验证领域的推理能力可以用 RL 规模化激发"，Reward Engineering 从"学一个 reward model"退回"写一段验证代码"，对抗面最小化。
2. **系统层**：rollout/train 混合编排成为新一代训练 Infra 的标配形态（verl、OpenRLHF、slime 均由此定型），倒逼 vLLM/SGLang 与 Megatron 的深度协同。
3. **生态层**：蒸馏结论重新定义了大小模型分工——大模型负责 RL 探索前沿，小模型负责蒸馏承接落地，"R1 时刻"之后推理能力的扩散速度以天为单位计算。