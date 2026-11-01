# Hermes-Automation 工具脚本清理审计报告（AUDIT-tools-cleanup）

> 生成日期：2026-10-31 ｜ 审计范围：`tools/`（259 个 .py + 5 个 .ps1）、`services/`、项目根目录散落文件
> 项目无 git 历史，分类依据：`daemon_scheduler.py` 源码引用、4 个 SKILL.md 引用、全量 import/subprocess 交叉引用扫描（grep 全仓 .py/.md/.vbs/.bat/.ps1）、文件 mtime、产出目录证据（`reports/`、`data/`、`config/`）。
> 抽查复核：父代理已对调度任务行号、传递依赖 import、保留清单文件存在性做二次核验，结论一致。

## 一、调度依赖清单（必须保留 — 直接引用）

来源：`services/daemon_scheduler.py` 的 `TASKS` 字典：

| 行号 | 任务 key | 被引用脚本 |
|---|---|---|
| L59 | weekly_github | `tools/weekly_github_digest.py` |
| L65 / L71 | freegames / bili_intel | `tools/cn_intel_search.py` |
| L77 | wool_radar | `services/wool_radar.py` |
| L83 | welfare_harvester | `tools/batch_welfare_harvester.py` |
| L89 | daily_checkin | `tools/daily_wool_checkin.py` |
| L95 | postgrad_papers | `tools/postgrad_exam_papers_harvester.py` |
| L101 | build_print_papers | `tools/fetch_official_full_pdf_papers.py` |
| L107 | xhh_comments_sentinel | `tools/xhh_comment_sentinel.py` |

启动器：`services/run_daemon_silent.vbs`（pythonw 拉起 daemon，保留）。运行状态：`config/scheduler_state.json`、`config/keys_pool.json`（scheduler.log 显示 2026-10-31 凌晨仍在运行，全部任务活跃）。

### 传递依赖（被调度脚本 import/subprocess，连锁保留）

| 被依赖脚本 | 引用方（源码行） |
|---|---|
| `tools/chatanywhere_harvester.py` | batch_welfare_harvester.py L63 `from chatanywhere_harvester import main` |
| `tools/docode_harvester.py` | batch_welfare_harvester.py L72-73 subprocess |
| `tools/harvest_github_apis.py` | chatanywhere_harvester.py L19（`save_to_pool`） |
| `tools/tg_notify.py` | harvest_github_apis.py L6 |
| `services/mail_receiver.py` | chatanywhere_harvester.py L17（IMAP 接码） |
| `services/wool_radar.py` | 另被 cn_intel_search L10、weekly_github_digest L16、docode_harvester L8 等 10+ 脚本 import（Telegram 推送公共库） |

**调度必需合计：tools/ 11 个 + services/ 2 个（+ run_daemon_silent.vbs）。**

## 二、Skill 依赖清单（必须保留）

| Skill | 引用的脚本 | 结论 |
|---|---|---|
| host-automation | SKILL.md L67 `python tools/niche_gem_harvester.py`；L69 `python tools/vision_auditor.py`；其余通过 daemon API 触发（即第一节 8 个任务脚本） | `tools/niche_gem_harvester.py`、`tools/vision_auditor.py` 保留 |
| post-xiaoheihe | 使用 skill 自带 `scripts/xhh_check.py、xhh_build.py、xhh_fill_text.py、xhh_verify_draft.py、xhh_common.py、start_chrome.py/.bat、check.bat`（位于 `.agents/skills/post-xiaoheihe/scripts/`，不在 tools/ 内） | skill 自带脚本不受本次清理影响；tools/ 下大量脚本 import 其 `xhh_common`，方向是 tools→skill，不构成 tools 的保留理由 |
| xhh-style-bible | 仅引用自身 `references/track_*.md` 与 `corpus/` | 无脚本依赖 |
| windows-batch-powershell | 无脚本依赖（纯规范文档） | 无 |

另：`reports/hermes_output/stockpile_drafts/README.md` L100 提及 `tools/niche_gem_harvester.py`、`tools/vision_auditor.py`（佐证保留）；该 README 还提到 `tools/build_articles.py`、`tools/compress_images.py`、`tools/verify_drafts.py` —— **这三个文件在仓库中不存在，属悬空引用，无需保留**。

