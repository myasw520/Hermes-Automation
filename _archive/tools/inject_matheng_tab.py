import re

dashboard_path = r"C:\Users\zzx05\Hermes-Automation\reports\CS408_Visual_Dashboard.html"

with open(dashboard_path, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Add Nav Item
old_nav = """            <div class="nav-item" onclick="switchTab('templates')">
                <svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path d="M16 18l6-6-6-6M8 6l-6 6 6 6"/></svg>
                高频代码与PV模板
            </div>"""

new_nav = """            <div class="nav-item" onclick="switchTab('matheng')">
                <svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z"/></svg>
                📐 公共课考纲(11vs22)
            </div>
            <div class="nav-item" onclick="switchTab('templates')">
                <svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path d="M16 18l6-6-6-6M8 6l-6 6 6 6"/></svg>
                高频代码与PV模板
            </div>"""

if old_nav in html:
    html = html.replace(old_nav, new_nav)
else:
    print("Warning: old_nav not found!")

# 2. Add the view panel HTML
matheng_panel_html = """
        <!-- 5. Math & English Syllabus View (NEW!) -->
        <div id="matheng-view" class="view-panel" style="flex-direction:column; padding:25px 30px; gap:20px; width:100%;">
            <!-- Decision Banner -->
            <div style="background:linear-gradient(135deg, rgba(59,130,246,0.15), rgba(139,92,246,0.15)); border:1px solid rgba(59,130,246,0.3); border-radius:12px; padding:20px; display:flex; flex-direction:column; gap:12px;">
                <div style="font-size:1.05rem; font-weight:700; color:#93c5fd; display:flex; justify-content:space-between; align-items:center;">
                    <span>⚖️ 计算机考研公共课抉择：选“11 (数一+英一)” 还是 “22 (数二+英二)”？</span>
                    <span style="font-size:0.75rem; background:rgba(59,130,246,0.25); color:#bfdbfe; padding:2px 8px; border-radius:4px;">官方大纲对齐</span>
                </div>
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:15px; font-size:0.82rem; line-height:1.6;">
                    <div style="background:rgba(15,23,42,0.6); padding:14px; border-radius:8px; border:1px solid rgba(255,255,255,0.06);">
                        <strong style="color:#f87171; font-size:0.9rem; display:block; margin-bottom:6px;">方案 A：选考“11 (数一 + 英一)” —— 适合学硕/直博</strong>
                        <ul style="padding-left:18px; color:#cbd5e1;">
                            <li><strong>考查范围</strong>：高数(56%) + 线代(22%) + 概率论(22%)。全大纲覆盖，含三重积分、曲线曲面积分、无穷级数。</li>
                            <li><strong>复习工作量</strong>：约为数二英二的 <strong>1.6 ~ 1.8 倍</strong>，需投入极多时间死磕高数生僻章节。</li>
                            <li><strong>调剂优势</strong>：<strong>高调低霸权</strong>。初试考数一英一者，调剂时可单向申请要求数二英二的专硕院校。</li>
                        </ul>
                    </div>
                    <div style="background:rgba(15,23,42,0.6); padding:14px; border-radius:8px; border:1px solid rgba(255,255,255,0.06);">
                        <strong style="color:#34d399; font-size:0.9rem; display:block; margin-bottom:6px;">方案 B：选考“22 (数二 + 英二)” —— 【小白首选黄金组合】</strong>
                        <ul style="padding-left:18px; color:#cbd5e1;">
                            <li><strong>考查范围</strong>：高数(78%) + 线代(22%)。<strong>彻底不考概率论</strong>！砍掉三重积分、曲线曲面积分、级数。</li>
                            <li><strong>复习工作量</strong>：公共课省下数百小时，能够腾出核心战略时间死磕 408 统考与做题。</li>
                            <li><strong>性价比</strong>：专硕招考名额占全国 80% 以上，找大厂工作和待遇与学硕完全一致。</li>
                        </ul>
                    </div>
                </div>
            </div>

            <!-- Math Comparison Table -->
            <div style="background:var(--bg-card); border:1px solid var(--border-color); border-radius:12px; padding:20px;">
                <h4 style="color:var(--accent-cyan); font-size:0.95rem; margin-bottom:12px;">📊 数学一 vs 数学二 高等数学大纲考查范围差异清单</h4>
                <table style="width:100%; border-collapse:collapse; font-size:0.8rem; text-align:left;">
                    <thead>
                        <tr style="background:#1e293b; color:#94a3b8;">
                            <th style="padding:10px 14px;">微积分考点章节</th>
                            <th style="padding:10px 14px;">数学一 (301)</th>
                            <th style="padding:10px 14px;">数学二 (302)</th>
                            <th style="padding:10px 14px;">复习难度与考法提醒</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr style="border-bottom:1px solid #334155;">
                            <td style="padding:10px 14px;"><strong>极限、导数与一元微积分</strong></td>
                            <td style="padding:10px 14px; color:#38bdf8;">必考</td>
                            <td style="padding:10px 14px; color:#38bdf8;">必考</td>
                            <td style="padding:10px 14px; color:#94a3b8;">两者完全一致，数二在定积分物理应用（引力/做功）考查更深</td>
                        </tr>
                        <tr style="border-bottom:1px solid #334155;">
                            <td style="padding:10px 14px;"><strong>多元函数偏导与二重积分</strong></td>
                            <td style="padding:10px 14px; color:#38bdf8;">必考</td>
                            <td style="padding:10px 14px; color:#38bdf8;">必考</td>
                            <td style="padding:10px 14px; color:#94a3b8;">极值与二重积分对称性化简，均为大题高频</td>
                        </tr>
                        <tr style="border-bottom:1px solid #334155; background:rgba(244,63,94,0.06);">
                            <td style="padding:10px 14px;"><strong>三重积分 (切片/柱面/球面)</strong></td>
                            <td style="padding:10px 14px; color:#f87171; font-weight:bold;">必考 (四大天王)</td>
                            <td style="padding:10px 14px; color:#10b981; font-weight:bold;">彻底不考 ❌</td>
                            <td style="padding:10px 14px; color:#cbd5e1;">数二直接减负，无需掌握空间立体积分</td>
                        </tr>
                        <tr style="border-bottom:1px solid #334155; background:rgba(244,63,94,0.06);">
                            <td style="padding:10px 14px;"><strong>第一类/第二类曲线曲面积分</strong></td>
                            <td style="padding:10px 14px; color:#f87171; font-weight:bold;">必考 (格林/高斯公式)</td>
                            <td style="padding:10px 14px; color:#10b981; font-weight:bold;">彻底不考 ❌</td>
                            <td style="padding:10px 14px; color:#cbd5e1;">数一计算量最大、最容易丢分的大题章节，数二完全不用学</td>
                        </tr>
                        <tr style="border-bottom:1px solid #334155; background:rgba(244,63,94,0.06);">
                            <td style="padding:10px 14px;"><strong>无穷级数 (数项级数与幂级数求和)</strong></td>
                            <td style="padding:10px 14px; color:#f87171; font-weight:bold;">必考 (傅里叶级数)</td>
                            <td style="padding:10px 14px; color:#10b981; font-weight:bold;">彻底不考 ❌</td>
                            <td style="padding:10px 14px; color:#cbd5e1;">数一必有一道 10~12 分压轴大题，数二完全不考</td>
                        </tr>
                        <tr style="border-bottom:1px solid #334155; background:rgba(244,63,94,0.06);">
                            <td style="padding:10px 14px;"><strong>概率论与数理统计全书</strong></td>
                            <td style="padding:10px 14px; color:#f87171; font-weight:bold;">占 22% (约33分)</td>
                            <td style="padding:10px 14px; color:#10b981; font-weight:bold;">完全不考 (0分) ❌</td>
                            <td style="padding:10px 14px; color:#cbd5e1;">数二直接省掉整整一本概率辅导书的复习时间</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <!-- English Comparison Cards -->
            <div style="background:var(--bg-card); border:1px solid var(--border-color); border-radius:12px; padding:20px;">
                <h4 style="color:var(--accent-amber); font-size:0.95rem; margin-bottom:12px;">🇬🇧 英语一 vs 英语二 题型与提分难度对比</h4>
                <div style="display:grid; grid-template-columns:repeat(3, 1fr); gap:15px; font-size:0.8rem; line-height:1.5;">
                    <div style="background:#0f172a; padding:12px; border-radius:8px; border:1px solid #334155;">
                        <strong style="color:#fde047; display:block; margin-bottom:4px;">1. 阅读理解 (Part A 40分)</strong>
                        <p style="color:#cbd5e1;"><strong>英一</strong>：长难句抽象，多选自英美哲理与社科期刊，题目陷阱多，过线难。<br><strong>英二</strong>：多选自商业、科技与社会生活，文章主旨清晰，答案定位更直接，均分普遍高 8~12 分。</p>
                    </div>
                    <div style="background:#0f172a; padding:12px; border-radius:8px; border:1px solid #334155;">
                        <strong style="color:#fde047; display:block; margin-bottom:4px;">2. 翻译题型 (Part C 10~15分)</strong>
                        <p style="color:#cbd5e1;"><strong>英一 (10分)</strong>：从极难学术长文中挑出 5 个超长句，生词怪词多，全国均分仅 3~4 分。<br><strong>英二 (15分)</strong>：通篇翻译一段约 150 词的连贯小短文，语境流畅，得分率普遍在 10 分以上。</p>
                    </div>
                    <div style="background:#0f172a; padding:12px; border-radius:8px; border:1px solid #334155;">
                        <strong style="color:#fde047; display:block; margin-bottom:4px;">3. 写作大作文 (Part B 15~20分)</strong>
                        <p style="color:#cbd5e1;"><strong>英一 (20分)</strong>：图画作文，需要准确提炼漫画中的深层哲理寓意并升华。<br><strong>英二 (15分)</strong>：图表作文（柱状/饼状/折线），三段式套路模板极度规范，提分见效快。</p>
                    </div>
                </div>
            </div>
        </div>
"""

# Insert panel before </div class="main-content">
insert_marker = "<!-- 4. Templates View -->"
if insert_marker in html:
    html = html.replace(insert_marker, matheng_panel_html + "\n        " + insert_marker)
else:
    print("Warning: insert_marker not found!")

# 3. Update switchTab JS function to handle 'matheng'
old_switch = """            } else if (tab === 'templates') {
                document.querySelectorAll('.nav-item')[3].classList.add('active');
                document.getElementById('templates-view').classList.add('active');
                document.getElementById('tab-title').innerText = '高频代码与PV解题模板';
                document.getElementById('tab-badge').innerText = '41题高频代码 · 操作系统经典PV';
                document.getElementById('tab-meta').innerText = '已包含一键复制代码';
            }"""

new_switch = """            } else if (tab === 'matheng') {
                document.querySelectorAll('.nav-item')[2].classList.add('active');
                document.getElementById('matheng-view').classList.add('active');
                document.getElementById('tab-title').innerText = '📐 公共课考纲深度对比与 11 vs 22 选考决策模型';
                document.getElementById('tab-badge').innerText = '数一/数二考纲差异 · 英一/英二题型分析';
                document.getElementById('tab-meta').innerText = '官方考纲详细对齐 · 小白起步期过渡策略';
            } else if (tab === 'strategy') {
                document.querySelectorAll('.nav-item')[3].classList.add('active');
                document.getElementById('strategy-view').classList.add('active');
                document.getElementById('tab-title').innerText = '分值权重与备考规划';
                document.getElementById('tab-badge').innerText = '45/45/35/25 分值矩阵';
                document.getElementById('tab-meta').innerText = '四季黄金备考时间线';
            } else if (tab === 'templates') {
                document.querySelectorAll('.nav-item')[4].classList.add('active');
                document.getElementById('templates-view').classList.add('active');
                document.getElementById('tab-title').innerText = '高频代码与PV解题模板';
                document.getElementById('tab-badge').innerText = '41题高频代码 · 操作系统经典PV';
                document.getElementById('tab-meta').innerText = '已包含一键复制代码';
            }"""

# Fix nav indices in switchTab
old_strategy_block = """            } else if (tab === 'strategy') {
                document.querySelectorAll('.nav-item')[2].classList.add('active');
                document.getElementById('strategy-view').classList.add('active');
                document.getElementById('tab-title').innerText = '分值权重与备考规划';
                document.getElementById('tab-badge').innerText = '45/45/35/25 分值矩阵';
                document.getElementById('tab-meta').innerText = '四季黄金备考时间线';
            } else if (tab === 'templates') {
                document.querySelectorAll('.nav-item')[3].classList.add('active');
                document.getElementById('templates-view').classList.add('active');
                document.getElementById('tab-title').innerText = '高频代码与PV解题模板';
                document.getElementById('tab-badge').innerText = '41题高频代码 · 操作系统经典PV';
                document.getElementById('tab-meta').innerText = '已包含一键复制代码';
            }"""

if old_strategy_block in html:
    html = html.replace(old_strategy_block, new_switch)
else:
    print("Warning: old_strategy_block not found!")

with open(dashboard_path, "w", encoding="utf-8") as f:
    f.write(html)

print("Injected Math & English Syllabus Tab successfully into CS408_Visual_Dashboard.html!")
