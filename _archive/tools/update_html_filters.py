import re

with open('cs408-dashboard/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

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

new_content, count = re.subn(pattern, replacement, content)
if count > 0:
    with open('cs408-dashboard/index.html', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"Replaced {count} occurrences successfully!")
else:
    print("Pattern not matched!")
