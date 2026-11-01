# 文档索引（00-index.md）

> 生成日期：2026-10-31（同日第二次刷新，覆盖上午版）｜ 性质：docs/ 目录导航 + 文档时点标注 + 跨文档矛盾/过期点清单
> 维护约定：新增文档时在本表加一行；文档内容过期时优先回改原文档，并在 §3 标注。
> 证据基线：git log（11 个提交，`a052903…0059d15`）、daemon 源码实读、文件系统实测（tools/ 与 _archive/ 计数、post-xiaoheihe/.venv、schtasks 查询 HermesWatchdog）、SECRET-HANDLING §0 实读，均为 2026-10-31 当日核实。

---

## 1. 阅读顺序与导航

| 文档 | 用途（一行） | 什么时候读 | 时点 / 状态 |
|---|---|---|---|
| `README.md`（项目根） | 项目入口：定位、架构分工、核心模块、凭证位置 | 第一次接触本项目时 | **仍结构性过期**：密钥段与 skills 路径已在 `7ae7dda` 修正，但全文仍未提 `daemon_scheduler.py` 这一真正核心（今日 grep 实测 0 命中），架构分工仍按已退役的 Docker 架构描述 → 详见 §3 第 5 条 |
| `docs/ARCHITECTURE.md` | 架构现状盘点：组件清单、数据流 mermaid 图、daemon 任务全表、skill 失配核对、P0-P3 风险清单 | 要理解"系统长什么样、风险在哪"时 | **修复前快照，过期面扩大**（2026-10-31 01:46 落盘）：其 P0"密钥硬编码 / README 明文 Key"已修复；"0.0.0.0 无鉴权"已被 SECRET-HANDLING §0 定性为 Tailscale 内网特性；"无 git / 无 requirements"早已过时；任务表仍写 9 个（现 10 个）→ 读时须按 §3 逐条换算，不可直接引用 |
| `docs/AUDIT-tools-cleanup.md` | tools/ 259 脚本全量审计：调度/skill 依赖清单、A/B/C 三级处置分级 | 找"某个脚本干嘛的 / 被删还是归档了"时 | **已从"待执行计划"变为"已执行完毕的账目"**（`b71fdd3`）：今日实测 tools/ 259→38 个 .py + 5 个 .ps1；B 级归档至 `_archive/tools/`（59 .py + 2 .ps1）与 `_archive/root/`（12 项）。原文的"建议处置"列现应读作"实际处置记录" |
| `docs/GAP-AND-ROADMAP.md` | 缺口评估与路线图：能力地图、G1-G8 缺口、建议新增/明确不加清单、Top3 行动路径 | 决定"下一步做什么/不做什么"时 | **Top1/Top3 大部分已执行**：install.bat+venv、content_inventory（S2）、内容流水线 SOP skill（§3.1）、外部看门狗（S1/G3）、requirements 均已落地（见 §2 第二轮）；头注"G5 依赖清单空白"仍过期（`ae1ae6a` 已含 requirements）。当前真实遗留只剩"内容线真正发一篇帖"这一人工环节 |
| `docs/SECRET-HANDLING.md` | 密钥处置与安全姿态：§0 用户已拍板决策 + 泄露现状表 +（已取消的）轮换/清洗手册 | 评估安全边界时；或**未来要推公网远程前**（必读） | **本地文件，有意不入库**（`.gitignore` L23，`e557ebd`；内容含旧明文值，仅存本机）。§0（`f7084d4`）已拍板：Tailscale 内网私有（本机 zzx-1 100.127.21.69 ↔ 网关机 zzx 100.114.18.45），密钥不轮换、git 历史不清洗；原 §1/§2 保留作"若公开仓库时的执行手册" |
| `docs/PROGRESS.md` | 阶段进度记录：第一轮（安全治理+缺口评估，§1-5）、第二轮（路线图执行，§6） | 想知道"实际做了什么、验证过什么"时 | **并行刷新中（另一会话正在更新，以更新后版本为准）**：本索引撰写时其头注已呈"两轮阶段记录"结构，第一轮旧结论以"→ 第二轮"箭头标注实际结局，当前真实遗留以 §6.3 为准 |