## 三、全量分类表

保留共 36 个 tools/*.py + 3 个 .ps1 + services 全部运行件；可清理 223 个 tools/*.py + 2 个 .ps1。逐组如下（每组一行说明覆盖全部组员）：

### 3.1 调度必需（11 py）
见第一节 8 个直接 + 4 个传递（chatanywhere_harvester / docode_harvester / harvest_github_apis / tg_notify）。

### 3.2 Skill 引用（2 py）
`niche_gem_harvester.py`（低星神器挖掘+截图采集，输出 stockpile 素材）、`vision_auditor.py`（多模态视觉质检，被 harvester 与 stockpile 管线调用）。

### 3.3 活跃产出类（19 py，未入调度但是内容生产线/活跃工具）
| 脚本 | 说明 |
|---|---|
| ai_paper_deep_diver.py | AI 论文精读库 → data/github_gems/deep_dive |
| github_gem_scout.py | 百星仓库雷达 → reports/github_gems + data/github_gems |
| github_gem_code_analyzer.py | 仓库源码深析 → deep_dive 配套 |
| niche_tool_radar.py | 冷门工具雷达 → reports/niche_tools |
| niche_web_navigator.py | 冷门站点导航库 → data/niche_web_vault |
| practical_tool_scout.py | 实用工具雷达+推文 → reports/practical_tools |
| xiaoheihe_intel_harvester.py | 小黑盒游戏推文生成 → reports/xiaoheihe_articles |
| daily_ai_trending_harvester.py | 每日 AI 热点 → reports/ai_daily_posts |
| cs408_universe_generator.py / cs408_vault_builder.py | 408 题库引擎 → data/cs408_universe、cs408_vault |
| generate_master_408_graph_and_vault.py | 408 知识图谱 → reports/master_408_graph_data.json（cs408-dashboard 数据源） |
| build_desktop_408_exam_papers.py | 桌面打印试卷生成（打印链路，需人工确认去留） |
| build_stockpile_drafts.py | 屯稿生成器，niche_gem_harvester 的下游管线 |
| setup_obsidian_vault.py | Obsidian 知识库构建 → data/ai_learning_vault |
| hermes_terminal_assistant.py | 交互式考研终端助手（挂 keys_pool） |
| sync_standalone_report.py / update_dashboard_graph.py | cs408-dashboard 数据/图谱维护 |
| oneapi_harvester.py | One-API 通用收割模板（README「核心固化模块」；仅被一次性 test_oneapi_live import，归档级保留） |
| hermes_xhs_collector.py | XHS 214 条样本采集引擎（任务已交付停用，daemon L111 注释佐证；建议归档） |

### 3.4 重复版本组-应保留（4 py）
`build_perfect_draft_v7.py`、`build_complete_draft_with_cover_v2.py`、`fetch_tool_screenshots.py`、`expand_all_vault_notes.py`（演化链见第四节）。

### 3.5 一次性实验/一次性已完成（214 py，全部可清理）
按攻击/实验线分组（每行说明同一）：

1. **小黑盒编辑器调试与长文发布实验（66，Oct 25-26）**：apply_scheme1_cover、automate_publish_settings、build_15_tools_mega_draft、build_and_log_mega、build_complete_draft_with_cover(v1)、build_perfect_draft(v1~v6)、build_sweet_spot_draft、check_ai_decl、check_api_cover_details、check_auto_save_status、check_content_decl、check_cover_and_decl、check_decl_options、check_draft_state、check_disabled_reason、check_save_btn、check_w_value、clean_and_refine_images、clean_test_draft、click_bottom_left_save、create_cover、create_v2_covers、dump_current_draft、finish_draft_settings、finish_save_15_tools、finish_save_page0、generate_all_covers_and_rebuild、inspect_cover_modal、inspect_editor、inspect_editor_dom、inspect_editor_toolbar、inspect_form_thumb、inspect_mask、inspect_mask_upload、inspect_settings_drawer、open_article_editor、prepare_draft1_assets、print_drawer、push_15_tools_mega、repush_clean_drafts、run_sweet_spot_push、save_current_draft、save_draft_now、scroll_drawer、select_ai、test_click_plan、test_cover_modal、test_draft_save_flow、test_editor_heading、test_emoji、test_head_click、test_image_input、test_live_mega_push、test_paste_interleaved、test_save_network、test_select_ai、test_topic_popup、test_topic_search、test_topic_type、test_upload_cover、verify_summary —— 全部为单篇文章的迭代构建/CDP 调试，成品已发布或废弃，且 post-xiaoheihe skill 已固化等价能力（xhh_build.py）。
2. **ChatAnywhere/OneAPI 注册与 OAuth 调试（48，Oct 20）**：auto_claim_real_live、bind_github、bind_popup、check_apikeys、check_apikeys_bound、check_btn、check_console、check_direct_register、check_gh_emails、check_popup、check_tabs、claim_chatanywhere、complete_oauth、create_github_repo、create_key、create_new_token、create_public_repo、do_bind_gh、dump_captcha、dump_elements、dump_form、dump_form2、dump_hrefs、dump_modal、find_captcha_type、fork_repo、get_api_resp、get_captcha_src、get_token_api、harvest_after_login、inspect_reg、inspect_reg_form、list_buttons、list_inputs、reveal_key、set_gh_email、solve_captcha_live、stealth_test、submit_real_code、test_anonymous、test_captcha、test_copy_key、test_gh_oauth、test_no_login、test_oauth、test_oauth_api_body、test_real_reg、test_submit、trace_oauth —— 成功路径已固化进 chatanywhere_harvester.py。
3. **DoCode 登录调试（13，Oct 21）**：do_login_extract_docode、extract_docode_key、extract_token_now、finish_docode_login、inspect_console、inspect_token_page、push_docode_telegram、read_reset_email、test_click_reset、test_docode_harvest、test_login_api、test_qq_docode、test_reset —— 成功路径已固化进 docode_harvester.py。
4. **第三方中转站批量探测（47，Oct 21）**：AgentRouter/AnyRouter/FlushAPI/KKToken/JustDoWork/CodexRelay/NoFX/Nianhua/HappyCode/VSLLM/X 全家桶：debug_anyrouter_popup、debug_oauth_net、harvest_agentrouter、harvest_flushapi、harvest_flushapi_complete、harvest_from_x、inspect_anyrouter、inspect_codexrelay、inspect_flushapi、inspect_gh_oauth_buttons、inspect_justdowork、inspect_kktoken、inspect_popup_network、inspect_popup_text、inspect_vsllm、probe_new_batch、probe_sites、search_x、test_agentrouter_flow、test_agentrouter_retry、test_ar_reg_oauth、test_anyrouter_auth_fixed、test_anyrouter_oauth、test_anyrouter_send_code、test_anyrouter_user_reg、test_clean_ar、test_click_dontcore、test_codexrelay_email、test_correct_auth、test_flush_direct、test_flush_gh、test_flushapi_github、test_flushapi_reg、test_flushapi_submit、test_happycode_reg、test_justdowork_gh、test_justdowork_login、test_kktoken_gh、test_kktoken_inspect、test_kktoken_reg、test_nianhua_btn、test_nianhua_send_actual、test_nianhua_send_code、test_nofx_gh、test_popup_detail、test_typing_cb、check_popup —— 战果截图均在 reports/（harvest_AgentRouter.png 等），站点多数已死或未常态化。
5. **B站/小黑盒早期探测（6）**：test_bili、test_bili_playwright、test_xhs_playwright、test_xhs_stealth、test_xiaoheihe、test_xiaoheihe_pw。
6. **XHS 采集调试（12）**：debug_xhs、extract_via_context、open_for_real_scan、open_for_scan、probe_xhs_ip、read_profile_cookies、test_capture_qr、test_feed、test_pure_api_search、test_xhs_explore_detail、try_decrypt_chrome、verify_xhs_login。
7. **Obsidian 下载实验（8）**：download_direct、download_direct_azure、download_install_obsidian、download_obsidian、download_obsidian_blocks、download_obsidian_resumable、make_shortcut、test_mirror（Obsidian 已装好，download_install_obsidian 可人工确认后归档备用）。
8. **考研情报一次性采集（12）**：cs_college_intel_gatherer、cs_jiangzhehu_major_gatherer、cs_postgrad_intel_gatherer、expand_obsidian_notes、generate_math_english_intel、inject_matheng_tab、investigate_22_vs_11_scores、investigate_blacklist_pitfalls、investigate_shuangfei_reexam、push_blacklist_tg、push_date_miniapp_tg、update_html_filters（对应 reports/ 下 CS_* 报告已交付）。
9. **系统/Clash 调试（3）**：check_clash_nodes、inspect_clash_nodes、clean_sessions。
10. **工具截图杂项（4）**：download_tool_screenshots、fix_twinkle_tray_image、inspect_quicklook、update_collection_images。
11. **其他一次性（4）**：cheapcodex_harvester（$20 首日收割已完成）、test_oneapi_live、test_vision_audit（vision_auditor 本体保留）、package_skills（已产出 xiaoheihe_skills_bundle.zip）。

### 3.6 PowerShell（5 个）
保留：show_status.ps1、enable_lan_access.ps1、clean_hosts.ps1（系统维护工具）。可清理：auto_install_obsidian.ps1、create_shortcut.ps1（一次性已完成，建议归档）。

## 四、重复版本组专项

| 组 | 演化链（按 mtime） | 应保留 | 应废弃 |
|---|---|---|---|
| build_perfect_draft | v1(14:09)→v2(14:16)→v3(14:33)→v4(14:37)→v5(14:41)→v6(14:47)→v7(14:50)，同一篇 LocalSend 等 3 工具长文的排版/封面/勾选迭代 | **v7**（最新，ARTICLE_BLOCKS 终版结构） | v1~v6 |
| build_complete_draft_with_cover | v1(16:51)→v2(16:56)，v2 加封面路径与最终勾选 | **v2** | v1 |
| 工具截图抓取 | download_tool_screenshots(10/24)→fetch_tool_screenshots(10/25) | **fetch_tool_screenshots.py** | download_tool_screenshots.py |
| Obsidian 笔记扩写 | expand_obsidian_notes(15:52)→expand_all_vault_notes(15:53，全库版) | **expand_all_vault_notes.py** | expand_obsidian_notes.py |
| dump_form | dump_form→dump_form2 | 两者均为一次性 DOM dump | 两者均可清 |
| harvest_flushapi | harvest_flushapi→harvest_flushapi_complete | 均一次性（站点已死） | 均可清（归档级） |
| open_for_scan | open_for_scan→open_for_real_scan | 均一次性 | 均可清 |
| waifu 封面（根目录） | make_waifu_cover→make_user_waifu_covers→render_clean_cover/apply_deep_blue_cover→**make_perfect_waifu_cover**（最终版） | make_perfect_waifu_cover.py（若需重跑） | 其余 4 个 |
| 15 工具大长文 | build_15_tools_mega_draft→push_15_tools_mega→finish_save_15_tools / build_and_log_mega | 已发布完成，全组一次性 | 全组 |

## 五、「可安全清理」最终清单

### A 级 — 安全删除（无引用、无唯一产出、纯调试，约 176 个 tools/*.py）
上表 3.5 中第 1 组的纯调试部分（check_*/dump_*/inspect_*/test_* 全部 40+）、第 2 组全部 48、第 3 组全部 13、第 4 组 47、第 5 组全部 6、第 6 组全部 12、第 9 组全部 3、第 10 组 4（download_tool_screenshots、fix_twinkle_tray_image、inspect_quicklook、update_collection_images）、第 11 组 2（test_oneapi_live、test_vision_audit）。

