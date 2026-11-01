# 🧭 全球顶级 AI 硬核工程与极客学习导航全景库
> 整理给个人深度学习与进阶：拒绝快餐营销号与公关稿，只收录真正有代码、有数学推导、有系统工程架构的权威与宝藏源。

---

## 一、🔥 顶级权威实验室与一手技术博客（看技术范式迁移）

| 平台 / 实验室 | 核心看点与推荐理由 | 直达链接 |
| :--- | :--- | :--- |
| **Anthropic Research & Engineering** | **全球 Agent 与模型对齐天花板**。他们提出的 MCP（Model Context Protocol）、Prompt Caching 以及智能体长循环机制，是现代 Agent 开发者必读的教科书。 | [anthropic.com/research](https://www.anthropic.com/research) |
| **OpenAI Research & Cookbook** | 官方 Cookbook 包含全球最标准的 Function Calling、结构化输出（Structured Outputs）、复杂检索 RAG 与微调范例，每一行代码都可直接抄作业。 | [cookbook.openai.com](https://cookbook.openai.com/) |
| **Hugging Face Blog** | **开源大模型工程落地第一站**。量化技术（GGUF/AWQ/BitsAndBytes）、vLLM 高并发推理、LoRA/DPO 微调、合成数据管道最详尽的实战保姆级教程。 | [huggingface.co/blog](https://huggingface.co/blog) |
| **Google DeepMind Research** | 多模态底层架构（Gemini）、科学大模型（AlphaFold/AlphaGenome）以及下一代神经符号推理的源头。 | [deepmind.google/research](https://deepmind.google/research/) |

---

## 二、🎬 封神级视频课程与硬核技术博主（看源码与数学本质）

| 讲师 / 频道 | 必看代表作 | 为什么封神？ |
| :--- | :--- | :--- |
| **Andrej Karpathy** (原 OpenAI 创始成员/Tesla AI总监) | • 《Neural Networks: Zero to Hero》<br>• 《Let's build GPT: from scratch, in code》<br>• 《Intro to Large Language Models》 | **全球无出其右的 AI 第一名师**。从纯 Python 和 C 开始，不调任何黑盒库，一行一行手写反向传播、手搓 Transformer 和 Tokenizer，看完彻底破除对大模型的恐惧。 |
| **3Blue1Brown (Grant Sanderson)** | • 《深度学习的本质》系列（4P）<br>• 《注意力机制与 Transformer 可视化》 | 把极其抽象的矩阵乘法、注意力权重、高维特征空间，用数学动画演绎到纳米级，直觉理解的绝对天花板。 |
| **跟李沐学AI (Mu Li)** | • 顶会经典论文逐篇精读系列（Transformer, BERT, GPT, ResNet）<br>• 《动手学深度学习》(Dive into Deep Learning) | 斯坦福/CMU 级别的内容，纯中文逐字拆解经典论文的写作背景、作者意图与代码实现。 |
| **Yannic Kilcher** | • 机器学习最新前沿顶会论文逐篇技术拆解 | 语速飞快、直捣黄龙，专挑前沿冷门突破论文进行硬核架构剖析与优缺点锐评。 |

---

## 三、💎 冷门宝藏高潜独立工程师个人博客（最接地气的工程实战）

很多大厂公关稿都是报喜不报忧，真正踩坑、踩碎了牙往肚子里咽的工程经验，全在这些顶级独立工程师的个人博客里：

| 独立博主 | 博客亮点与必读篇目 | 博客地址 |
| :--- | :--- | :--- |
| **Lilian Weng** (翁丽莲，原 OpenAI 安全系统总监) | **《LLM Powered Autonomous Agents》** 被全球奉为现代智能体架构的“圣经”；她的博客每一篇都结构严谨，把复杂算法的前世今生梳理得清清楚楚。 | [lilianweng.github.io](https://lilianweng.github.io/) |
| **Simon Willison** (Datasette 作者，LLM 实用先锋) | 专攻日常工作中如何用 LLM 提高 10 倍生产力、提示词注入防护（Prompt Injection）、个人微工具构建。更新极勤快，全是干货代码。 | [simonwillison.net](https://simonwillison.net/) |
| **Chip Huyen** (原 Stanford 讲师，实战 AI 系统专家) | **《Building LLM applications for production》** 生产级大模型系统设计、评测指标、延迟与成本优化的天花板级分析。 | [huyenchip.com](https://huyenchip.com/) |
| **Sebastian Raschka** (Ahead of AI 创办人) | 专精“模型架构演化与微调”。每一期 Newsletter 都用详尽的图表对比不同模型（如 LLaMA vs Qwen vs DeepSeek）的注意力层与架构微调差异。 | [magazine.sebastianraschka.com](https://magazine.sebastianraschka.com/) |
| **Eugene Yan** (Amazon 应用科学家) | 深度总结大模型落地中的设计模式：何时用 Agent、何时用 Router、RAG 的 10 种失败模式与解法。 | [eugeneyan.com](https://eugeneyan.com/) |

---

## 四、🛠️ 必刷的开源硬核“极简实战练习靶场”（自己手敲一遍胜读十年书）

如果你想真正掌握大模型底层，别去装那些几万行的重型框架，去克隆这几个 **只有几百行代码却五脏俱全** 的神级极简仓库：

1. **`karpathy/nanoGPT`**：最简单、最快训练和精调 GPT 的单文件 Python 代码，无任何多余抽象；
2. **`karpathy/minbpe`**：从零用纯 Python 实现 GPT-4 的 BPE Tokenizer 分词算法；
3. **`modelcontextprotocol/servers`**：Anthropic 官方开源的 MCP 服务器范例库（看看别人是怎么让 Claude 和大模型直接操作 SQLite、Git、浏览器的）；
4. **`tinygrad/tinygrad`**：George Hotz（comma.ai 创始人）开发的极简深度学习框架，代码精简到令人发指，是学习硬件加速与张量计算的核心宝库。
