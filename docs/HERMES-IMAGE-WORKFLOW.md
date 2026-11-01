# Hermes 采图工作流（dispatch_to_hermes.py 使用说明）

> 2026-10-31 ｜ 分工（用户拍板）：**写稿 = ZCode，采图 = Hermes agent，ZCode 只做管理不采图**

## 职责边界

| 环节 | 谁 | 用什么 |
|---|---|---|
| 写赛道稿 | ZCode | 风格宪法提示词 + GitHub API 实时星数（已完成 5 篇） |
| 提取仓库清单、生成任务包 | ZCode（管理） | `dispatch_to_hermes.py --scan` |
| **采图** | **Hermes**（Docker 容器 `hermes`，:8642 网关） | 它自己跑（README 抓图 + 视觉自检） |
| 拉回宿主 | ZCode（管理） | `--pull`（docker cp 从容器卷） |
| 图质检 | ZCode（管理） | `--audit`（复用 tools/vision_auditor.py） |

## 命令序列

```bash
# 1. 从稿子生成任务包（reports/hermes_output/image_tasks/<track>_task.json）
python tools/dispatch_to_hermes.py --scan

# 2. 派发给 Hermes（每个赛道最长等 30 分钟；即使 HTTP 超时它也会把活干完）
python tools/dispatch_to_hermes.py --send

# 3. 查进度（回图 N/M 仓库）
python tools/dispatch_to_hermes.py --status

# 4. 把容器内的图拉回宿主（docker cp）
python tools/dispatch_to_hermes.py --pull

# 5. vision_auditor 质检（淘汰 logo/banner/二维码，劣图直接删）
python tools/dispatch_to_hermes.py --audit
```

## 已验证的关键事实

- Hermes 网关 `http://localhost:8642/v1/chat/completions`（OpenAI 兼容，凭证 `.env` 的 HERMES_API_URL/KEY），模型名 `hermes-agent`。
- **Hermes 是同步 agent：HTTP 响应返回 = 活干完了**。单仓库 ~3 分钟，7 仓库赛道 10-30 分钟。`--send` 放宽到 1800s；即使 HTTP 层超时，它后台仍会把活干完（实测确认），重新 `--status`/`--pull` 即可。
- Hermes 在容器内写图到 `/opt/data/reports/hermes_output/image_tasks/<track>/<owner>_<repo>/img_XX.png`；`/opt/data` 是 Docker 卷 `hermes_hermes-data`，宿主不能直读（Docker Desktop 卷在 WSL VM 里），**必须 docker cp**（`--pull` 已封装）。
- 任务包 JSON 含 track/article/out_dir/repos/status，状态机：`pending → dispatched`。
- 裸仓库名（标题式引用如 `## PCSX2（15958 星）`）经 GitHub search 解析为全名，缓存在 `<track>_namemap.json`。

## 当前状态（2026-11-01 完工）

5 个赛道全部交付，宿主 `reports/hermes_output/image_tasks/<track>/<owner>_<repo>/`：

| 赛道 | 仓库 | 图数（质检后） |
|---|---|---|
| emulator | 7/7 | 27 |
| game_streaming | 6/6 | 21 |
| self_hosted | 5/5 | 16 |
| win_tools | 4/4 | 15 |
| local_ai | 2/5 | 5（其余 3 仓库图在容器 work 区，待补拉） |

质检：Hermes 侧自带 doubao 视觉核对（vision_audit.json，game_streaming 21/21 全 UI），
宿主侧再跑 vision_auditor 终审。注意：终审时 API 偶发 403 限流会误杀图（microsoft_terminal
2 张已从容器恢复）；awesome-selfhosted 的 2 张 NoneType 异常为清单仓库无 UI 可截，属正常。

经验：单任务约 3-10 分钟；整赛道 >30 分钟会超 HTTP 窗口，**派发后不要等同步返回**，
用 --status/--poll 轮询容器内产物，归位即 --pull。会话空闲后派发的新任务会开新 turn。