### B 级 — 建议归档（有唯一成功产出/代表已交付工程，约 47 个）
- tools：build_perfect_draft v1~v6、build_complete_draft_with_cover v1、build_15_tools_mega_draft、build_and_log_mega、push_15_tools_mega、finish_save_15_tools、finish_save_page0、build_sweet_spot_draft、run_sweet_spot_push、generate_all_covers_and_rebuild、repush_clean_drafts、clean_and_refine_images、create_cover、create_v2_covers、apply_scheme1_cover、automate_publish_settings、prepare_draft1_assets、save_draft_now、save_current_draft、click_bottom_left_save、clean_test_draft、open_article_editor、verify_summary、cs_college_intel_gatherer、cs_jiangzhehu_major_gatherer、cs_postgrad_intel_gatherer、generate_math_english_intel、inject_matheng_tab、investigate_22_vs_11_scores、investigate_blacklist_pitfalls、investigate_shuangfei_reexam、push_blacklist_tg、push_date_miniapp_tg、update_html_filters、expand_obsidian_notes、download_direct*、download_obsidian*、make_shortcut、test_mirror、cheapcodex_harvester、harvest_agentrouter、harvest_flushapi(_complete)、harvest_from_x、search_x、package_skills、auto_install_obsidian.ps1、create_shortcut.ps1
- 根目录：make_waifu_cover.py、make_user_waifu_covers.py、render_clean_cover.py、apply_deep_blue_cover.py、generate_xhh_article_WAIFU.py、dump_waifu.py、inspect_waifu.py、waifu_text.txt、小黑盒封面_二次元美少女_VOL01.png、小黑盒封面_纯壁纸流.png、xhs_viral_notes_dataset_delivery.zip（交付物）、xiaoheihe_skills_bundle.zip（可由 package_skills.py 重生成）

