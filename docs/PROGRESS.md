# Hermes-Automation 阶段进度记录（PROGRESS.md）

> 记录日期：2026-10-31 ｜ 性质：**两轮阶段记录**。第一轮（凌晨—午后）：安全治理 + 缺口评估（§1-5）；第二轮（下午）：路线图执行（§6）。
> §3/§4 为第一轮原文，结论已部分过时，原文保留、逐项以"→ 第二轮"箭头标注实际结局；当前真实遗留以 §6.3 为准。
> 前置文档：`docs/ARCHITECTURE.md`、`docs/AUDIT-tools-cleanup.md`、`docs/GAP-AND-ROADMAP.md`、`docs/SECRET-HANDLING.md`
> 写法说明：本文只记实际发生并经复核的事，未做的明写未做。所有证据均已重新核实（git log / 实测接口 / 文件系统），非转抄前报。

---

## 1. 阶段目标回顾

阶段起点（2026-10-31 凌晨）：无 git、无 docs/、根目录 13 个散落脚本 + tools/ 259 个 .py（大量一次性实验残留）、README 含明文 API key、密钥硬编码在多个脚本、daemon REST API 绑 0.0.0.0 且敏感接口无鉴权。

本阶段目标：① 盘点架构与脚本资产；② 修复 P0 安全问题（密钥、鉴权、版本控制）；③ 评估功能缺口并给出路线图；④ 交付验收并修复验收发现的缺陷。

---

## 2. 逐项交付与证据

### 2.1 资产盘点（tech-architect/Explore 代产出，父代理落盘）

| 交付物 | 证据 |
|---|---|
| `docs/ARCHITECTURE.md`（21KB）——架构盘点 + 风险清单 P0×3 / P1×3 / P2×5 / P3×5（§7） | 文件在案（01:46）；风险逐条带源码行号 |
| `docs/AUDIT-tools-cleanup.md`（18.5KB）——259 个 tools 脚本全量分类：保留 36 py + 3 ps1，可清理 223 py + 2 ps1；根目录可清理 33 个；合计约 260 个 | 文件在案（01:35）；§五 L153-156 汇总 |

### 2.2 P0 安全修复（本轮主任务）

| 动作 | 验证方式 | 证据 |
|---|---|---|
| 新增 `services/config_lib.py`（.env 统一加载，单一代码路径） | 读源码确认无明文、有回退告警 | 文件在案；docstring 明确"本文件不含任何明文密钥" |
| `.env` 补全（TELEGRAM_×5、GATEWAY(OPENAI_×2)、API_ACCESS_TOKEN、GMAIL_×2、QQ_×2、GITHUB_TOKEN、REGISTER_PASSWORD 等 20 个变量名） | 实读 `.env` 键名（未读值） | `.env` 已被 .gitignore 排除（已核实 .gitignore 含 `.env`） |
| 20 个脚本去硬编码：13 个接线 config_lib + 7 个占位符中和 | 提交记录 + 密钥特征串全仓扫描 | 提交 `a052903`；`git grep` 扫描 6 组特征串 = **CLEAN** |
| daemon `/keys`、`/data` 加 token 门禁 | **今日实测**：无 token → 403，带 token → 200 | `daemon_scheduler.py:56-66`（门禁逻辑）；提交 `a052903` |
| README / ps1 密钥打码 | README 已无明文 key（扫描 CLEAN） | 提交 `a052903` |
| `.gitignore` 补全（.env、credentials.json、keys_pool.json、scheduler_state.json、pushed_history.json、hermes_channel.json 等） | 实读文件 | 在案 |
| git init + 3 次提交 | `git log` 核实 | `a052903`（12:37，**473 文件 / +68,482 行**）→ `ae1ae6a`（12:47，2 文件 +139）→ `7ae7dda`（13:02，**25 文件 +54/-73**） |

### 2.3 缺口评估与重要事实修正

`docs/GAP-AND-ROADMAP.md`（12.9KB，提交 `ae1ae6a`）。核心结论：**不缺采集器，缺"环与环之间的接口"**；Top3 = 内容线急救三连 / watchdog 看门狗 / 可重建性三件套。

评估中修正了早期报告的两处误判（均已实测复核为真）：
- **Docker `hermes` 容器真实在运行**（`docker ps`：Up 17 hours）——早期"已退役"判断有误；
- **开机自启已存在**（Startup 目录 3 个 vbs：Start_Hermes_Automation / Start_CS408_Dashboard / Hermes-Bridge-Autostart）——ARCHITECTURE.md P1"无自启"半条已过时。

