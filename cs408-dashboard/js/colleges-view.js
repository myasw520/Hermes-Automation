// Colleges View Module: Table Rendering, Filtering, Search & Pagination
import { collegesData } from './data/colleges-data.js';

export class CollegesView {
    constructor(tbodyId, paginationId, counterId) {
        this.tbody = document.getElementById(tbodyId);
        this.paginationContainer = document.getElementById(paginationId);
        this.counterEl = document.getElementById(counterId);

        this.allData = collegesData;
        this.filteredData = [...collegesData];

        this.currentCategory = 'all';
        this.searchQuery = '';
        this.currentPage = 1;
        this.pageSize = 8; // 8 items per page for clean paging

        this.applyFilters();
    }

    setCategory(cat, btn) {
        this.currentCategory = cat;
        if (btn) {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
        }
        this.currentPage = 1;
        this.applyFilters();
    }

    setSearch(query) {
        this.searchQuery = query.toLowerCase().trim();
        this.currentPage = 1;
        this.applyFilters();
    }

    setPageSize(size) {
        this.pageSize = size === 'all' ? 9999 : parseInt(size, 10);
        this.currentPage = 1;
        this.render();
    }

    goToPage(page) {
        this.currentPage = page;
        this.render();
        const table = document.getElementById('college-table');
        if (table) table.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    applyFilters() {
        this.filteredData = this.allData.filter(item => {
            let matchCat = true;
            if (this.currentCategory === 'c9' || this.currentCategory === '985') {
                matchCat = (item.tag === 'tag-c9' || item.tag === 'tag-985' || item.cat === 'c9' || item.cat === 'strong');
            } else if (this.currentCategory === '211') {
                matchCat = (item.tag === 'tag-211' || item.cat === '211');
            } else if (this.currentCategory === 'double') {
                matchCat = (item.tag === 'tag-double' || item.cat === 'double');
            } else if (this.currentCategory === 'jzh') {
                matchCat = (item.region === '江浙沪');
            } else if (this.currentCategory === 'med') {
                matchCat = (item.is_med === true);
            }

            let matchQuery = true;
            if (this.searchQuery) {
                const targetText = [
                    item.name,
                    item.subject,
                    item.source,
                    item.level,
                    item.major || '',
                    item.region || '',
                    item.y2023 || '',
                    item.y2024 || '',
                    item.y2025 || ''
                ].join(' ').toLowerCase();

                matchQuery = targetText.includes(this.searchQuery);
            }
            return matchCat && matchQuery;
        });

        this.render();
    }

    render() {
        if (!this.tbody) return;
        this.tbody.innerHTML = '';

        const totalItems = this.filteredData.length;
        const totalPages = Math.max(1, Math.ceil(totalItems / this.pageSize));
        if (this.currentPage > totalPages) this.currentPage = totalPages;

        const startIndex = (this.currentPage - 1) * this.pageSize;
        const pageItems = this.filteredData.slice(startIndex, startIndex + this.pageSize);

        if (pageItems.length === 0) {
            this.tbody.innerHTML = `<tr><td colspan="10" style="text-align:center; padding:35px; color:#94a3b8; font-size:0.88rem;">🔍 未找到符合条件的院校数据，请调整分类或搜索关键词</td></tr>`;
        } else {
            pageItems.forEach(item => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td style="min-width: 220px;">
                        <div style="font-weight: 700; color: #f8fafc; font-size: 0.92rem; letter-spacing: 0.02em;">${item.name}</div>
                        <div style="margin-top: 5px; display: flex; align-items: center; gap: 6px; flex-wrap: wrap;">
                            <span class="tag ${item.tag}">${item.level}</span>
                            ${item.region ? `<span style="font-size:0.68rem; padding:1px 6px; border-radius:4px; background:#1e293b; color:#94a3b8; border:1px solid #334155;">${item.region}</span>` : ''}
                        </div>
                        ${item.major ? `<div style="font-size:0.73rem; color:#38bdf8; margin-top:5px; font-family:monospace; background:#0b1329; padding:2px 7px; border-radius:4px; display:inline-block; border-left:3px solid #38bdf8; line-height:1.4;">${item.major}</div>` : ''}
                    </td>
                    <td><span style="color:var(--accent-cyan);font-weight:600;">${item.subject}</span></td>
                    <td><span style="color:#94a3b8;">${item.y2023}</span></td>
                    <td><span style="color:#cbd5e1;">${item.y2024}</span></td>
                    <td><strong style="color:#38bdf8; font-weight:700;">${item.y2025}</strong></td>
                    <td style="font-weight:500;">${item.tuition}</td>
                    <td><span class="tag ${item.dorm_type}">${item.dorm}</span></td>
                    <td><span style="color:#cbd5e1;">${item.ratio}</span></td>
                    <td style="color:#94a3b8;font-size:0.75rem;">${item.pub_date}</td>
                    <td><a href="${item.url}" target="_blank" class="official-link">${item.source} ↗</a></td>
                `;
                this.tbody.appendChild(tr);
            });
        }

        if (this.counterEl) {
            this.counterEl.innerText = `共匹配 ${totalItems} 所标杆院校 (显示第 ${totalItems === 0 ? 0 : startIndex + 1} - ${Math.min(startIndex + this.pageSize, totalItems)} 条)`;
        }

        this.renderPagination(totalPages, totalItems);
    }

    renderPagination(totalPages, totalItems) {
        if (!this.paginationContainer) return;

        if (totalPages <= 1) {
            this.paginationContainer.innerHTML = `
                <span>当前显示全部 ${totalItems} 所院校</span>
                <div style="display:flex; align-items:center; gap:8px;">
                    <label style="color:#64748b; font-size:0.78rem;">每页:</label>
                    <select onchange="window.setPageSize(this.value)" style="background:#0f172a; border:1px solid #334155; color:#cbd5e1; border-radius:4px; padding:3px 6px; font-size:0.78rem;">
                        <option value="8" ${this.pageSize === 8 ? 'selected' : ''}>8 条</option>
                        <option value="15" ${this.pageSize === 15 ? 'selected' : ''}>15 条</option>
                        <option value="all" ${this.pageSize >= 999 ? 'selected' : ''}>全部</option>
                    </select>
                </div>
            `;
            return;
        }

        let pagesHtml = '';
        for (let i = 1; i <= totalPages; i++) {
            pagesHtml += `<button class="page-btn ${i === this.currentPage ? 'active' : ''}" onclick="window.goToPage(${i})">${i}</button>`;
        }

        this.paginationContainer.innerHTML = `
            <span>第 ${this.currentPage} / ${totalPages} 页</span>
            <div class="pagination-btns">
                <button class="page-btn" ${this.currentPage === 1 ? 'disabled' : ''} onclick="window.goToPage(${this.currentPage - 1})">◀ 上一页</button>
                ${pagesHtml}
                <button class="page-btn" ${this.currentPage === totalPages ? 'disabled' : ''} onclick="window.goToPage(${this.currentPage + 1})">下一页 ▶</button>
            </div>
            <div style="display:flex; align-items:center; gap:8px;">
                <label style="color:#64748b; font-size:0.78rem;">每页:</label>
                <select onchange="window.setPageSize(this.value)" style="background:#0f172a; border:1px solid #334155; color:#cbd5e1; border-radius:4px; padding:3px 6px; font-size:0.78rem;">
                    <option value="8" ${this.pageSize === 8 ? 'selected' : ''}>8 条</option>
                    <option value="15" ${this.pageSize === 15 ? 'selected' : ''}>15 条</option>
                    <option value="all" ${this.pageSize >= 999 ? 'selected' : ''}>全部</option>
                </select>
            </div>
        `;
    }
}