建议阅读顺序：`README.md`（入口，注意 §3 第 5 条）→ `ARCHITECTURE.md`（对照 §3 换算修复状态）→ `GAP-AND-ROADMAP.md`（对照 §2 第二轮看剩余项）→ `AUDIT-tools-cleanup.md`（当账目读）→ `SECRET-HANDLING.md` §0（安全姿态）→ `PROGRESS.md`（以刷新后为准）。

---

## 2. 文档时点分层（理解表面矛盾的关键）

评估/记录文档写于同一天的**两轮阶段**，矛盾多为时间线造成：

**第一轮：安全治理 + 缺口评估（凌晨—午后）**

1. **修复前快照**（01:35-01:46）：`AUDIT-tools-cleanup.md`、`ARCHITECTURE.md` —— git init 之前，"无版本控制/无鉴权/密钥硬编码"均属实。
2. **修复中**（12:46 前后）：`GAP-AND-ROADMAP.md` —— git 首提 `a052903` 已完成，requirements 尚未建。
3. **修复后**（13:02-13:07）：`7ae7dda`（验收修复 25 文件）、`SECRET-HANDLING.md` 初版、`PROGRESS.md` —— 密钥出工作区、敏感接口加门禁、README 密钥段修正。

**第二轮：路线图执行（下午，本索引上午版之后）**

4. **姿态拍板**（`f7084d4`）：SECRET-HANDLING 新增 §0 —— Tailscale 内网私有，不轮换、不清洗历史；`e557ebd` 将该文件 gitignore、本地有意保留。
5. **能力补齐**（`d9a4f71`、`f0965a7`、`914cd50`）：daemon 第 10 个任务 content_inventory（每日库存提醒）；新 skill `.agents/skills/xhh-content-pipeline/`（内容流水线总 SOP，纯文档）；外部看门狗 `tools/watchdog.ps1` + `tools/install_watchdog.ps1`（Windows 计划任务 HermesWatchdog 每 15 分钟，杀 daemon 进程实测自愈）。
6. **清理与收尾**（`b71fdd3`、`0059d15`）：AUDIT 清理执行（tools/ 259→38 .py + 5 .ps1，其余删除/归档）；验收修复（niche_gem_harvester 导入改正、post-xiaoheihe/install.bat 重写为 ASCII、requirements.txt 补 xhshow==0.2.0）。

git 提交序（11 个）：`a052903`（初始，473 文件）→ `ae1ae6a`（requirements.txt + GAP 文档）→ `7ae7dda`（第一轮验收修复）→ `648dc56`（00-index 上午版 + PROGRESS）→ `e557ebd`（gitignore SECRET-HANDLING）→ `f7084d4`（§0 姿态拍板）→ `d9a4f71`（content_inventory）→ `f0965a7`（pipeline skill）→ `914cd50`（watchdog）→ `b71fdd3`（AUDIT 清理执行）→ `0059d15`（第二轮验收修复）。

---

## 3. 跨文档矛盾 / 过期点清单

> 只标注与引用，不改原文。每条给出双方位置与今日（第二次刷新时点）核实结果。已解决的条目保留并标注，供对账。