另确认两个事实（今日实测仍在）：内容生产线停摆一周（`reports/xiaoheihe_articles/` 最新产物 2026-10-24，今天 10-31）且系统无感知；post-xiaoheihe `.venv` 缺失，发帖流水线当前跑不起来（install.bat 未执行）。

### 2.4 交付验收（ux-tester）与验收修复

验收发现：P0×1（改动清单外仍有明文密钥且部分进 git 历史）、P2×1（README 凭证段指向遗留 credentials.json）、P3×3（host-automation SKILL.md 的 /data 示例缺 token、假 key 示例泄露首尾片段、防火墙建议 -Profile Any）。

修复（提交 `7ae7dda`，25 文件 +54/-73）：

| 修复 | 验证方式 | 结果 |
|---|---|---|
| 4 个活脚本去硬编码：`services/mail_receiver.py`（IMAP 授权码）、`tools/fetch_official_full_pdf_papers.py`（GitHub PAT）、`tools/chatanywhere_harvester.py` + `tools/docode_harvester.py`（注册密码），接线 config_lib | `python -m py_compile` 4 文件 + config_lib | **COMPILE ALL OK** |
| `config/hermes_channel.json` 出 git（-35 行）并入 .gitignore | `git show 7ae7dda` | 在案 |
| 17 个一次性/归档脚本密钥中和为 `os.environ` 占位 | 扫描 CLEAN | 在案 |
| README 凭证段改指 .env 单一来源；SKILL.md /data 示例补 `?token=`、假 key 占位 | 实读 SKILL.md:88 | 在案 |
| 修复中连带发现批量替换造成的 9 个语法错误并全部修正 | 逐文件复检 | 全部 CLEAN |

产出 `docs/SECRET-HANDLING.md`（3.5KB）：轮换步骤与 git 历史清洗指南。注意：**该文件目前未入库（git status 唯一未跟踪项）**——它本身含明文旧值（供 filter-repo 替换用），入库前必须二选一：脱敏后提交，或加入 .gitignore。

### 2.5 基础设施

`requirements.txt`（提交 `ae1ae6a`）：9 个依赖全部 pin 版本（requests/playwright(+stealth)/ddddocr/pillow/opencv/numpy/bs4/pywin32），提交说明注明全部在活解释器上 import 验证通过；内含重建命令两行。

---

## 3. 遗留清单（分级）

### A. 需要用户执行（机器无法代劳）

| # | 事项 | 状态 | 依据 |
|---|---|---|---|
| A1 | **密钥轮换**（TG Bot Token / ZeroGate Key / GitHub PAT / QQ+Gmail 授权码 / 注册密码，逐项操作步骤见 `docs/SECRET-HANDLING.md` §2.1） | **未完成**。截至本文记录无任何完成证据；严格说 P0 泄露面只剩 git 历史里的旧值（工作区已 CLEAN） | SECRET-HANDLING.md §1-2 |
| A2 | git 历史清洗（可选）：若确认仓库永不推远程可暂缓（SECRET-HANDLING.md §2.2 已标注）；若要推远程则必须先做 | 未做（本仓库当前无远程） | 同上 |

> → 第二轮结论（`f7084d4`）：用户拍板项目为 **Tailscale 内网私有**（本机 zzx-1 100.127.21.69 ↔ 网关机 zzx 100.114.18.45，即 ZeroGate 所在机），**明文密钥可用、不轮换、git 历史不清洗**，该安全姿态已写入本地版 SECRET-HANDLING.md §0。A1/A2 从"遗留"转为**经用户决策关闭**；唯一红线：推任何公共远程前必须轮换+清洗（见该文件）。SECRET-HANDLING.md 保持不入 git（`e557ebd` 加入 .gitignore，`f7084d4` 追加拓扑注释行）。

### B. 下阶段建议（均为 GAP-AND-ROADMAP 已立项项，未开工）

| # | 事项 | 来源 | 现状证据 |
|---|---|---|---|
| B1 | GAP Top1 内容线急救三连：S4 跑 install.bat 修 `.venv`（实测仍 MISSING）→ S2 `content_inventory.py` 库存提醒（实测无此文件）→ 3.1 `xhh-content-pipeline` SOP skill（实测无此 skill） | GAP §5-1 | 全部未做 |
| B2 | GAP Top2：`watchdog.ps1` 外部看门狗（实测根目录无此文件） | GAP §5-2 | 未做 |
| B3 | GAP Top3 余项：host-automation SKILL.md 三处漂移修复（实测 `host.docker.internal` 等 11 处仍在）、README 补 daemon 章节（实测 README 零处提及 daemon）。**requirements.txt 这一项已提前完成** | GAP §5-3 | 部分完成 |
| B4 | AUDIT 清理：223 个 tools + 33 个根目录文件。**现在有 git 了，可以安全做**（删除前先 `git status` 确认工作区干净即可） | AUDIT §五 | 未做（tools 仍 259 py、根目录仍 13 py，实测） |
| B5 | ARCHITECTURE.md 对齐：它是修复前快照，其中 P0"密钥硬编码 / 无鉴权"已被部分修复；另外它漏记了 Docker hermes 容器与 3 个自启 vbs | §2.3 修正 | 待更新 |