### C 级 — 需人工确认（8 个）
| 文件 | 理由 |
|---|---|
| tools/build_perfect_draft_v7.py | 重复组最终版，但内容是单篇已发文章的硬编码；确认不再复用排版后可归档 |
| tools/build_complete_draft_with_cover_v2.py | 同上（引用根目录 轻杂志漫风 封面） |
| tools/build_desktop_408_exam_papers.py | 桌面打印试卷链路，未入调度但与 build_print_papers 任务同域 |
| tools/oneapi_harvester.py | README 列为核心固化模块，仅被一次性脚本 import |
| tools/download_install_obsidian.py | 换机重装 Obsidian 时可复用 |
| tools/expand_all_vault_notes.py | Obsidian 库再扩写时可用 |
| tools/hermes_xhs_collector.py | 214 条样本已交付、任务停用，但为数据集唯一采集引擎 |
| 根目录 make_perfect_waifu_cover.py + 小黑盒封面_轻杂志漫风_推荐.png | waifu 封面最终版 / v2 构建脚本引用的封面图 |

### 根目录直接安全删除（无任何引用）
PNG 中间产物 12 个：after_confirm_cover.png、after_corner_click.png、after_file_set.png、bubble_crop.png、bubble_gen_crop.png、bubble_text_test.png、clean_base.png、clean_character.png、cleaned_bubble_test.png、hair_adjusted_test.png、temp_chk.jpg、tmp_ex.jpg；HTML 2 个：sidebar_dump.html、draft_194948470_full.html（后者仅被一次性 verify_summary.py 引用）；脚本 5 个：test_click_cover.py、test_confirm_cover.py、test_cover_dom.py、test_cover_upload.py、list_desktop.py。services/probe_screenshot.png 亦为 debris，可删。

