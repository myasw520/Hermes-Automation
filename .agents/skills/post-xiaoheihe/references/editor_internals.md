# 小黑盒创作者后台与 ProseMirror 编辑器底层深度笔记

> 存放 ProseMirror DOM 结构、工具栏按钮选择器、组件底层逆向与排版技术细节。
> 日常发帖构建无需加载本文，排查 CDP 报错或修改自动化底层时按需查阅。

---

## 一、ProseMirror 排版与快捷键实测

编辑器是 ProseMirror，支持 Markdown 基础输入规则，但存在大量平台特异性：

| 格式 | 输入方式 | 产出 HTML | 状态 / 注意事项 |
|---|---|---|---|
| 一级标题 | `# 标题` | `<h2>` | ✅ 支持 |
| 二级标题 | `## 标题` | `<h3>` | ✅ 支持（⚠️ 只有一级/二级，`###` 不支持会原样留在正文） |
| 无序列表 | `- 项` 或 `* 项` | `<ul><li><p>` | ✅ 列表项按 Enter 会继续，退出需按两次 Enter |
| 有序列表 | `1. 项` | `<ol><li><p>` | ✅ |
| 引用块 | `> 内容` | `<blockquote><p>` | ✅ |
| 字体加粗 | 选中文字点工具栏 B | `<strong>`（存储序列化为 `<b>`） | ⚠️ **`Ctrl+B` 在 CDP 下不生效**，必须点击工具栏 `button[data-name="字体加粗"]` |
| 行内代码 | `` `code` `` | - | ❌ 不支持 |
| 分隔线 | `---` | - | ❌ 不支持 |

---

## 二、工具栏与附件组件实测定位表

正文未获焦点时按钮全部处于 `disabled` 状态，操作前必须先 `click` 正文：

| data-name | 功能 | 选择器 / 自动化细节 |
|---|---|---|
| `插入表情` | cube 表情面板 | 点击弹出 4 个分类 tab；正文直接打 `[cube_名]` 保存时会自动转译 |
| `插入图片` | filechooser 批量传 | 先点工具栏按钮，**待弹窗出现后再点弹窗内上传框 `.editor-image-wrapper__box.upload`** 才能触发 filechooser |
| `插入投票` | 投票弹窗 | `input[placeholder="请输入投票主题"]`，选项限15字，时长下拉框；生成 `special_type=7` |
| `插入游戏` | 游戏卡片 | `input[placeholder="搜索游戏"]`，插入 `DIV.article-editor-node.editor-card > .com-game-card`（内联跟着光标走） |
| `插入链接` | 蓝字链接 | ⚠️ URL **不会存进 text 字段**，只保留显示文本；故推荐中文句号法 |

---

## 三、图片原生题注输入规范

```html
<div class="article__image-desc-box">
  <input class="article__image-desc-input" placeholder="请输入图片描述">
</div>
```

- **必须用 `keyboard.type` 逐字输入**：直接 `.fill()` 不触发 React state 绑定，保存后变为空。
- **刚插入的图片题注框不可见**（图片处于选中态），需所有图插入完毕后再统一遍历 `nth(idx)` 填入。
- **不能使用 CSS `:last-of-type`**：图片块与 `<p>` 同级混合，会导致选择器超时。

---

## 四、防串位五重熔断机制

1. **前置计数核验**：插第 `i` 张前，断言编辑器图数严格等于 `i - 1`；
2. **缩略图完全加载**：检查 `complete && naturalWidth > 0`，避免未传完就点确定；
3. **入库增量轮询**：点「确定」后轮询等图数真正 `+1`（超时 10s）；未增量则 `Escape` 重试（最多 3 次）；
4. **主动硬熔断**：单图 3 次失败立即 `RuntimeError` 终止，不盲目续写；
5. **终局全量审计**：存草稿前强制 `final_imgs == len(images)`，不符拒绝保存。

---

## 五、接口签名与会话安全

- `/bbs/app/link/drafts` 和 `/bbs/app/link/edit/info` 必须携带动态签名参数（`hkey` 等），直接 fetch 返回 null。
- `xhh_verify_draft.py` 采用**搭页面原生请求便车**方案（监听页面的 `response` 事件）。
- 保存草稿后页面会自动跳到草稿箱；**在网页端点开已存草稿显示空白属正常编辑器机制**，校验内容一律看手机 App 或通过 verify 脚本。
