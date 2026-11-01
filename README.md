# 🦙 Hermes-Automation 智能羊毛与全自动资源猎手

本项目为面向 7x24 小时无人值守场景的 AI 资产自动化寻猎与注册系统。

---

## 🏛️ 架构分工（Antigravity 与 Hermes 的职责定位）

| 角色 | 扮演实体 | 核心职责 |
| :--- | :--- | :--- |
| **总架构师 & 逆向攻坚** | **Antigravity (本助手)** | 负责攻破疑难反爬、复杂逆向分析（如 4 帧动态 GIF 验证码融合破译、底层 hosts/DNS 网络链路排查、OAuth 跨域授权穿透），并将突破成功的复杂业务逻辑封装固化为确定性 Python 工具与 Skill。 |
| **24/7 巡检劳工** | **Hermes Agent (Docker 本地服务)** | 部署在本地 Docker (`:8642`/`:9119`)，挂载本地 Python 工具链。在后台定时执行已固化的巡检任务（如扫描 RSS、一键注册、批量测试 Key 连通性），并通过 Telegram 机器人汇报战果。 |

---

## 🚀 核心固化模块列表

### 1. 真实公网中转站全自动注册与提 Key
* **[tools/chatanywhere_harvester.py](tools/chatanywhere_harvester.py)**:
  * **GIF 多帧融合算法 (`ImageChops.darker`)**：突破专门致盲静态截图 OCR 的 4 帧动态透明字符隐藏机制；
  * **本地 `ddddocr` 卷积神经网络**：离线 5ms 极速推理，无外部 API 依赖与超时风险；
  * **QQ 邮箱 IMAP 监听器**：自动剔除 HTML 模板中的 Tailwind CSS 颜色代码等假验证码，秒级回填 6 位真实验证码；
  * **GitHub OAuth 自动授权**：打通跨域授权流，一键解锁官方 50,000 Token 免费配额；
  * **已实测验证 Key**：已入库 `config/keys_pool.json` 并在 Telegram Topic 3 播报（Key 值不入文档，凭证统一存 `.env`）。

### 2. 羊毛雷达巡检系统
* **[services/wool_radar.py](services/wool_radar.py)**: 7x24 小时多源情报雷达，集成大模型反诈过滤与 Telegram 多话题推送。
* **[services/mail_receiver.py](services/mail_receiver.py)**: 极速 IMAP 协议接码器（支持 QQ 邮箱与 Gmail 时间基准过滤）。
* **[tools/oneapi_harvester.py](tools/oneapi_harvester.py)**: 通用 One API / New API 标准中转站模版自动注册与 Token 抽取脚本。

### 3. 系统避坑规范与 Skill
* **[skills/windows-batch-powershell](.agents/skills/windows-batch-powershell/SKILL.md)**:
  * 彻底解决 Windows `cmd.exe` 默认 CP936 (GBK) 与 UTF-8 冲突导致的批处理乱码及命令截断问题；
  * 规范“PowerShell 负责业务与 UAC 提权，.bat 仅做纯 ASCII 极简转发”的黄金原则。

---

## 📁 凭证与资产池
* **凭证配置**：项目根 `.env`（唯一事实来源，经 `services/config_lib.py` 加载；`config/credentials.json` 为历史遗留，不再被代码引用）
* **有效 Key 资产池**：`config/keys_pool.json`
* **Telegram 推送**：群组 `-1004415041729` (话题 3: 羊毛情报 / 话题 4: GitHub 高星 / 话题 5: 交互)