> → 第二轮结论：**B1、B2、B4 全部完成**（逐项证据见 §6.2 第 2/5/6 条）；B3 中 requirements.txt 已在第一轮完成、其余（README 补 daemon 章节）未做，顺延为 §6.3 的 D4；B5 未做，同样顺延为 D4。B4 完成后 tools/ 实测 38 py + 5 ps1（本轮核验）。

### C. 风险提示（本阶段修复未覆盖的面，已核实）

- daemon 仍绑 **0.0.0.0**（`daemon_scheduler.py:428`）；`/trigger`（GET/POST）与 `/status` `/logs` 仍无鉴权（门禁只加了 `/keys`、`/data`）。ARCHITECTURE P0"绑 0.0.0.0 无鉴权"只能算**部分修复**：敏感读接口已封，绑定面与触发接口未收敛。
- `docs/SECRET-HANDLING.md` 未入库且含明文旧值（见 §2.4 注意事项）。

---

## 4. 下一步判断（按性价比，来源标注 GAP-AND-ROADMAP 章节）

1. **GAP Top1 内容线急救三连**（§5-1，约半天）：install.bat 是现成的，只是没人跑；S2 是只读脚本不会坏；SOP 是纯文档。做完后停摆一周的内容生产从"想起来才发"变成"被提醒、有素材、发完有人盯"。这是当前痛感最高（G1/G2 均"高"）且成本最低的一条。
2. **GAP Top2 watchdog.ps1**（§5-2，2-4 小时）：daemon 是唯一 TG 告警通道，它死后手机永远沉默——无人值守的致命单点，40 行 PS1 + 一条 schtasks。可单独做，不依赖 Top1。
3. **先做 B4 清理再做任何新东西**（AUDIT §五；GAP §5 尾注）：requirements.txt 已就位（GAP 明言它是清理的前置），git 已就位，223+33 文件清理成本已降到最低；不清则每次安全审计和会话发现成本持续放大。

守则重申（GAP §5）：上表未完成前，不新增采集源、不新增 skill、不动调度框架。本阶段遵守了这条（未加任何源/skill）。

> → 第二轮结论：本轮即上述判断的执行阶段，第 1、2、3 条全部完成（见 §6.2），且第二轮实质新增了一个 skill（`xhh-content-pipeline`，GAP 3.1 本身就是"加一个纯文档 skill"，故不算违反守则，但已如实记录）；守则其余部分（不加采集源、不动调度框架）继续遵守。

---

## 5. 打转检查

对比 GAP-AND-ROADMAP（12:46 生成）的建议与本阶段实际动作（13:02 收尾）：

| GAP 建议 | 本阶段 | 跳过理由是否成立 |
|---|---|---|
| Top3 的 S3 requirements.txt（本应排第三批做） | **立即做了**（12:47 提交，与 GAP 文档同批次） | — |
| Top1 内容线急救三连 / Top2 watchdog | 未做 | **成立但需盯住**：本阶段的既定范围是安全 P0 修复 + 验收缺陷闭环，验收 P0（清单外文件仍有明文密钥）是必须当场处理的硬阻断，挤占的时间合理。但这两项已是连续第二阶段排期未动工，下阶段若继续让位于"再盘一遍/再修一轮安全"，即构成打转 |
| 守则"不新增采集源/skill/框架" | 遵守 | — |

**结论：不在打转。** 本阶段是单向推进的（盘点→修复→验收→修复→文档），每步都有可核查的产物和提交号，且守住了"不加新东西"的守则；但产出的全是"地基"（git、密钥治理、依赖锁定、路线图），GAP 诊断的最高痛感问题（内容线停摆、daemon 单点）一件都还没动手。判断依据：本轮新增文档 0 份重复内容、新增脚本仅 1 个（config_lib，P0 修复必需）、未新增任何采集器。**下一个阶段应当是"动手做 Top1/Top2"的执行阶段，而不是再产出评估文档**——那是打转开始的标志。