**保留勿动**：.env、config/ 全部、data/ 全部、reports/ 的成品报告与截图归档、cs408-dashboard/ 全部、.agents/skills/ 全部、README.md。

## 六、根目录散落文件处置汇总

| 类别 | 数量 | 处置 |
|---|---|---|
| 一次性实验脚本 | 13 个 .py | 5 个直接删（test_*_cover/list_desktop），8 个归档（waifu 系列最终版 + 文章生成器） |
| 调试截图 PNG/JPG | 15 个 | 12 个直接删，3 个「小黑盒封面_*.png」归档（其中 轻杂志漫风_推荐 被 v2 脚本引用） |
| HTML dump | 2 个 | 直接删 |
| TXT | 1 个（waifu_text.txt） | 归档 |
| ZIP | 2 个 | 归档（数据集交付物 / skill 分发包） |
| 配置与文档 | .env/.gitignore/README.md | 保留 |

## 七、统计

- tools/：**259 个 .py 中保留 36 个、可清理 223 个**（安全删除约 176、建议归档约 47）；5 个 .ps1 保留 3、归档 2。
- services/：全部保留（daemon_scheduler、wool_radar、mail_receiver、run_daemon_silent.vbs、pushed_history.json），仅 probe_screenshot.png 可删。
- 根目录：可清理/归档 33 个文件（13 脚本 + 15 图 + 2 HTML + 1 TXT + 2 ZIP），保留 .env/.gitignore/README.md。
- 合计可清理对象约 **260 个文件**（安全删除 ~205、建议归档 ~52、需人工确认 ~8）。
