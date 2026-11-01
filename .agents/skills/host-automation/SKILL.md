---
name: host-automation
description: "Control host automation tasks: trigger wool radar, key harvester, check status, and query keys pool."
version: 1.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [host-automation, wool-radar, keys-pool, harvester, scheduler, xhh-gems-hunter]
    category: autonomous-ai-agents
    related_skills: [infra-giveaway-triage]
---

# Host Automation & Wool Harvester Controller

This skill enables Hermes Agent to interact with the host Windows automation daemon running on `http://host.docker.internal:28987` (from inside the Hermes Docker container) or `http://127.0.0.1:28987` (from the Windows host itself), or via local Python scripts.

> **Auth**: `/keys` and `/data` are sensitive endpoints — append `?token=<API_ACCESS_TOKEN>` (value stored in the project-root `.env`). `/status`, `/tasks`, `/logs`, `/trigger` require no token.

## When to Use

Use this skill whenever the user asks to:
- Check current automation scheduler status or task countdowns ("查看调度状态", "任务计划跑得怎么样", "下次什么时候巡检")
- Query available/healthy free API keys ("查看Key池", "有哪些可用Key", "给我一个免费Key")
- Trigger an on-demand wool scan ("跑一下羊毛雷达", "立即巡检羊毛", "扫一下免费API")
- Trigger key harvester & health test ("测试Key活态", "收割公益Key", "测一下中转站")
- Check recent automation execution logs ("查看调度日志", "最近跑了什么任务")
- Trigger game freebies or Bilibili tech digest ("查一下游戏喜加一", "B站技术速递")
- Trigger postgrad past exam papers & solution bank ("抓取考研真题", "更新408数二英二真题库", "整理考研真题")
- Trigger Xiaoheihe niche gems scout ("挖掘小黑盒低星神器", "搜集冷门开源工具", "抓取实操UI截图")

## API Endpoints

- From the Hermes Docker container: `http://host.docker.internal:28987`
- From the Windows host: `http://127.0.0.1:28987`

All commands can be executed using `curl` inside the terminal.

### 1. View Scheduler Status & Next Runs
```bash
curl -s http://host.docker.internal:28987/status   # host: use 127.0.0.1 instead
```
Returns JSON containing uptime and each task's interval, last run time, and remaining seconds until next trigger.

### 2. Query Live API Keys Pool
```bash
TOKEN=$(grep "^API_ACCESS_TOKEN=" /path/to/Hermes-Automation/.env | cut -d= -f2)
curl -s "http://host.docker.internal:28987/keys?token=$TOKEN"
```
Returns verified living API keys, model lists, latency, and endpoints. Hermes can use these keys directly or present them to the user.

### 3. Trigger Tasks On Demand
Tasks can be triggered asynchronously (returns immediately) or synchronously (waits for completion with `sync=1`).

- **Wool Radar Scan (全网羊毛巡检)**:
  `curl -s "http://host.docker.internal:28987/trigger?task=wool_radar&sync=1"`
- **Welfare Key Harvester & Health Check (公益Key收割与测活)**:
  `curl -s "http://host.docker.internal:28987/trigger?task=welfare_harvester&sync=1"`
- **Free Games Giveaway (游戏喜加一)**:
  `curl -s "http://host.docker.internal:28987/trigger?task=freegames&sync=1"`
- **Bilibili Tech Digest (B站硬核技术速递)**:
  `curl -s "http://host.docker.internal:28987/trigger?task=bili_intel&sync=1"`
- **GitHub Weekly AI Digest (GitHub 高星周报)**:
  `curl -s "http://host.docker.internal:28987/trigger?task=weekly_github&sync=1"`
- **Postgraduate Exam Papers & Solutions (计算机专硕 408+数二+英二 真题题库)**:
  `curl -s "http://host.docker.internal:28987/trigger?task=postgrad_papers&sync=1"`
- **Build Desktop Print-Ready Exam Papers (一键生成桌面打印店专用全套试卷)**:
  `curl -s "http://host.docker.internal:28987/trigger?task=build_print_papers&sync=1"`
- **Xiaoheihe Niche Gems Scout (小黑盒低星神器挖掘 + 多模态AI视觉质检与智能题注)**:
  ```bash
  # 运行全自动低星神器挖掘（自动经过多模态视觉模型审查）
  python tools/niche_gem_harvester.py
  # 对指定图片资产目录进行多模态 AI 审片与题注直出（自动淘汰 Logo、Banner、二维码）
  python tools/vision_auditor.py <target_directory>
  ```

### 4. View Recent Scheduler Logs
```bash
curl -s "http://host.docker.internal:28987/logs?n=30"
```

### 5. Access Host Data Directory & Raw Files
Hermes can read all underlying dataset files directly (sensitive — requires token):
```bash
# List all files in data directory
TOKEN=$(grep "^API_ACCESS_TOKEN=" /path/to/Hermes-Automation/.env | cut -d= -f2)
curl -s "http://host.docker.internal:28987/data?token=$TOKEN"
```

## Presentation Rules
- Always reply to the user in Simplified Chinese (简体中文).
- When reporting Key pool status, display base URL, supported models, and whether it is alive.
- Mask sensitive parts of the API keys (e.g. `sk-abcd...wxyz`) unless the user explicitly asks for the full key.
