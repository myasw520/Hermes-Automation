# 调研：小黑盒帖子封面图自动生成方案

> research-scout @ 2026-10-31（所有 API 价格/协议/额度均为当日实抓核实，非凭记忆）


> **⚠️ 2026-10-31 用户拍板更新**：ZeroGate 网关不做生图 API，封面维持**手工 Gemini**（效果天花板、每帖几分钟，可接受）。
> 本报告的路线 B 降级为"可选备胎"：`tools/cover_generator.py` 的 GLM-Image 路（不依赖 ZeroGate）实测可用，
> 仅当某天想把封面环节自动化时再启用。
## 一句话结论

**做，且本周就能做完**：产线断点只有封面一个环节，而两条零/近零成本 API 路线（自家 ZeroGate 中转的 images 接口、智谱 GLM-Image 0.1 元/张原生 16:9）都是 OpenAI 兼容 POST，`keys_pool.json` 现成端点直接对接；手工 Gemini 不必长期维持。

---

## 零、先说一个调研中的意外发现（本机实测）

对自家 Tailscale 内网中转 ZeroGate（`http://100.114.18.45:7863/v1`，即 keys_pool 里的 `ZeroGate-ZCode`）做只读探测：

- 模型表 222 个模型中含多个**生图模型**：`gptgemini/gpt-image-2.5`、`gptgemini/grok-imagine-image`(-quality/-2.0)、`gptgemini/gpt-image-1.5`、`doubao/doubao/image` 等。
- 实际调用时上游返回 503，错误信息原文明示路由：`"model grok-imagine-image is only supported on **/v1/images/generations** and **/v1/images/edits**"`，同时报 `no_healthy_account`（上游账号全部冷却/禁用）。
- 管理面板标题 "ZeroGate 管理面板" 在用户自己手里。

**含义**：手工 Gemini 网页版的 API 化可能只差"把 ZeroGate 的生图上游账号池修活"。这是把现状自动化成本最低的路径，但账号池稳定性属于未验证项（见文末待确认）。

---

## 一、免费/低价生图 API 核查（2026-10-31 实抓）

