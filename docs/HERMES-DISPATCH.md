# HERMES-DISPATCH.md — 派发器编辑者契约（给未来改脚本的 AI / 人）

> 2026-11-01 ｜ 读者：任何要修改 `tools/dispatch_to_hermes.py` 的 AI 会话或人。
> 改代码前**先读完本文**，坑都标好了坐标。

## 一、这个脚本是什么（一句话）

ZCode（宿主 CLI）与 Hermes（Docker agent，`nousresearch/hermes-agent`，OpenAI 兼容网关 :8642）之间的**采图任务派发与验收管理器**。职责边界是用户拍板的：**ZCode 只管理（提取清单/派发/拉回/质检），绝不自己采图**。

## 二、五个子命令与数据流

```
track_*.md 稿件
   │ --scan    （正则提取 仓库/星数，裸名走 GitHub search 解析 -> <track>_namemap.json 缓存）
   ▼
reports/hermes_output/image_tasks/<track>_task.json   ← 任务包（状态机: pending → dispatched）
   │ --send    （POST Hermes :8642/v1/chat/completions，模型名 hermes-agent）
   ▼
容器内 /opt/data/reports/hermes_output/image_tasks/<track>/<owner>_<repo>/img_XX.png
   │ --pull    （docker cp hermes:/opt/data/... → 宿主同相对路径）
   ▼
宿主 reports/hermes_output/image_tasks/<track>/...
   │ --audit   （tools/vision_auditor.py 终审：非 UI 图直接删）
   │ --status  （每赛道 "回图 N/M 仓库"）
```

## 三、改代码前必须知道的坑（按代价排序）

1. **Hermes 是同步 agent：HTTP 响应返回 = 活干完**。单仓库 3-10 分钟，整赛道 30 分钟+。`--send` 的超时是 1800s，且超时 ≠ 失败——HTTP 断开后 Hermes 往往继续把活干完。**不要把超时改成"快速失败重试"**，那会重复派发同一个任务（Hermes 会开新 turn 再干一遍，浪费 25 亿 token 池）。
2. **两个路径体系**：宿主 `reports/hermes_output/image_tasks/...` ↔ 容器 `/opt/data/reports/hermes_output/image_tasks/...`。`--pull` 依赖这层映射（`HERMES_DATA_IN_CONTAINER = "/opt/data"`）。若改 compose 卷映射，这里必须同步。
3. **任务包里 repos 是 dict 列表**（`{"repo": ..., "stars": ..., "bare": 可选}`）——不是字符串。`cmd_status` 曾因把它当字符串 `.replace()` 崩过（已修）。新增遍历代码时先 `isinstance(repo, dict)`。
4. **提取器三种模式别动顺序**：模式1 数字星数（`repo（42824 星）`）、模式2 中文万星（`repo，33 万星`）、模式3 标题裸名（`## PCSX2（15958 星，C++）`）。模式3 产出的条目带 `"bare": True`，靠 `_load_namemap()` 用 GitHub search 转全名；解析失败的 bare 条目会被剔除。**裸名解析结果缓存在 `<track>_namemap.json`，改了解析逻辑要手动删缓存才会重跑**。
5. **`--audit` 会真删图**。vision_auditor 调 LLM 视觉 API，偶发 403 限流会把好图误判成"API调用失败"并删除。误杀了从容器 `docker cp` 恢复即可（容器内原图还在）。若要改 audit，先加 `--dry-run`。
6. **Hermes 侧沙箱**：docker-compose.yml 里 `HERMES_YOLO_MODE=1`（用户 2026-10-31 授权，专供采图任务）。若它被关掉，Hermes 的 terminal/execute_code 会被 BLOCKED，表现为日志满屏 BLOCKED 且 30 分钟只出 1 张图。
7. **凭证来源**：`HERMES_API_URL/KEY` 从 `services/config_lib.py` → 项目根 `.env` 读。不要硬编码，不要新造密钥文件。

## 四、验收一组新图的标准动作

```bash
python -I tools/dispatch_to_hermes.py --pull     # 容器 → 宿主
python -I tools/dispatch_to_hermes.py --audit    # 质检（会删劣图）
python -I tools/dispatch_to_hermes.py --status   # 回图 N/M 仓库
```
成品路径即发帖配图路径：`reports/hermes_output/image_tasks/<track>/<owner>_<repo>/`。

## 五、已知尾巴

- local_ai 赛道 3 个仓库（llamafile / local-deep-research / dograh）图未归位（agent turn 提前收尾，素材在其 work 区）——补派一次单赛道任务即可，参考 `docs/HERMES-IMAGE-WORKFLOW.md`。
- Hermes 超出任务书的自发行为（补拍真机截图、扩展挖掘 `work/treasure/`）是**特性不是 bug**，别在 prompt 里禁止它。
