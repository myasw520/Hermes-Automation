# Hermes-Automation 缺口评估与增补路线图（GAP-AND-ROADMAP.md）

> 生成日期：2026-10-31 ｜ 性质：产品功能视角的缺口评估 + 增补建议，不含安全清单复述
> 核心问题：**目前缺少什么？要不要再加 skill 或脚本？加什么最划算？**
> 方法：三层过滤法——先发散 → 剔除"烂大街/不切实际/维护不起" → 补齐必须的基础件。
> 前置输入：`docs/ARCHITECTURE.md`（架构盘点）、`docs/AUDIT-tools-cleanup.md`（脚本审计）。
> 本文档撰写前已实测复核：git 首次提交完成（473 文件）、Startup 目录已有 3 个自启 vbs、
> `.venv` 仍缺失、`requirements.txt` 仍不存在、内容产物最新落盘为 2026-10-24。

---

## 0. 结论速览（TL;DR）

**不缺采集器，不缺新任务源，缺三样东西：内容生产线的"人工卡点"自动化、daemon 的外部看门狗、可重建性三件套。**
建议：**新增 1 个纯文档 skill、2 个脚本/任务、3 个基础件；明确拒绝 4 类常见增补。**
总投入约 **1 个工作日**，覆盖当前 90% 的痛感。

---

## 1. 现状能力地图

四个 skill + 九个任务 + daemon API 各自覆盖的能力（✅=已覆盖，⚠️=覆盖但有名实不符，❌=空白）：

| 能力域 | 具体能力 | 载体 | 状态 |
|---|---|---|---|
| 调度 | 周期任务调度、600s 超时、防重 | daemon_scheduler.py | ✅ 9/9 健康，日志 0 失败 |
| 调度 | 按需触发、状态/日志/Key 池查询 | daemon REST API | ✅ 含 /trigger?sync= 同步模式 |
| 遥控 | Agent 查状态/触发任务/读数据 | skill: host-automation | ⚠️ 3 处文档漂移（host.docker.internal、幽灵任务、悬空引用） |
| 情报 | GitHub 周报 / 限免 / B站 / 羊毛 | weekly_github、freegames、bili_intel、wool_radar | ✅ 全自动推送 TG |
| 资源 | 公益 Key 收割/测活/签到 | welfare_harvester、daily_checkin | ✅ keys_pool 5 节点活态 |
| 学习 | 408 真题提纯、打印 PDF、dashboard | postgrad_papers、build_print_papers、cs408-dashboard | ✅ 全自动 |
| 舆情 | 小黑盒恶评巡检 | xhh_comments_sentinel | ⚠️ 任务 10 分钟一次在跑，但巡检池（monitored_articles.json）**只有 1 篇文章**且需手工喂 |
| 创作 | 写作风格库 | skill: xhh-style-bible | ✅ 纯文档，完备 |
| 发布 | 小黑盒 CDP 发帖（存草稿） | skill: post-xiaoheihe | ❌ **`.venv` 缺失，流水线当前跑不起来**（install.bat 现成但未执行） |
| 素材 | 挖宝/屯稿/工具雷达 | niche_gem_harvester、build_stockpile_drafts 等 19 个活跃脚本 | ⚠️ 手工触发，stockpile 已囤 A/B/C/DS/WAIFU 五套素材 |
| 告警 | 任务结果推 TG | wool_radar（10+ 脚本 import） | ⚠️ **daemon 是唯一告警通道，它死了告警一起死** |
| 自启 | 开机拉起 daemon/dashboard | Startup 目录 3 个 vbs | ✅ **已存在**（ARCHITECTURE.md 的 P1 此半条已过时） |
| 守护 | 进程死了自动拉起 + 主动报丧 | — | ❌ **空白** |
| 版本 | git 回滚点 | git（首提 a052903） | ✅ 已解决（P0 已修） |
| 依赖 | 依赖清单/重建 | — | ❌ **空白**（根目录无 requirements.txt） |
| 发布-监控闭环 | 发新帖自动纳入巡检 | — | ❌ **空白**（发布与巡检两个世界互不相通） |

**产品视角一句话**：消费侧（情报、资源、巡检）全自动且健康；生产侧（素材→草稿→发布→巡检）每一环都健康，但**环与环之间的接口全是人工**，且最近一次产出停在 10-24——生产线停摆一周，系统对此**无任何感知和提醒**。这就是最大的缺口。

---

## 2. 缺口清单（按痛感排序）