| 候选 | 模型 | 免费额度 / 价格 | OpenAI 兼容协议 | 国内直连 | 时效与来源 |
|---|---|---|---|---|---|
| **智谱 BigModel（GLM-Image）** | glm-image | **0.1 元/张**；免费额度未核实到（旧 CogView-3-Flash 免费时代已结束，文档站已无 CogView 条目，被 GLM-Image 取代） | ✅ `POST /api/paas/v4/images/generations`，返回图片 URL；**keys_pool 已有该端点+key** | ✅ 本机 200 | [GLM-Image 模型页](https://docs.bigmodel.cn/cn/guide/models/image-generation/glm-image)、[图像生成 API 参考](https://docs.bigmodel.cn/api-reference/%E6%A8%A1%E5%9E%8B-api/%E5%9B%BE%E5%83%8F%E7%94%9F%E6%88%90)（实抓） |
| **Cloudflare Workers AI** | flux-1-schnell；备选 sdxl-lightning | **每天 10,000 Neurons 免费**（Free/Paid 计划同享，UTC 0 点重置）；flux-1-schnell 计价 4.80 N/tile + 9.60 N/step，1024px 4 步 ≈ 173 N → **免费层约 57 张/天** | ❌ 自有 `/ai/run/` REST（Bearer + JSON，返回 base64），需 ~30 行适配 | ✅ 本机触达（400=需 token） | [Workers AI 定价](https://developers.cloudflare.com/workers-ai/platform/pricing/)、[flux-1-schnell](https://developers.cloudflare.com/workers-ai/models/flux-1-schnell/)、[schema-input.json](https://developers.cloudflare.com/workers-ai/models/flux-1-schnell/schema-input.json)（实抓） |
| **阿里云百炼（通义万相）** | wanx-v1（V2 系价格另页未核） | **新账号 500 张免费**（90 天有效），之后 0.16 元/张 | ❌ DashScope 专有**异步** API（`X-DashScope-Async: enable` + 轮询 task），需 SDK/轮询代码 | ✅ | [万相文生图 API 参考](https://help.aliyun.com/zh/model-studio/text-to-image-api-reference)（实抓，仅 wanx-v1 部分） |
| **fal.ai** | FLUX.1 [schnell] | $0.003/百万像素（≈1024² 1 张 $0.003）；**页面未见免费额度**（仅 sandbox 试玩） | ❌ fal.run 队列 API，自有格式 | ✅ 本机触达 | [fal.ai flux/schnell](https://fal.ai/models/fal-ai/flux/schnell)（实抓） |
| **Replicate** | FLUX.1 schnell | **$3.00/千张**（$0.003/张）；页面未载明新账号免费额度 | ❌ Replicate predictions API | ✅ 本机 200 | [Replicate Pricing](https://replicate.com/pricing)（实抓） |
| **Together AI** | — | ⚠️ **定价页 2026 已无 FLUX.1-schnell 条目**（在售 FLUX.2 dev $0.0154/张等）；免费政策页面未载明——**"Together 有免费生图"的旧情报已过时，未核实到现行免费额度** | ❓（未深入，因免费通道不明确已降级） | 未测 | [together.ai/pricing](https://www.together.ai/pricing)（实抓） |
| **Groq** | — | ❌ **无生图模型**（仅视觉理解/OCR 输入），keys_pool 里的 Groq 与封面无关 | — | — | [console.groq.com/docs/models](https://console.groq.com/docs/models)（实抓） |
| **Gemini API 官方** | gemini-2.5/3.1-flash-image 等 | ❌ **免费层对生图模型 "Not available"**；付费 $0.0336–0.045/张（2.5 Flash Image 2027-03-15 停用） | ✅ 但无免费层 | ✅ 本机触达 | [ai.google.dev pricing](https://ai.google.dev/gemini-api/docs/pricing)（实抓） |
| **自家 ZeroGate 中转** | gpt-image-2.5 / grok-imagine 等 | 成本取决于 ZeroGate 账号池（现状 503 no_healthy_account） | ✅ **官方支持 `/v1/images/generations` `/v1/images/edits`**（错误信息明示） | ✅ 内网 | 本机实测 2026-10-31 |
| ChatAnywhere / DoCode（现有池） | — | ❌ 实查模型表 30/14 个，**均无生图模型** | — | — | 本机实测 2026-10-31 |

**关键发现 1：Cloudflare flux-1-schnell REST 版无宽高比参数。** 官方 input schema 只有 `prompt`（≤2048 字符）+ `steps`（≤8），无 size/aspect_ratio → REST 输出非 16:9，需后裁切；如要原生 16:9 需改用 `stable-diffusion-xl-lightning`（schema 实测支持 width/height 256–2048），但 SDXL 系美学与"轻日漫杂志风"差距大，且 Flux/SDXL 均不能可靠渲染中文字。

**关键发现 2：智谱 GLM-Image 几乎是为"杂志排版封面"定制的。** 官方推荐场景原文："商业海报……支持文字内容的精准嵌入与稳定呈现"、"社交媒体图文——适用于制作封面设计与版式结构较为复杂的社交媒体图文"；原生 16:9（推荐尺寸 1728x960，自定义 512–2048px 且为 32 倍数）；文字渲染开源 SOTA（LongText-Bench 中文 0.9788、CVTG-2K Word Accuracy 0.9116，官方页数据）。**即"图+大字标题"一张 prompt 直接出，绕过排版环节。**

---

## 二、GitHub 项目盘点（杂志排版封面自动生成）

结论先行：**没有"16:9 杂志风封面无人值守生成"的现成能打项目**；最接近的是归藏的 Agent Skill。

| 项目 | ★ | 最近更新 | License | 功能覆盖 | 差异点 / 可借鉴性 |
|---|---|---|---|---|---|
| 🟡 [op7418/guizang-social-card-skill](https://github.com/op7418/guizang-social-card-skill) | 7,873 | 2026-10-30（极活跃） | **AGPL-3.0** | 小红书 3:4 图文 + 公众号 21:9/1:1 封面对；Editorial（Monocle/Kinfolk 杂志风）+ Swiss 双视觉系统、28 版式骨架、10 主题；**单文件 HTML + Playwright 渲染出 PNG**（`node scripts/render.mjs`） | 形态是 Claude Code/Codex 交互式 Skill 非无人值守产线；**画板无 16:9**；AGPL 意味着直接改其代码集成需开源衍生（个人自用无法律风险，但注意）。**最大价值：证明 HTML+Playwright 路线能到很高审美水准，且版式/quiet-zone/字体规范可直接抄思路** |
| 🟡 [pixpark/picprose](https://github.com/pixpark/picprose) | 758 | 2026-08-11 | MIT | WYSIWYG 网页封面生成器（Medium/YouTube/BiliBili）：Unsplash 底图+标题/作者/字体排版+导出 | **手动 Web 工具**，无 API/产线接口，只适合当 UI 参考，不能直接进产线 |
| 🟡 [palxiao/poster-design](https://github.com/palxiao/poster-design) | 4,965 | 2026-09-10 | **AGPL-3.0** | 迅排设计：仿稿定的在线图片编辑器（Vue），海报/公众号封面 | 是"编辑器"不是"自动生成器"，太重；不适合 |
| 🟢 其他 | — | — | — | 小红书封面关键词下全是 0–8★ 玩具项目（如 Fmaverick/cover-generator 8★、azlll/xhs-cover-generator 0★）；og-image 系（satori 生态，vercel/satori 14,149★）只做"代码→SVG 文字卡"，无插画配图 | 无有效竞品 |

**DIY 路线工作量评估（HTML/CSS 模板 + AI 生底图 + Playwright 截字）**：
- 本项目 Playwright 已在产线使用（`tools/build_complete_draft_with_cover_v2.py` 上传封面即 Playwright 流程），**基建零新增**。
- 从零写一套 16:9 杂志风模板：HTML+CSS + 字体选型 + Playwright 截图脚本，约 **2–4 小时/套**（有 guizang 的版式规范可抄时取下限）。
- 但若采用 GLM-Image（文字渲染 SOTA），排版环节可能整个省掉——先测 GLM-Image 的真实出字质量再决定要不要 HTML 层。

---

## 三、三条路线结论与推荐

| 路线 | 效果预期 | 工作量 | 月成本* | 判定 |
|---|---|---|---|---|
| **A. 手工 Gemini 网页版（现状）** | 效果天花板（已验证） | 0 | 0 元 + **每帖 5–10 分钟手工**，是产线唯一人工断点 | 不推荐长期维持：Gemini API 免费层无生图（$0.0336–0.045/张），网页版无法脚本化；手工环节与"无人值守产线"目标直接冲突 |
| **B. 免费生图 API 进产线** | 分层：ZeroGate 修活 ≈ 手工 Gemini；GLM-Image 接近（原生 16:9+中文字渲染是官方主打）；CF flux-schnell 可当备胎（需裁切+无中文字） | **~1 小时**：写一个 ~50 行 `cover_generator.py`（见下） | **0–6 元/月**（按 60 帖/月：全 GLM-Image ≈ 6 元；ZeroGate 稳定则 0） | ✅ **推荐，本周实施** |
| **C. HTML 模板 + Playwright 排版** | 大字标题精准可控（AI 生图文字不可控时这是解法）；审美上限取决于模板设计功力 | 2–4 小时/套模板 + 底图来源仍需 B | 0 元（底图走 CF 免费层或 GLM-Image） | 🔶 **作为 B 的可选增强**，而非独立路线：先用 GLM-Image 直接出完整封面，仅当中文字/排版不满意时再加 HTML 压字层 |

*按每天 2 帖、月 60 帖估算。

### 推荐实施路径（两步走）

**第一步（本周，约 1 小时）——B：双端点 fallback 的 `tools/cover_generator.py`**
1. 优先调 ZeroGate：`POST http://100.114.18.45:7863/v1/images/generations`，model `gptgemini/gpt-image-2.5`，OpenAI images 协议，keys_pool 现成 → **先在 ZeroGate 管理面板把生图上游账号池修活**（当前 503 no_healthy_account）。
2. 失败则 fallback 智谱：`POST https://open.bigmodel.cn/api/paas/v4/images/generations`，model `glm-image`，size `1728x960`，Bearer 用 keys_pool 里 ZCode-BigModel 的 key（注意其响应返回图片 URL 需再下载，非 b64）。
3. 产出直接落到 `COVER_PATH`（`build_complete_draft_with_cover_v2.py` 已引用的 `小黑盒封面_轻杂志漫风_推荐.png` 路径），发布环节零改动；可选在入库前过一遍现有 `tools/vision_auditor.py` 质检。

**第二步（可选）——若对排版/中文字不满意再加 C 层**：GLM-Image 改为只生"无字底图"，本地 HTML 16:9 模板压大字标题 + Playwright 截图，兼得生图美学与排版控制（版式规范参考 guizang-skill 的 Editorial 骨架，但建议重写而非复制其 AGPL 代码）。

### 为什么没人把这件事做成现成工具（绿档自检）
封面自动生成的真正难点不在生图，而在"审美模板 + 渠道规格适配 + 文字排版"三者的组合，它高度依赖各人内容调性（小黑盒 16:9 vs 小红书 3:4 需求不同），开源社区自然碎片化；且 2026 年"认知型生图"模型（GLM-Image/Nano Banana 系）才把"中文字稳定渲染"做到可用——时机刚到，值得直接用 API 吃掉排版环节。

---

## 四、撞车判定

| 对象 | 档位 | 依据 |
|---|---|---|
| guizang-social-card-skill | 🟡 部分重合 | 图文卡片生成思路重合，但画板无 16:9、形态为交互式 Skill 非产线组件、AGPL；借鉴而非照搬 |
| picprose | 🟢 无有效竞品 | 手动 Web 工具，无自动化接口 |
| poster-design | 🟢 无有效竞品 | 编辑器形态，非自动生成 |
| 各类 xhs-cover-generator（≤8★） | 🟢 无有效竞品 | 玩具/废弃级 |

## 五、待确认（需人工判断或后续验证）

1. **ZeroGate 生图上游**：账号池能否修活、`gpt-image-2.5` 实际是哪家模型（名称含 gptgemini 但未验证真实后端）、出图质量是否接近网页版 Gemini——需在管理面板操作后实测，本次调研因 503 无法出样图。
2. **智谱 GLM-Image 实测样张**：0.1 元/张已在定价页核实，但"轻日漫杂志风"风格遵循度未出图验证（需充少量金额实测 3–5 张；体验中心 https://bigmodel.cn/trialcenter/modeltrial/image 可免费试）。
3. **智谱是否有现行免费额度**（如新用户赠费）：文档站未载明，未获取。
4. Together AI 免费通道、阿里云 wan2.x 系价格：本次降级未深查，如需可补。
5. 小黑盒对 AI 生成封面的社区观感/规则：项目已有"AI 声明"环节（发布脚本 `build_complete_draft_with_cover_v2.py` 中有 AI declaration 步骤），封面是否需声明未查证，建议沿用现有一致策略。