| # | 点 | 双方位置 | 今日核实结论 |
|---|---|---|---|
| 1 | ARCHITECTURE 称"无 git、无 requirements"，GAP 称"git 首提已完成" | `ARCHITECTURE.md` §6 表格 vs `GAP-AND-ROADMAP.md` 头注 | **已解决，原文未改**：git 现 11 个提交，requirements.txt 在库（`ae1ae6a`）。ARCHITECTURE 该表述继续过期 |
| 2 | ARCHITECTURE P0「REST API 绑 0.0.0.0 无鉴权」 | `ARCHITECTURE.md` §7 P0 第 3 条 | **已重新定性**：SECRET-HANDLING §0 明确 0.0.0.0 在 Tailscale 内网场景是**特性而非缺陷**（`daemon_scheduler.py:434` 仍监听 0.0.0.0:28987，容器/网内机器回调依赖它）。既有工程护栏保留：`/keys`、`/data` token 门禁（`daemon_scheduler.py:288,369`，无 token 403）；CORS 仍 `*`（`:256`），按拍板姿态可接受 |
| 3 | GAP 称「requirements.txt 仍不存在」（G5 缺口、S3 建议） | `GAP-AND-ROADMAP.md` 头注、§1 能力地图、§4.1 S3 | **GAP 自身仍过期**：requirements.txt 已在库且第二轮补齐（`0059d15` 加 xhshow==0.2.0，今日实测 L18）。"README 加重建命令"仍未见落地 |
| 4 | ARCHITECTURE P1「无开机自启、无进程守护」 | `ARCHITECTURE.md` §6、§7 P1 第 1 条 | **两个半条均已解决**：Startup 目录自启 vbs（第一轮已核实）+ 外部看门狗已上线（`914cd50`：`tools/watchdog.ps1` 独立探测 `/status`，失败时直连 TG 报丧并拉起 run_daemon_silent.vbs 自愈；`schtasks` 实测 HermesWatchdog 计划任务就绪、每 15 分钟）。GAP G3 可销 |
| 5 | README 结构性过期 | `README.md` vs `ARCHITECTURE.md` §5（Docker 架构已退役） | **仍成立**：今日 grep 实测 README 全文 0 处提及 `daemon_scheduler.py`，架构分工仍按 Docker 旧架构描述。GAP Top3 的「README 更新（daemon 章节）」是 Top3 中唯一未做项 |
| 6 | SECRET-HANDLING「历史含旧密钥」 vs 扫描「CLEAN」 | `SECRET-HANDLING.md` §1 vs PROGRESS 扫描结论 | **范围不同仍对，且处置已拍板**：CLEAN 指工作区/HEAD；旧值仍在 `a052903` 历史。§0 已决策不清洗——历史值按"仅内网可见"处理，**仅当未来推公网远程时才须先执行 §2 轮换+清洗** |
| 7 | AUDIT 判定 223+33 个文件可清理 | `AUDIT-tools-cleanup.md` §七 | **已执行**（`b71fdd3`）：今日实测 tools/ 38 个 .py + 5 个 .ps1 在岗，`_archive/tools/` 59 .py + 2 .ps1、`_archive/root/` 12 项。原文身份已从计划变为账目 |
| 8 | GAP G2「.venv 缺失，发帖流水线是坏的」 | `GAP-AND-ROADMAP.md` §1 发布行、§2 G2 | **已解决**：`.agents/skills/post-xiaoheihe/.venv` 今日实测已存在；install.bat 已重写为 ASCII（`0059d15`）并可复现环境。环境就绪，真正跑通尚差"发一篇帖"的人工环节 |
| 9 | GAP G6「host-automation 三处漂移」 | `GAP-AND-ROADMAP.md` §2 G6；`ARCHITECTURE.md` §5 失配表 | **仍成立**：`host.docker.internal`（SKILL.md L17/L35/L42）、harvester 示例混入 trigger 语境（L73-75 附近）、`related_skills: [infra-giveaway-triage]` 悬空（L12）均未改。注意区分：niche_gem_harvester 本体的导入错误已修（`0059d15`，`tools/niche_gem_harvester.py:268`），SKILL 文档漂移是另一回事 |
| 10 | ARCHITECTURE 称 `/keys` 返回明文 key「有泄露面」 | `ARCHITECTURE.md` §5 host-automation 核对表 | **已过期（保留对账）**：token 门禁已加（同第 2 条），SKILL.md 示例已带 `?token=` |
| 11 | ARCHITECTURE P0「README:24 明文真实 Key」 | `ARCHITECTURE.md` §7 P0 第 1 条 | **工作区已修复**；该 Key 仍在 git 历史 `a052903` 中，处置已由 SECRET-HANDLING §0 拍板为**不清洗**（推公网远程时才触发 §2） |
| 12 | ARCHITECTURE「hermes_channel.json 编码异常」 | `ARCHITECTURE.md` §6、§7 P2 | **部分处理，仍挂**：文件已出 git 并入 .gitignore（`7ae7dda`，今日实测文件仍在 config/ 本地存在）；文件本体的编码问题未见修复动作 |
| 13 | ARCHITECTURE 任务表 9 个 vs daemon 现状 | `ARCHITECTURE.md` §6 任务全表 vs `services/daemon_scheduler.py` | **新增过期点**：TASKS（`daemon_scheduler.py:69` 起）今日实测 **10 个任务**，新增「内容库存每日提醒（推文时效/囤稿/巡检池）」（content_inventory，`:125`，`d9a4f71`）。凡引用 ARCHITECTURE 任务全表处需按 10 个换算 |
| 14 | GAP Top3 行动路径 vs 第二轮实际 | `GAP-AND-ROADMAP.md` §Top3 | **大部分已执行**：venv/install.bat、content_inventory（S2）、pipeline skill（§3.1）、watchdog（S1/G3）、requirements 均完成；Top3 仅剩「README 更新（daemon 章节）」（同第 5 条）。GAP 整体应按"路线图已走完大半"读 |
| 15 | PROGRESS 第一轮旧结论（§3/§4） vs 第二轮实际结局 | `docs/PROGRESS.md` §3/§4 vs §6 | **原文已自标注**：PROGRESS 头注以"→ 第二轮"箭头逐项标注旧结论结局；且该文件正被并行刷新，本索引对其的一切引用以刷新后版本为准 |