| # | 缺口 | 痛感 | 证据 |
|---|---|---|---|
| G1 | **内容线停摆无感知**：囤了 5 套素材、装了发布 skill，但最新文章停在 10-24（今天 10-31）；没有"该发帖了"的提醒机制，生产线全靠想起来 | 高 | `reports/xiaoheihe_articles/` 最新 md 为 20261024；`reports/ai_daily_posts/` 同样停在 1024；stockpile_drafts 5 套 blocks 无人消费 |
| G2 | **发帖流水线当前是坏的**：post-xiaoheihe 强制 `.venv\Scripts\python.exe`，目录不存在，下次想发帖第一步就报错 | 高 | `.agents/skills/post-xiaoheihe/` 无 `.venv/`；`install.bat` 存在未跑 |
| G3 | **告警单点**：所有任务靠 daemon 内的 wool_radar 推 TG，daemon/pythonw 崩溃后无人发消息、无自动重拉。开机自启已解决"重启后要手工点"，但**运行中崩溃**仍无解 | 高 | daemon_scheduler.py 是唯一 TG 出口；Startup vbs 只在开机时执行一次 |
| G4 | **巡检池没人喂**：sentinel 10 分钟一次巡检，池里只有 10-27 手工加的 1 篇。发新帖后忘记加 link_id = 新文章裸奔 | 中 | `config/monitored_articles.json` 仅 1 条（Win11 右键菜单文） |
| G5 | **依赖不可重建**：git 保住了代码，但 requirements 没锁定，换机后 19 个活跃脚本 + 4 个 harvester 链路全部要靠回忆装依赖 | 中 | 根目录无 requirements.txt/pyproject.toml；已知隐式依赖 requests/playwright/ddddocr/Pillow |
| G6 | **host-automation 文档漂移**：Agent 按文档遥控会失败（host.docker.internal 在宿主机不可解析）、会被误导去触发不存在的任务 | 中 | `.agents/skills/host-automation/SKILL.md:17,64-70,12` |
| G7 | 日志无轮转：scheduler.log 已 99KB 永续增长（ARCHITECTURE P2，维持原判，痛感低） | 低 | `reports/scheduler.log` 99,400 bytes |
| G8 | 223+33 个死脚本待清理（AUDIT 已规划为下阶段动作，本文不重复展开，仅提醒：**它是 G5 的前置——先锁 requirements 再删，才知道锁的是什么**） | 低 | `docs/AUDIT-tools-cleanup.md` §五 |

---

## 3. 「建议新增 skill」清单

经三层过滤，**只建议 1 个，且是纯文档形态（零脚本零维护）**：

### 3.1 ✅ 建议新增：`xhh-content-pipeline`（内容流水线 SOP，纯文档）

- **做什么**：一页 SKILL.md，把散在三处的内容资产串成一条带步骤的流水线：素材在哪（reports/hermes_output/stockpile_drafts + xiaoheihe_articles）→ 怎么生成草稿（post-xiaoheihe 流程，先跑 install.bat）→ 怎么过风格关（xhh-style-bible 分册路由）→ **发布后必做一步：把文章 link_id 追加进 config/monitored_articles.json** → 怎么确认巡检已接管（/status 看 sentinel）。
- **触发场景**：用户说"发个帖/写篇推文/看看囤稿"时自动加载。
- **覆盖的空白**：G1 + G4 的"人"侧。现状三个资产互不引用，每个新 agent 会话都要重新发现流水线；发布后喂巡检池这一步目前**只存在于人的记忆里**（证据：池里 1 篇 vs 实际发过的更多篇）。
- **工作量**：1-2 小时，纯文档。
- **依赖**：无（引用现有 skill 与文件路径）。
- **ROI**：极高。一次写作，永久消除"流水线藏在哪/发完要干嘛"的会话级重复发现成本。

### 3.2 ❌ 明确不建议新增（防堆砌清单）

| 候选 skill | 拒绝理由 |
|---|---|
| **TG 双向遥控 bot**（发消息查状态/触发任务） | 烂大街方案且与现有能力 100% 重叠：ZCode + host-automation skill 已经能在任何会话里查状态触发任务；再养一个常驻 bot 进程 = 多一个会死的单点 + token 管理 + 命令解析维护。单人场景"打开终端问一句"比"配置 bot"便宜两个数量级 |
| **自动发布 skill**（把存草稿变成全自动点发布） | 人工质检是 AI 内容的最后防线：风格自检（style-bible 的去 AI 味清单）+ 封面/题注人工扫一眼，价值大于省下的 30 秒；且全自动发布叠加风控风险（小黑盒对自动化发帖不友好），换来的只是每天最多 1 篇的量——不值得 |
| **内容数据统计 skill**（阅读量/涨粉 dashboard） | 样本量不支持：一周 1-2 篇的发布频率，统计没有统计学意义；等月更 10 篇再谈 |
| **通用 RPA/抢券 skill** | 与既有 4 skill 无协同，本质是重新发明 post-xiaoheihe 已固化的 CDP 能力 |

> 附加原则：**如果未来一个月内发现自己手工重复同一操作 ≥3 次，再把它固化为 skill**——按需生长，不预支维护成本。

---

## 4. 「建议新增脚本/任务」清单

### 4.1 ✅ 建议新增