---

## 6. 第二轮阶段（2026-10-31 PM）：路线图执行

### 6.1 前提：安全姿态落盘

用户拍板：项目为 **Tailscale 内网私有**（本机 zzx-1 `100.127.21.69` ↔ 网关机 zzx `100.114.18.45`，即 ZeroGate 所在机），**明文密钥可用、不轮换、git 历史不清洗**，授权直接执行第一轮 §4 的路线图。据此第一轮遗留 A1/A2 经用户决策关闭（红线不变：推公共远程前必须轮换+清洗）。提交 `f7084d4` 将该姿态写入本地版 `docs/SECRET-HANDLING.md` §0；此前 `e557ebd` 已把该文件加入 .gitignore 保持本地私有。

### 6.2 逐项交付与证据（提交号均可 `git show` 复核）

| # | 交付 | 验证方式 | 证据 |
|---|---|---|---|
| 1 | 安全姿态落盘：SECRET-HANDLING.md §0（本地文件不进 git） | `git show f7084d4` | `.gitignore` +1 行（Tailscale 拓扑注释）；姿态三条写入 §0 |
| 2 | **GAP Top1-S4**：post-xiaoheihe `.venv` 重建。手动 `python -m venv` + pin 版 patchright 1.58.2 / playwright 1.58.0（install.bat 有 GBK 编码坑，暂绕开，后于 `0059d15` 重写为 ASCII 版） | 冒烟：`xhh_check.py --help` 通过 | `.venv` 目录在案；install.bat 重写在 `0059d15` |
| 3 | **GAP Top1-S2**：`tools/content_inventory.py`（+117 行）每日库存提醒：推文 7 天没发 / 囤稿 10 套 / 巡检池 1 篇 → TG 话题 5；注册为 daemon 第 10 任务（`daemon_scheduler.py:124`） | daemon `/trigger` 实测触发执行成功 | 提交 `d9a4f71`（2 文件 +123） |
| 4 | **GAP Top1-3.1**：新 skill `.agents/skills/xhh-content-pipeline/SKILL.md`（+96 行）：六步内容流水线 SOP（囤稿→构建→风格关→手机发布→喂巡检池→库存确认） | 文件在案 | 提交 `f0965a7` |
| 5 | **GAP Top2**：`tools/watchdog.ps1`（98 行）+ `install_watchdog.ps1`（15 行，UTF-8 BOM）：计划任务 HermesWatchdog 每 15 分钟探测 `/status`，挂了直连 TG Bot API 报丧（绕开死掉的 daemon）→ 重拉 `run_daemon_silent.vbs` → 复测 | **实测**：手动杀 daemon → TG 收到 2 条消息（挂了/恢复）→ 约 15 秒自愈 | 提交 `914cd50`；两文件在案 |
| 6 | **AUDIT 清理执行**（§2.2 B4）：tools/ 259→**38** py + 5 ps1（163 A 级删除、61+10 B 级归档 `_archive/tools/`）；根目录 19 删 + 14 归档 `_archive/root/`。清理前做了 keep-list 完整性 + 交叉 import 防御校验；清理后全量语法扫 0 错，daemon 实触发 daily_checkin 成功 | 本轮文件系统复核：`tools/*.py` = 38、`tools/*.ps1` = 5、`_archive/tools/` 59 py + 2 ps1、`_archive/root/` 12 项 | 提交 `b71fdd3` |
| 7 | 验收修复（`0059d15`，4 文件 +14/-30）：P1 `tools/niche_gem_harvester.py` 的 `from tools.vision_auditor` → `from vision_auditor`（tools/ 无 `__init__.py`，标准调用必炸——初版老雷，非本轮引入）；install.bat ASCII 重写（消 GBK 坑）；requirements.txt 补 `xhshow==0.2.0`；删除编辑器残留 `editor_current.png` | `git show 0059d15 --stat` | 全部在案 |

### 6.3 当前真实遗留清单（第一轮 §3 的替代，分级）

第一轮 GAP Top1/Top2/Top3 已基本做完（Top3 中 requirements.txt 在第一轮完成）。**以下为全部现存遗留**：

