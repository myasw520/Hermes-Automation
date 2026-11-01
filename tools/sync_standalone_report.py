import re

with open('cs408-dashboard/js/data/colleges-data.js', 'r', encoding='utf-8') as f:
    js_data = f.read()

# remove export
data_block = js_data.replace('export const collegesData =', 'const collegesData =')

with open('reports/CS408_Visual_Dashboard.html', 'r', encoding='utf-8') as f:
    standalone = f.read()

standalone = re.sub(r'const collegesData = \[[\s\S]*?\];', data_block.strip(), standalone)

# also update filter buttons in standalone
pattern = r'<div class="filter-pills">[\s\S]*?</div>\s*<input type="text" class="search-box" id="college-search"[^>]*>'

replacement = '''<div class="filter-pills">
                    <button class="filter-btn active" onclick="filterColleges('all', this)">全部标杆</button>
                    <button class="filter-btn" onclick="filterColleges('jzh', this)" style="border-color:#38bdf8; color:#38bdf8;">📍 江浙沪精选 (保宿/常规学费)</button>
                    <button class="filter-btn" onclick="filterColleges('med', this)" style="border-color:#10b981; color:#10b981;">🧬 医工交叉/中医药黄金赛道</button>
                    <button class="filter-btn" onclick="filterColleges('211', this)">高性价比211</button>
                    <button class="filter-btn" onclick="filterColleges('double', this)">优质双非/就业名门</button>
                    <button class="filter-btn" onclick="filterColleges('c9', this)">顶级C9/985</button>
                </div>
                <input type="text" class="search-box" id="college-search" placeholder="🔍 搜索院校名称 / 专业代码 (如 085404) / 城市..." oninput="searchColleges()">'''

standalone, c = re.subn(pattern, replacement, standalone)
print("Updated standalone filter pills:", c)

# update filter logic in standalone if present
filter_fn = '''function filterColleges(cat, btn) {
            currentCollegeCat = cat;
            if (btn) {
                document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
            }
            applyCollegeFilter();
        }'''

# check if applyCollegeFilter in standalone needs updating
if 'item.region === \'江浙沪\'' not in standalone:
    standalone = standalone.replace(
        "if (currentCollegeCat === 'c9') matchCat = item.tag === 'tag-c9';",
        "if (currentCollegeCat === 'c9') matchCat = item.tag === 'tag-c9';\n            else if (currentCollegeCat === 'jzh') matchCat = item.region === '江浙沪';\n            else if (currentCollegeCat === 'med') matchCat = item.is_med === true;"
    )
    # also add major in rendering
    old_td = "<td><strong>${item.name}</strong> <span class=\"tag ${item.tag}\">${item.level}</span></td>"
    new_td = """<td>
                        <div style="font-weight:700; color:#f8fafc; font-size:0.92rem;">${item.name}</div>
                        <div style="margin-top:4px; display:flex; align-items:center; gap:6px; flex-wrap:wrap;">
                            <span class="tag ${item.tag}">${item.level}</span>
                            ${item.region ? `<span style="font-size:0.68rem; padding:1px 6px; border-radius:4px; background:#1e293b; color:#94a3b8; border:1px solid #334155;">${item.region}</span>` : ''}
                        </div>
                        ${item.major ? `<div style="font-size:0.75rem; color:#38bdf8; margin-top:5px; font-family:monospace; background:#0f172a; padding:3px 7px; border-radius:4px; display:inline-block; border-left:2px solid #38bdf8;">${item.major}</div>` : ''}
                    </td>"""
    standalone = standalone.replace(old_td, new_td)

with open('reports/CS408_Visual_Dashboard.html', 'w', encoding='utf-8') as f:
    f.write(standalone)

print("Synchronized reports/CS408_Visual_Dashboard.html successfully!")
