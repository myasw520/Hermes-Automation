# post-xiaoheihe —— 换电脑安装与首次跑通

这是「小黑盒图文/文章发布」skill 的**可移植版本**：脚本、依赖、配置全在一个目录里，
不依赖 social-auto-upload 仓库，换电脑拷过去就能装。

---

## 1. 安装（3 分钟）

前置：本机装好 **Google Chrome** 和 **Python 3.10+**（安装 Python 时勾选 "Add python.exe to PATH"）。

```
双击 install.bat
```

它会：创建 `.venv` → 用清华镜像装 `patchright` + `playwright` → 自检导入。

看到 `安装完成` 即可。

> 如果 Python 不在 PATH，命令行进这个目录手动跑：
> ```
> python -m venv .venv
> .venv\Scripts\python.exe -m pip install -r requirements.txt --index-url https://pypi.tuna.tsinghua.edu.cn/simple
> ```

**不需要** `playwright install` 下载浏览器——本套脚本全部连本机 Chrome。

---

## 2. 首次跑通（5 步）

### ① 拉起浏览器

```
双击 scripts\start_chrome.bat
```

会用本目录下的 `.chrome-profile` 拉起 Chrome（调试端口 9223）并打开 creator 后台。
**第一次是全新 profile，必须扫码登录。**

### ② 扫码登录

在打开的浏览器里：右上角「登录」→ 手机小黑盒 App 扫码。

> 会话存在 profile 里，下次不用重扫。但**小黑盒服务端会踢会话**，隔几天必失效，届时重扫一次。

### ③ 验登录态

```
双击 scripts\check.bat
```

期望看到 `✓ 已登录`。若显示 `✗ 未登录`，回第 ② 步。

### ④ 开一个空白编辑器

浏览器里点「发布内容 → 发布文章」，停在编辑器页面（URL 含 `/creator/editor/draft/`）。

### ⑤ 跑一篇

准备一个图片目录 + `items.json`，然后：

```
.venv\Scripts\python.exe scripts\xhh_build.py --layout caption ^
    --title "标题 20 字内" ^
    --items items.json --hashtags "#AI #程序员" ^
    --cover "封面.png" ^
    --plan-article ^
    --declare-ai ^
    --save-draft ^
    "D:\图片目录"
```

或者使用更精细的结构化区块模式（支持 `<h2>`/`<h3>` 分级标题与原生题注）：
```
.venv\Scripts\python.exe scripts\xhh_build.py ^
    --title "标题 20 字内" ^
    --article-json article_blocks.json ^
    --cover "封面.png" ^
    --plan-article ^
    --declare-ai ^
    --save-draft
```

看到 `[AUDIT PASS]`、`[✓] 封面上传与裁剪绑定完成！` 和 `[S] 已点击「保存草稿」` 就成了。
最后到**手机 App 草稿箱**确认并一键发布（网页点开草稿是空白，正常）。

---

## 3. 配置（一般不用改）

`config.json`：

| 字段 | 默认 | 说明 |
|---|---|---|
| `cdp_url` | `http://127.0.0.1:9223` | 调试端口。与 9222（抖音）错开，两个平台可同时开 |
| `chrome_path` | 空=自动探测 | 自动找 Program Files / (x86) / LocalAppData 下的 chrome.exe |
| `profile_dir` | 空=本目录 `.chrome-profile` | 登录态存在这里，别删 |

环境变量优先级更高：`XHH_CDP` / `XHH_CHROME` / `XHH_PROFILE`。

---

## 4. 脚本速查

| 脚本 | 干什么 |
|---|---|
| `install.bat` | 一键装依赖（建 .venv） |
| `scripts\start_chrome.bat` | 拉起带调试端口的 Chrome + 打开 creator |
| `scripts\check.bat` | 登录态 + 编辑器状态检查（**每次发之前先跑**） |
| `scripts\xhh_build.py` | ★ 长文一键构建：标题+导语+批量插图+图注+hover题注+话题+存草稿 |
| `scripts\xhh_fill_text.py` | 只填标题/正文（短图文用） |
| `scripts\xhh_verify_draft.py` | 存完草稿读接口验内容（`--expect N` 校验图数） |

所有 py 脚本都支持 `--help`。

---

## 5. 常见问题

**连不上 9223**
先跑 `start_chrome.bat`。若提示 profile 被占用，关掉所有用该 profile 的 Chrome 窗口再试。
另检查是否有杀软拦截 `--remote-debugging-port`。

**页面能打开但填表全失败**
100% 是登录态过期。跑 `check.bat`，看到「登录」按钮就扫码。**未登录也能打开后台框架**，别看页面正常就以为登好了。

**插图卡住 / 图数不对**
脚本会重试 3 次，仍失败会熔断并打印是哪一张。多半是图片太大或网络抖动，换图或重跑。**熔断是保护**：强行续写会导致后续图注整体错位。

**草稿箱点开是空白**
正常现象，编辑器不回填已存草稿。内容在接口里，用 `xhh_verify_draft.py` 验，或直接在手机 App 看。

**`xhh_verify_draft.py` 报接口没数据**
小黑盒可能改版了。用 `--raw` 看返回体，改脚本顶部的 `DRAFT_LIST_PATHS` / `DRAFT_INFO_PATHS`。

**必须升级 `playwright` 那行吗**
是的，`patchright` 不提供 `playwright` 模块，缺了会 `ModuleNotFoundError`。版本号可以随 patchright 一起升，但两个都要装。

---

## 6. 红线（别踩）

- 小黑盒**文章类型脚本点发布会失效**（跳转 image_text，不提交）。一律 `--save-draft` + 手机 App 发布。
- 每次开跑先验登录态，别假设会话还在。
- 脚本只在**空白编辑器**上工作，检测到已有内容会直接中止（退出码 2）——这是防写花老草稿的保护，不要绕过。
