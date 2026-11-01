---
name: xhh-content-pipeline
description: 小黑盒内容流水线总 SOP：把"囤稿素材 → 草稿构建 → 风格自检 → 手机发布 → 喂巡检池 → 库存确认"六个环节串成一条带步骤的流水线。用户说"发个帖/写篇推文/看看囤稿/内容流水线"时加载本 skill 做总调度，具体环节跳转到对应专项 skill。
triggers:
- 发个帖
- 发篇推文
- 内容流水线
- 看看囤稿
- 发新帖
- 内容库存
- xhh pipeline
metadata:
  version: 1.0.0
  related_skills: [post-xiaoheihe, xhh-style-bible, host-automation]
---

# 小黑盒内容流水线总 SOP（xhh-content-pipeline）

本 skill 是**纯文档调度层**：不含脚本，只告诉你每一步用什么、在哪、怎么确认完成。
专项能力在两个下游 skill 里：`post-xiaoheihe`（机械操作）+ `xhh-style-bible`（文风把关）。

```
囤稿素材 ──→ 草稿构建 ──→ 风格自检 ──→ 手机发布 ──→ 喂巡检池 ──→ 库存确认
(stockpile)  (xhh_build)  (style-bible)  (人工)      (必做!)     (inventory)
```

---

## 第 1 步：盘点囤稿，挑一套

素材仓（两处）：
- `reports/hermes_output/stockpile_drafts/` — 结构化 article_blocks_*.json + 16:9 封面 png（主力仓，每套自带 README 说明赛道/字数/图数）
- `reports/stockpile_drafts/` — 早期 track_a_windows / track_b_local_ai 分轨稿

挑选判据：**优先最新鲜的赛道**（与最近已发主题不撞车）。挑定时读该目录 `README.md` 的分套表格。

> 环境前置：`post-xiaoheihe/.venv` 必须存在。没有就进该目录跑
> `python -m venv .venv && .venv\Scripts\pip install -r requirements.txt`（install.bat 有 GBK 编码坑，别用它）。

## 第 2 步：过风格关（写/改文案时必做）

读 `xhh-style-bible/SKILL.md` 主册，按赛道路由到对应 `references/track_*.md` 分册。
硬性红线：AI 味黑名单词汇一律替换；标题 ≤ 30 字（24~28 最佳，超了保存按钮直接禁用）。

## 第 3 步：构建草稿（post-xiaoheihe 全自动）

一切以 `post-xiaoheihe/SKILL.md` 的「标准流水线」为准，速查：

```bash
cd .agents/skills/post-xiaoheihe
.venv\Scripts\python.exe scripts\xhh_check.py        # ① 登录态，每次必跑
.venv\Scripts\python.exe scripts\xhh_build.py ^       # ② 一键构建+存草稿
    --title "标题(≤30字)" --article-json <blocks.json> ^
    --cover <cover_16_9.png> --plan-article --declare-ai --save-draft
.venv\Scripts\python.exe scripts\xhh_verify_draft.py  # ③ 抓包校验草稿内容
```

发布方式（唯一稳健路线）：**手机小黑盒 App 打开草稿箱 → 人工确认 → 发布**。
网页端直接点「发布」会被拦截，不要试。

## 第 4 步：发布后必做——喂巡检池（最容易忘的一步）

发布成功后，从小黑盒 App/网页拿到文章 link_id，追加进 `config/monitored_articles.json`：

```json
[
  {
    "link_id": "195154753",
    "title": "Win11 右键菜单恶心？6 个冷门小工具直接治",
    "added_at": "2026-10-27 20:14:13"
  }
]
```

`link_id` 取自文章 URL 中的数字段（如 `xiaoheihe.cn/p/195154753`）。
不喂池子的后果：`xhh_comments_sentinel`（10 分钟一轮的恶评巡检）盯不到这篇，新帖被带节奏无人知晓。

## 第 5 步：确认闭环

```bash
python tools/content_inventory.py    # 立即跑一次库存日报（正常也每日 86400s 自动跑）
curl -s "http://127.0.0.1:28987/status"   # 确认 sentinel 下次巡检倒计时正常
```

库存日报已推 TG 话题 5；看到「巡检池 N 篇在盯」数字 +1 即闭环完成。

---

## 故障速查

| 症状 | 处置 |
|---|---|
| `xhh_check.py` 报连不上 9223 | 先跑 `scripts/start_chrome.bat` 拉起带调试端口的 Chrome，再扫码登录 |
| 保存按钮禁用变红 | 标题超 30 字，砍标题 |
| 库存日报说"巡检池 0 篇"但你明明发过 | 第 4 步被跳过了，现在补 |
| `.venv` 报缺模块 | 见第 1 步环境前置，手动重建 venv |