| # | 名字 | 做什么 | 为什么值得（证据） | 工作量 | 依赖 |
|---|---|---|---|---|---|
| S1 | **watchdog.ps1**（外部看门狗，挂 Windows 计划任务） | 每 15-30 分钟探测 `127.0.0.1:28987/health`；失败则：① 用 curl 直接调 TG Bot API 发"daemon 挂了"（**不经过 daemon**，这是关键）② 重新拉起 `run_daemon_silent.vbs` ③ 结果写独立日志 | 堵 G3：daemon 是唯一告警通道，它死后 TG 永远沉默——这是无人值守的致命单点。形态极轻：一个 ~40 行 PS1 + 一条 schtasks，Startup 目录已有 3 个 vbs 证明此路可走 | 2-4 小时 | Windows 计划任务；TG token（从 config_lib.py/.env 读，不新造密钥） |
| S2 | **content_inventory.py**（内容库存提醒，注册为 daemon 每日任务） | 每天扫一次：`reports/xiaoheihe_articles/` 最新 md 距今天数、`stockpile_drafts` 可用套数、`monitored_articles.json` 条数 → 组装一条 TG 提醒（如"4 天没发帖，囤稿 5 套，巡检池 1 篇"） | 堵 G1 + G4 的"机器"侧：生产线停摆一周系统毫无感知；一个只读脚本，无浏览器无 LLM，不会坏。同时给"发完帖忘了喂巡检池"兜底 | 1-2 小时 | daemon TASKS 注册一行（这是唯一需要改 daemon 的地方） |
| S3 | **requirements.txt**（手工裁剪版） | `pip freeze` 后人工删掉无关项，锁定 requests/playwright/ddddocr/Pillow + daemon 全链依赖；README 加一行重建命令 | 堵 G5：git 已保住代码，依赖是"可重建"的最后缺口；AUDIT 的 223 文件清理动手前必须有它，否则删完才知道少了什么 | 1 小时 | 无 |
| S4 | **执行 post-xiaoheihe/install.bat + 冒烟验证** | 跑现成 install.bat 重建 .venv，用 xhh_check.py 打开编辑器页验证一遍 | 堵 G2：流水线当前是断的；脚本和文档全齐，只差执行 | 0.5 小时 | Chrome；一次性 |
| S5 | （可选）**log 轮转**：daemon 启动时检查 scheduler.log >5MB 则 rename 为 .old | 维持 ARCHITECTURE P2 原判，顺手做即可，不单独立项 | 1 小时 | 改 daemon_scheduler.py 启动段 |

### 4.2 ❌ 明确不建议新增（防堆砌清单）

| 候选任务/脚本 | 拒绝理由 |
|---|---|
| **Epic 等限免自动领取** | 收益是"省一次点击"，代价是账号风控/验证码对抗的持续维护 + 封号风险；现有 freegames 3 天一推已足够，点击由人完成是最优解 |
| **AI 日报/新采集源类任务**（再加一个 harvester） | 存量产线都在空转：ai_daily_posts 停在 10-24、xiaoheihe_articles 停在 10-24。**先让现有素材变现金（发出去），再谈加新源**——加源只会增大未消费库存 |
| **keys_pool 消耗预测/余额统计** | 5 个节点，/keys 一眼看完；预测模型需要历史序列，样本远不够，纯过度工程 |
| **多进程并发调度/任务队列框架**（celery/APScheduler 重写） | 9 个任务串行跑得很好（日志 0 失败），600s 超时对唯二可能超时的任务（harvester/print_papers）调参即可；换框架是典型的"用大炮打蚊子"并引入新故障面 |
| **全量自动备份方案** | git 已覆盖全部代码与文档；data/ 的 vault 本身可再生，SQLite 小到可随 git 提交。真正的灾备需求已被 git + .gitignore 策略满足，再建备份体系维护不起 |

---

## 5. 下一步执行路径（按性价比排序 Top 3）

| 序 | 行动 | 一句话说明"做完后什么变好了" | 工作量 |
|---|---|---|---|
| **1** | **内容线急救三连**：S4（跑 install.bat 修活发帖流水线）→ S2（库存提醒任务）→ 3.1（pipeline SOP 文档，含"发布后喂巡检池"步骤） | 停摆一周的内容生产从"想起来才发、发完裸奔"变成"被提醒、有素材、发完有人盯" | ~半天 |
| **2** | **S1 看门狗** | 无人值守从"daemon 死了就全体静默"升级为"30 分钟内自愈 + 手机收到报丧"——这是无人值守目标的最后一块拼图 | 2-4 小时 |
| **3** | **可重建性三件套**：S3 requirements.txt + 修复 host-automation SKILL.md 三处漂移 + README 更新（skills 路径/daemon 章节） | 换机重装和新 agent 会话从"靠回忆踩坑"变成"照文档一条命令跑通" | 1-2 小时 |

之后的自然顺序：按 AUDIT 执行 223+33 文件清理（G8，需先完成上表第 3 项）→ 顺手做 S5 日志轮转。

**守则**：上表做完前，不新增任何采集源、不新增任何 skill、不动调度框架。
