// Application Bootstrap & Router
import { GraphEngine } from './graph-engine.js';
import { CollegesView } from './colleges-view.js';
import { allNodes } from './data/syllabus-nodes.js';
import { allLinks } from './data/syllabus-links.js';

let graphEngine = null;
let collegesView = null;

export function switchTab(tab) {
    document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.view-panel').forEach(el => el.classList.remove('active'));

    const tabTitle = document.getElementById('tab-title');
    const tabBadge = document.getElementById('tab-badge');
    const tabMeta = document.getElementById('tab-meta');

    // 1. Activate target panel
    const targetPanel = document.getElementById(tab + '-view');
    if (targetPanel) {
        targetPanel.classList.add('active');
        targetPanel.scrollTop = 0;
    }

    // 2. Activate target nav item
    const navItems = document.querySelectorAll('.nav-item');
    const tabIndexMap = { 'graph': 0, 'colleges': 1, 'strategy': 2, 'matheng': 3, 'templates': 4 };
    if (tabIndexMap[tab] !== undefined && navItems[tabIndexMap[tab]]) {
        navItems[tabIndexMap[tab]].classList.add('active');
    }

    // 3. Update topbar meta
    if (tab === 'graph') {
        if (tabTitle) tabTitle.innerText = '408 知识全景拓扑图 (高清高交互重构版)';
        if (tabBadge) tabBadge.innerText = '总分 150 分 · 统考代码 408';
        if (tabMeta) tabMeta.innerText = `核心考点：${allNodes.length} 个 · 命题连线：${allLinks.length} 条 · 支持全景缩放与节点拖拽`;
        if (graphEngine) {
            graphEngine.resize();
            setTimeout(() => graphEngine.fitToScreen(false), 50);
        }
    } else if (tab === 'colleges') {
        if (tabTitle) tabTitle.innerText = '🏫 计算机考研标杆院校逐年录取数据库与避坑指南';
        if (tabBadge) tabBadge.innerText = '含 2023-2025 逐年线 & 2026 简章公布日';
        if (tabMeta) tabMeta.innerText = '官方权威来源核验 · 小程序数据抓取指南';
    } else if (tab === 'strategy') {
        if (tabTitle) tabTitle.innerText = '分值权重与备考规划';
        if (tabBadge) tabBadge.innerText = '45/45/35/25 分值矩阵';
        if (tabMeta) tabMeta.innerText = '四季黄金备考时间线';
    } else if (tab === 'matheng') {
        if (tabTitle) tabTitle.innerText = '📐 公共课考纲深度对比与 11 vs 22 选考决策模型';
        if (tabBadge) tabBadge.innerText = '数一/数二考纲差异 · 英一/英二题型分析';
        if (tabMeta) tabMeta.innerText = '官方考纲详细对齐 · 小白起步期过渡策略';
    } else if (tab === 'templates') {
        if (tabTitle) tabTitle.innerText = '高频代码与PV解题模板';
        if (tabBadge) tabBadge.innerText = '41题高频代码 · 操作系统经典PV';
        if (tabMeta) tabMeta.innerText = '已包含一键复制代码';
    }
}

export function copyCode(id) {
    const code = document.getElementById(id).innerText;
    navigator.clipboard.writeText(code).then(() => {
        alert('代码模板已成功复制到剪贴板！');
    });
}

export function toggleIntelCard() {
    const card = document.getElementById('intel-card');
    const btn = document.getElementById('intel-toggle-btn');
    if (!card || !btn) return;
    card.classList.toggle('collapsed');
    if (card.classList.contains('collapsed')) {
        btn.innerText = '展开指南 ▾';
    } else {
        btn.innerText = '收起指南 ▴';
    }
}

// Window exports for HTML onclick/oninput handlers
window.switchTab = switchTab;
window.copyCode = copyCode;
window.toggleIntelCard = toggleIntelCard;

window.filterColleges = (cat, btn) => window.collegesView && window.collegesView.setCategory(cat, btn);
window.searchColleges = () => {
    const input = document.getElementById('college-search');
    const q = input ? input.value : '';
    window.collegesView && window.collegesView.setSearch(q);
};

window.zoomIn = () => window.graphEngine && window.graphEngine.zoomIn();
window.zoomOut = () => window.graphEngine && window.graphEngine.zoomOut();
window.fitToScreen = (anim) => window.graphEngine && window.graphEngine.fitToScreen(anim);
window.resetGraphView = () => window.graphEngine && window.graphEngine.filterCategory('all');
window.toggleWheelMode = () => {
    if (!window.graphEngine) return;
    const mode = window.graphEngine.toggleWheelMode();
    const btn = document.getElementById('btn-wheel-mode');
    const txt = document.getElementById('wheel-mode-text');
    if (txt) txt.innerText = mode === 'zoom' ? '滚轮: 缩放' : '滚轮: 平移';
    if (btn) btn.classList.toggle('active', mode === 'pan');
};
window.toggleDrawer = () => {
    if (!window.graphEngine) return;
    const isCollapsed = window.graphEngine.toggleDrawer();
    const btnLabel = document.getElementById('drawer-btn-label');
    const icon = document.getElementById('drawer-toggle-icon');
    if (btnLabel) btnLabel.innerText = isCollapsed ? '展开侧栏' : '收起侧栏';
    if (icon) icon.innerHTML = isCollapsed 
        ? '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M15 18l-6-6 6-6"/>'
        : '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 18l6-6-6-6"/>';
};
window.filterGraphCategory = (cat, el) => window.graphEngine && window.graphEngine.filterCategory(cat, el);
window.filterGraphSearch = (q) => window.graphEngine && window.graphEngine.searchNode(q);

document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('graph-canvas');
    const drawer = document.getElementById('detail-drawer');
    const minimapCanvas = document.getElementById('minimap-canvas');

    if (canvas) {
        graphEngine = new GraphEngine(canvas, drawer, minimapCanvas);
        window.graphEngine = graphEngine;
    }

    collegesView = new CollegesView('college-tbody', 'pagination-bar', 'college-counter');
    window.collegesView = collegesView;
});