其他待办状态速查（2026-10-31 下午复核，非矛盾，属路线图状态）：~~看门狗 S1~~ ✅ `914cd50`（HermesWatchdog 实测就绪）；~~内容库存提醒 S2~~ ✅ `d9a4f71`；~~内容流水线 SOP skill~~ ✅ `f0965a7`；~~requirements 锁依赖~~ ✅ `ae1ae6a`+`0059d15`；~~AUDIT tools/ 清理~~ ✅ `b71fdd3`。**仍未做**：日志轮转 S5、README daemon 章节（Top3 余项）、「内容线真正发一篇帖」（GAP 遗留的唯一人工环节）。密钥轮换与历史清洗已由 SECRET-HANDLING §0 **取消**（推公网远程时才触发）。

入库状态：docs/ 六份中仅 `SECRET-HANDLING.md` **有意不入库**（.gitignore L23，本地保留，内容含旧明文值）；其余（含 00-index、PROGRESS）均已提交，工作区 CLEAN。

---

## 4. 文档缺口清单（该有而没有，只列名字与理由）

1. **`docs/OPERATIONS-daemon.md`（daemon 运维手册）** —— 10 个任务的启停、/trigger 用法、日志排查、600s 超时与单实例端口假死等操作知识散落在 ARCHITECTURE 快照和源码 docstring 里；第二轮新增的看门狗（HermesWatchdog 计划任务、`reports/watchdog.log`）与 content_inventory 也没有操作视角的记载。
2. **`docs/API-REFERENCE.md`（daemon REST API 参考）** —— 各接口的鉴权要求、参数与示例需要一处权威记载，避免 host-automation SKILL.md 式的漂移再次发生（该漂移至今未改，见 §3 第 9 条）。
3. **`docs/SKILL-AUTHORING.md`（skill 开发规范）** —— SKILL.md 元数据、脚本依赖声明、与 daemon 实际路由对齐的自查项没有规范可循。注意：`xhh-content-pipeline` 只示范了"内容 SOP"类写法，不解决元数据/依赖声明规范问题。
4. **`docs/SETUP-REBUILD.md`（换机重建指南）** —— 理由已变化：requirements.txt（含 xhshow==0.2.0）与 post-xiaoheihe/install.bat 已就位，但换机重建仍无一篇式文档（Python 版本、.env 变量清单、Startup vbs、HermesWatchdog 计划任务注册）。

增补说明：GAP §3.1 原建议的「内容流水线 SOP」已由 `.agents/skills/xhh-content-pipeline/SKILL.md` 承载（`f0965a7`），不再是文档缺口，不再列出。

---

## 5. 本索引的边界

- 本文件只做导航、时点标注与矛盾登记，不代替任何原文档陈述事实。
- 所有"已修复/仍存在"判断均基于 2026-10-31（11 个提交时点）的 git 历史、源码与文件系统实测；`PROGRESS.md` 正在并行刷新，此后有新提交或新文档版本时，§3 表格需复核更新。