| # | 事项 | 级别 | 说明 |
|---|---|---|---|
| 1 | **内容线人工环节：真正发一篇帖** | 高（痛感） | SOP 已就绪（`xhh-content-pipeline` skill）、囤稿 10 套、库存提醒已上线，但**内容线尚未真正跑一篇**（`reports/xiaoheihe_articles/` 最新产物仍停在 2026-10-24）。需要用户或 agent 按流水线走一遍才算闭环 |
| 2 | daemon `/trigger` `/status` `/logs` 仍无鉴权（daemon 仍绑 0.0.0.0） | 低 | 内网定性下低危；0.0.0.0 监听是 Docker hermes 回调需要（`f7084d4` 记录）。若未来引入不可信设备接入 Tailscale，需重新评估 |
| 3 | `scheduler.log` 无轮转，持续增长 | 低 | 加个按大小/日期轮转即可，顺手项 |
| 4 | 文档过时：`docs/ARCHITECTURE.md` 任务表仍是 9 任务（实际 10，content_inventory 未记入）、README 仍未提 daemon 核心地位 | 低 | 下轮顺手刷，非阻断 |

### 6.4 本轮验收结论（ux-tester）

"清理真无损"。P0×0；P1×1（niche_gem_harvester import，已修，见 §6.2-7）；P2×2（install.bat GBK——已修；文档过时——即本文件正在修的这条）；P3×3（已修 2，归档口径 1 条仅表述差异）。

### 6.5 打转检查（第二轮）

第一轮 §4 明确说："下一阶段应当是动手做 Top1/Top2 的执行阶段，而不是再产出评估文档——那是打转开始的标志。"第二轮对照：

| 第一轮承诺 | 第二轮实际 | 结果 |
|---|---|---|
| Top1 内容线急救三连 | `.venv` 重建（S4）+ content_inventory（S2）+ SOP skill（3.1），`d9a4f71`/`f0965a7`/`0059d15` | **全部完成** |
| Top2 watchdog | `914cd50`，实测杀 daemon 15 秒自愈 | **完成** |
| 先清理再做新东西（B4） | `b71fdd3`，259→38，先校验后删 | **完成** |
| "不再产出评估文档" | 本轮新增文档仅 SECRET-HANDLING §0 追记 + 本文件 | **遵守** |

**结论：不在打转，且恰是第一轮要求的"执行阶段"。** 连续两轮排期未动的 Top1/Top2 本轮全部落地，每项带提交号和实测证据；无重复评估、无新增采集源。唯一未竟的是内容线"真发一篇"——这是人工/半人工环节，工具链（提醒→素材→SOP→发布→巡检→库存）已全部就位，下一阶段应直接执行该闭环而非再建任何工具。


---

## 第二轮.5（2026-10-31 晚）：内容质量打磨 + 封面产线（git 443662f）

**触发**：用户反馈"发出来的帖子太 AI 了"、"PIL 封面太丑（已淘汰，实际在用手工 Gemini 生图）"，要求打磨 skill、调研更好的生图方案。

**诊断**：`tools/xiaoheihe_intel_harvester.py` 的 LLM 提示词只有 15 行自制调性，从未接入 xhh-style-bible（167 篇热帖提炼的风格库）——skill 写好了但产线没接上，是"太 AI"的根因。

**交付**：
1. 提示词 v2（"风格宪法"）：三大人味密码 + AI 味黑名单（违者废稿）+ 强制每款游戏差异化写法（禁止机械对称模板）；max_tokens 1200→2400。
2. `docs/RESEARCH-image-gen.md`：10 个候选生图 API 实抓核查（Groq 无生图、Gemini API 免费层无生图、Together 旧情报过时）；自家 ZeroGate 中转模型表实测含 8+ 生图模型（上游账号池 503/404 待用户在管理面板修活）；智谱 GLM-Image 原生 16:9 + 中文精准渲染、0.1 元/张。
3. `tools/cover_generator.py`：双端点 fallback（ZeroGate 优先 → GLM-Image 兜底），实测出图 1728x960 构图合格（主体居左右侧留白给标题，自带 AI 生成角标）。
4. 同素材新旧文对比实测：v2 文（"18块7的吸血鬼，我肝到手机没电"）三大人味密码全部落地——翻车自嘲（凌晨三点手机砸脸上）、具体场景（晕 3D 玩二十分钟躺十分钟）、主观偏见（"这玩意是给老粉的情书，不是入门票"）；每款游戏写法完全不同；黑名单 0 命中。

**遗留**：
- ZeroGate 生图路由 404：**用户已拍板（2026-10-31）——网关不做生图 API，封面维持手工 Gemini**；cover_generator.py 保留为可选备胎（GLM-Image 路不依赖 ZeroGate，实测可用，0.1 元/张），不接产线不推广
- style-bible 分册（track_*.md）尚未按赛道路由进各产线脚本（当前只接了总纲），下一轮可做
- 新提示词只过了文本验收，尚未走过完整发帖链路（真机发布反馈循环待第一篇正式帖）
