// Graph Canvas Engine (High-DPI Retina, Auto-Fit, Minimap, Smooth Navigation)
import { allNodes } from './data/syllabus-nodes.js';
import { allLinks } from './data/syllabus-links.js';

export class GraphEngine {
    constructor(canvas, drawer, minimapCanvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.drawer = drawer;
        this.minimapCanvas = minimapCanvas;
        this.mCtx = minimapCanvas ? minimapCanvas.getContext('2d') : null;

        this.nodes = [...allNodes];
        this.links = [...allLinks];

        this.width = 800;
        this.height = 600;

        // Viewport
        this.zoom = 1.0;
        this.panX = 0;
        this.panY = 0;
        this.targetPanX = 0;
        this.targetPanY = 0;
        this.targetZoom = 1.0;
        this.isAnimating = false;

        this.isPanning = false;
        this.startPanX = 0;
        this.startPanY = 0;
        this.wheelMode = 'zoom'; // 'zoom' or 'pan'

        this.selectedNode = null;
        this.dragNode = null;
        this.hoveredNode = null;
        this.activeCategory = 'all';

        this.initEvents();
        this.resize();
        this.fitToScreen(false);
        this.startRenderLoop();
    }

    resize() {
        if (!this.canvas || !this.canvas.parentElement) return;
        const isCollapsed = this.drawer && this.drawer.classList.contains('collapsed');
        const drawerW = isCollapsed ? 0 : 380;
        this.width = this.canvas.parentElement.clientWidth - drawerW;
        this.height = this.canvas.parentElement.clientHeight;

        if (this.width > 50 && this.height > 50) {
            const dpr = window.devicePixelRatio || 1;
            this.canvas.width = Math.round(this.width * dpr);
            this.canvas.height = Math.round(this.height * dpr);
            this.canvas.style.width = this.width + 'px';
            this.canvas.style.height = this.height + 'px';
        }
    }

    fitToScreen(animate = true) {
        if (!this.nodes || this.nodes.length === 0 || !this.width || !this.height) return;

        let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
        this.nodes.forEach(n => {
            const pad = n.r + 55;
            if (n.x - pad < minX) minX = n.x - pad;
            if (n.x + pad > maxX) maxX = n.x + pad;
            if (n.y - pad < minY) minY = n.y - pad;
            if (n.y + pad + 25 > maxY) maxY = n.y + pad + 25;
        });

        const gW = maxX - minX;
        const gH = maxY - minY;
        const padScreen = 45;
        const sX = (this.width - padScreen * 2) / gW;
        const sY = (this.height - padScreen * 2) / gH;
        const targetZ = Math.min(Math.max(Math.min(sX, sY), 0.45), 1.6);

        const cX = (minX + maxX) / 2;
        const cY = (minY + maxY) / 2;

        const tPanX = (this.width / 2) - cX * targetZ;
        const tPanY = (this.height / 2) - cY * targetZ;

        if (animate) {
            this.animateViewportTo(tPanX, tPanY, targetZ);
        } else {
            this.panX = tPanX;
            this.panY = tPanY;
            this.zoom = targetZ;
            this.targetPanX = tPanX;
            this.targetPanY = tPanY;
            this.targetZoom = targetZ;
        }
    }

    animateViewportTo(tx, ty, tz) {
        this.targetPanX = tx;
        this.targetPanY = ty;
        this.targetZoom = tz;
        this.isAnimating = true;
    }

    zoomIn() {
        const cX = this.width / 2;
        const cY = this.height / 2;
        const nextZ = Math.min(this.zoom * 1.25, 3.5);
        const tX = cX - (cX - this.panX) * (nextZ / this.zoom);
        const tY = cY - (cY - this.panY) * (nextZ / this.zoom);
        this.animateViewportTo(tX, tY, nextZ);
    }

    zoomOut() {
        const cX = this.width / 2;
        const cY = this.height / 2;
        const nextZ = Math.max(this.zoom / 1.25, 0.3);
        const tX = cX - (cX - this.panX) * (nextZ / this.zoom);
        const tY = cY - (cY - this.panY) * (nextZ / this.zoom);
        this.animateViewportTo(tX, tY, nextZ);
    }

    toggleWheelMode() {
        this.wheelMode = (this.wheelMode === 'zoom') ? 'pan' : 'zoom';
        return this.wheelMode;
    }

    toggleDrawer() {
        if (!this.drawer) return;
        this.drawer.classList.toggle('collapsed');
        const graphView = document.getElementById('graph-view');
        if (graphView) graphView.classList.toggle('drawer-closed');

        setTimeout(() => {
            this.resize();
            this.fitToScreen(true);
        }, 320);

        return this.drawer.classList.contains('collapsed');
    }

    filterCategory(cat, element) {
        this.activeCategory = cat;
        if (cat === 'all') {
            this.nodes = [...allNodes];
            this.links = [...allLinks];
        } else if (cat === 'cross') {
            const crossSrc = new Set(allLinks.filter(l => l.cross).map(l => l.source));
            const crossTgt = new Set(allLinks.filter(l => l.cross).map(l => l.target));
            this.nodes = allNodes.filter(n => crossSrc.has(n.id) || crossTgt.has(n.id));
            this.links = allLinks.filter(l => l.cross);
        } else {
            this.nodes = allNodes.filter(n => n.cat === cat || n.cat === 'center');
            const nodeIds = new Set(this.nodes.map(n => n.id));
            this.links = allLinks.filter(l => nodeIds.has(l.source) && nodeIds.has(l.target));
        }

        if (element) {
            document.querySelectorAll('.filter-pill-item').forEach(el => el.classList.remove('active'));
            element.classList.add('active');
        }
        this.fitToScreen(true);
    }

    searchNode(query) {
        const q = query.toLowerCase().trim();
        if (!q) {
            this.filterCategory(this.activeCategory);
            return;
        }
        const match = allNodes.find(n => n.name.toLowerCase().includes(q) || n.desc.toLowerCase().includes(q));
        if (match) {
            this.selectedNode = match;
            this.showDetail(match);
            const tX = (this.width / 2) - match.x * 1.35;
            const tY = (this.height / 2) - match.y * 1.35;
            this.animateViewportTo(tX, tY, 1.35);
        }
    }

    getNodeAt(clientX, clientY) {
        const rect = this.canvas.getBoundingClientRect();
        const x = (clientX - rect.left - this.panX) / this.zoom;
        const y = (clientY - rect.top - this.panY) / this.zoom;
        for (let i = this.nodes.length - 1; i >= 0; i--) {
            const n = this.nodes[i];
            if (Math.hypot(n.x - x, n.y - y) <= n.r + 8) return n;
        }
        return null;
    }

    isNeighbor(n1, n2) {
        if (!n1 || !n2) return false;
        if (n1.id === n2.id) return true;
        return this.links.some(l => 
            (l.source === n1.id && l.target === n2.id) || 
            (l.source === n2.id && l.target === n1.id)
        );
    }

    showDetail(node) {
        const titleEl = document.getElementById('drawer-node-name');
        const bodyEl = document.getElementById('drawer-node-body');
        if (titleEl) titleEl.innerText = node.name;

        let html = `<p style="line-height:1.7; color:#f1f5f9; font-size:0.9rem;">${node.desc}</p>`;

        const neighbors = [];
        allLinks.forEach(l => {
            if (l.source === node.id) {
                const targetNode = allNodes.find(n => n.id === l.target);
                if (targetNode) neighbors.push({ name: targetNode.name, cross: l.cross, label: l.label });
            } else if (l.target === node.id) {
                const sourceNode = allNodes.find(n => n.id === l.source);
                if (sourceNode) neighbors.push({ name: sourceNode.name, cross: l.cross, label: l.label });
            }
        });

        if (neighbors.length > 0) {
            html += `<h5 style="margin-top:18px; margin-bottom:8px; color:var(--accent-amber); font-size:0.85rem;">🔗 关联考点与综合命题链路：</h5><ul style="padding-left:18px; font-size:0.82rem; line-height:1.6; color:#94a3b8;">`;
            neighbors.forEach(nbr => {
                if (nbr.cross) {
                    html += `<li style="color:#f43f5e; margin-bottom:4px;"><strong>[跨学科考查]</strong> ${nbr.name} ${nbr.label ? '— ' + nbr.label : ''}</li>`;
                } else {
                    html += `<li>${nbr.name}</li>`;
                }
            });
            html += `</ul>`;
        }

        if (bodyEl) bodyEl.innerHTML = html;
    }

    drawRoundRect(c, x, y, w, h, r) {
        if (c.roundRect) {
            c.roundRect(x, y, w, h, r);
        } else {
            c.beginPath();
            c.moveTo(x + r, y);
            c.lineTo(x + w - r, y);
            c.quadraticCurveTo(x + w, y, x + w, y + r);
            c.lineTo(x + w, y + h - r);
            c.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
            c.lineTo(x + r, y + h);
            c.quadraticCurveTo(x, y + h, x, y + h - r);
            c.lineTo(x, y + r);
            c.quadraticCurveTo(x, y, x + r, y);
            c.closePath();
        }
    }

    startRenderLoop() {
        const render = () => {
            this.draw();
            requestAnimationFrame(render);
        };
        requestAnimationFrame(render);
    }

    draw() {
        if (!this.canvas.width || !this.canvas.height) return;
        const dpr = window.devicePixelRatio || 1;

        if (this.isAnimating) {
            const factor = 0.2;
            this.panX += (this.targetPanX - this.panX) * factor;
            this.panY += (this.targetPanY - this.panY) * factor;
            this.zoom += (this.targetZoom - this.zoom) * factor;
            if (Math.abs(this.targetPanX - this.panX) < 0.5 && Math.abs(this.targetPanY - this.panY) < 0.5 && Math.abs(this.targetZoom - this.zoom) < 0.002) {
                this.panX = this.targetPanX;
                this.panY = this.targetPanY;
                this.zoom = this.targetZoom;
                this.isAnimating = false;
            }
        }

        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        this.ctx.save();
        this.ctx.scale(dpr, dpr);
        this.ctx.translate(this.panX, this.panY);
        this.ctx.scale(this.zoom, this.zoom);

        // Draw Links
        this.links.forEach(link => {
            const s = this.nodes.find(n => n.id === link.source);
            const t = this.nodes.find(n => n.id === link.target);
            if (!s || !t) return;

            const isHighlight = this.hoveredNode && (this.hoveredNode.id === s.id || this.hoveredNode.id === t.id);
            const isDimmed = this.hoveredNode && !isHighlight;
            const alpha = isDimmed ? 0.15 : (isHighlight ? 1.0 : 0.7);

            this.ctx.save();
            this.ctx.globalAlpha = alpha;

            this.ctx.beginPath();
            this.ctx.moveTo(s.x, s.y);
            this.ctx.lineTo(t.x, t.y);

            if (link.cross) {
                this.ctx.strokeStyle = isHighlight ? '#fb7185' : 'rgba(244, 63, 94, 0.8)';
                this.ctx.setLineDash([6, 4]);
                this.ctx.lineWidth = isHighlight ? 3.0 : 2.0;
            } else {
                this.ctx.strokeStyle = isHighlight ? '#38bdf8' : 'rgba(148, 163, 184, 0.35)';
                this.ctx.setLineDash([]);
                this.ctx.lineWidth = isHighlight ? 2.5 : 1.4;
            }
            this.ctx.stroke();

            // Cross-link label with clean pill background
            if (link.cross && (this.zoom > 0.65 || isHighlight)) {
                const mx = (s.x + t.x) / 2;
                const my = (s.y + t.y) / 2;
                const txt = link.label || '跨学科贯通';
                this.ctx.font = 'bold 11px -apple-system, BlinkMacSystemFont, "Segoe UI", "Microsoft YaHei", sans-serif';
                const tw = this.ctx.measureText(txt).width;
                const bw = tw + 14;
                const bh = 18;

                this.ctx.beginPath();
                this.drawRoundRect(this.ctx, mx - bw / 2, my - bh / 2, bw, bh, 4);
                this.ctx.fillStyle = 'rgba(15, 23, 42, 0.92)';
                this.ctx.fill();
                this.ctx.strokeStyle = 'rgba(244, 63, 94, 0.65)';
                this.ctx.lineWidth = 1;
                this.ctx.stroke();

                this.ctx.fillStyle = '#fda4af';
                this.ctx.textAlign = 'center';
                this.ctx.textBaseline = 'middle';
                this.ctx.fillText(txt, mx, my);
            }

            this.ctx.restore();
        });

        // Draw Nodes
        this.nodes.forEach(node => {
            const isSelected = (this.selectedNode === node);
            const isHovered = (this.hoveredNode === node);
            const isConnected = this.hoveredNode ? this.isNeighbor(this.hoveredNode, node) : true;
            const alpha = (this.hoveredNode && !isHovered && !isConnected) ? 0.22 : 1.0;

            this.ctx.save();
            this.ctx.globalAlpha = alpha;

            // Outer halo
            this.ctx.beginPath();
            this.ctx.arc(node.x, node.y, node.r + 7, 0, Math.PI * 2);
            this.ctx.fillStyle = node.color + '25';
            this.ctx.fill();

            // Core Circle
            this.ctx.beginPath();
            this.ctx.arc(node.x, node.y, node.r, 0, Math.PI * 2);
            this.ctx.fillStyle = node.color;
            if (isSelected || isHovered) {
                this.ctx.shadowColor = isSelected ? '#38bdf8' : node.color;
                this.ctx.shadowBlur = isSelected ? 24 : 16;
            }
            this.ctx.fill();
            this.ctx.shadowBlur = 0;

            // Border
            this.ctx.strokeStyle = isSelected ? '#ffffff' : (isHovered ? '#ffffff' : 'rgba(255, 255, 255, 0.55)');
            this.ctx.lineWidth = isSelected ? 3.5 : (isHovered ? 2.5 : 1.5);
            this.ctx.stroke();

            // Node Name Pill Badge
            let fontSize = 12;
            let fontWeight = '600';
            if (node.cat === 'center') {
                fontSize = 14;
                fontWeight = 'bold';
            } else if (['ds', 'coa', 'os', 'cn'].includes(node.cat) && node.r >= 22) {
                fontSize = 13;
                fontWeight = 'bold';
            }

            this.ctx.font = `${fontWeight} ${fontSize}px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", "Microsoft YaHei", sans-serif`;

            const label = node.name;
            const textWidth = this.ctx.measureText(label).width;
            const padX = 8;
            const padY = 4;
            const pillH = fontSize + padY * 2;
            const pillW = textWidth + padX * 2;
            const pillX = node.x - pillW / 2;
            const pillY = node.y + node.r + 7;

            // Draw pill background
            this.ctx.beginPath();
            this.drawRoundRect(this.ctx, pillX, pillY, pillW, pillH, 5);
            this.ctx.fillStyle = isSelected ? 'rgba(15, 23, 42, 0.96)' : (isHovered ? 'rgba(30, 41, 59, 0.96)' : 'rgba(15, 23, 42, 0.88)');
            this.ctx.fill();
            this.ctx.strokeStyle = isSelected ? '#38bdf8' : (isHovered ? node.color : 'rgba(100, 116, 139, 0.5)');
            this.ctx.lineWidth = isSelected ? 2.0 : 1;
            this.ctx.stroke();

            // Draw crisp text
            this.ctx.fillStyle = isSelected ? '#38bdf8' : (isHovered ? '#ffffff' : '#f8fafc');
            this.ctx.textAlign = 'center';
            this.ctx.textBaseline = 'middle';
            this.ctx.fillText(label, node.x, pillY + pillH / 2);

            this.ctx.restore();
        });

        this.ctx.restore();

        // Minimap
        this.drawMinimap();
    }

    drawMinimap() {
        if (!this.minimapCanvas || !this.mCtx) return;
        const mW = this.minimapCanvas.width;
        const mH = this.minimapCanvas.height;
        this.mCtx.clearRect(0, 0, mW, mH);

        const minX = 0, maxX = 1000, minY = 20, maxY = 750;
        const scaleX = (mW - 16) / (maxX - minX);
        const scaleY = (mH - 16) / (maxY - minY);
        const scale = Math.min(scaleX, scaleY);
        const offX = (mW - (maxX - minX) * scale) / 2;
        const offY = (mH - (maxY - minY) * scale) / 2;

        const toMini = (x, y) => ({
            x: offX + (x - minX) * scale,
            y: offY + (y - minY) * scale
        });

        // Miniature links
        this.mCtx.strokeStyle = 'rgba(148, 163, 184, 0.2)';
        this.mCtx.lineWidth = 0.8;
        this.links.forEach(l => {
            const s = allNodes.find(n => n.id === l.source);
            const t = allNodes.find(n => n.id === l.target);
            if (s && t) {
                const p1 = toMini(s.x, s.y);
                const p2 = toMini(t.x, t.y);
                this.mCtx.beginPath();
                this.mCtx.moveTo(p1.x, p1.y);
                this.mCtx.lineTo(p2.x, p2.y);
                this.mCtx.stroke();
            }
        });

        // Miniature nodes
        this.nodes.forEach(n => {
            const p = toMini(n.x, n.y);
            this.mCtx.beginPath();
            this.mCtx.arc(p.x, p.y, Math.max(n.r * scale * 0.7, 2), 0, Math.PI * 2);
            this.mCtx.fillStyle = n.color;
            this.mCtx.fill();
        });

        // Viewport rectangle
        const vpLeft = (0 - this.panX) / this.zoom;
        const vpTop = (0 - this.panY) / this.zoom;
        const vpRight = (this.width - this.panX) / this.zoom;
        const vpBottom = (this.height - this.panY) / this.zoom;

        const pTopLeft = toMini(vpLeft, vpTop);
        const pBottomRight = toMini(vpRight, vpBottom);

        const rX = pTopLeft.x;
        const rY = pTopLeft.y;
        const rW = pBottomRight.x - pTopLeft.x;
        const rH = pBottomRight.y - pTopLeft.y;

        this.mCtx.strokeStyle = '#38bdf8';
        this.mCtx.lineWidth = 1.5;
        this.mCtx.strokeRect(rX, rY, rW, rH);
        this.mCtx.fillStyle = 'rgba(56, 189, 248, 0.15)';
        this.mCtx.fillRect(rX, rY, rW, rH);
    }

    initEvents() {
        window.addEventListener('resize', () => {
            this.resize();
            this.fitToScreen(false);
        });

        // Mousedown
        this.canvas.addEventListener('mousedown', e => {
            if (this.isAnimating) this.isAnimating = false;
            const hitNode = this.getNodeAt(e.clientX, e.clientY);

            if (hitNode) {
                this.dragNode = hitNode;
                this.selectedNode = hitNode;
                this.showDetail(hitNode);
            } else {
                this.isPanning = true;
                this.startPanX = e.clientX - this.panX;
                this.startPanY = e.clientY - this.panY;
                this.canvas.classList.add('grabbing');
            }
        });

        // Mousemove
        window.addEventListener('mousemove', e => {
            const rect = this.canvas.getBoundingClientRect();
            if (this.dragNode) {
                this.dragNode.x = (e.clientX - rect.left - this.panX) / this.zoom;
                this.dragNode.y = (e.clientY - rect.top - this.panY) / this.zoom;
            } else if (this.isPanning) {
                this.panX = e.clientX - this.startPanX;
                this.panY = e.clientY - this.startPanY;
            } else {
                const hit = this.getNodeAt(e.clientX, e.clientY);
                if (hit !== this.hoveredNode) {
                    this.hoveredNode = hit;
                }
                this.canvas.style.cursor = hit ? 'pointer' : 'grab';
            }
        });

        // Mouseup
        window.addEventListener('mouseup', () => {
            this.dragNode = null;
            this.isPanning = false;
            this.canvas.classList.remove('grabbing');
        });

        // Double click
        this.canvas.addEventListener('dblclick', e => {
            const hit = this.getNodeAt(e.clientX, e.clientY);
            if (hit) {
                const targetX = (this.width / 2) - hit.x * 1.4;
                const targetY = (this.height / 2) - hit.y * 1.4;
                this.animateViewportTo(targetX, targetY, 1.4);
            } else {
                this.fitToScreen(true);
            }
        });

        // Mouse Wheel
        this.canvas.addEventListener('wheel', e => {
            e.preventDefault();
            if (this.isAnimating) this.isAnimating = false;

            if (this.wheelMode === 'pan' && !e.ctrlKey) {
                this.panX -= e.deltaX;
                this.panY -= e.deltaY;
            } else {
                const zoomFactor = e.deltaY < 0 ? 1.09 : 0.917;
                const rect = this.canvas.getBoundingClientRect();
                const mouseX = e.clientX - rect.left;
                const mouseY = e.clientY - rect.top;

                const nextZoom = Math.min(Math.max(this.zoom * zoomFactor, 0.3), 3.5);
                this.panX = mouseX - (mouseX - this.panX) * (nextZoom / this.zoom);
                this.panY = mouseY - (mouseY - this.panY) * (nextZoom / this.zoom);
                this.zoom = nextZoom;
            }
        }, { passive: false });

        // Keyboard
        window.addEventListener('keydown', e => {
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
            const step = 60;
            if (e.key === 'ArrowUp' || e.key === 'w' || e.key === 'W') {
                this.panY += step;
            } else if (e.key === 'ArrowDown' || e.key === 's' || e.key === 'S') {
                this.panY -= step;
            } else if (e.key === 'ArrowLeft' || e.key === 'a' || e.key === 'A') {
                this.panX += step;
            } else if (e.key === 'ArrowRight' || e.key === 'd' || e.key === 'D') {
                this.panX -= step;
            } else if (e.key === '+' || e.key === '=') {
                this.zoomIn();
            } else if (e.key === '-' || e.key === '_') {
                this.zoomOut();
            } else if (e.key === '0' || e.key === ' ') {
                this.fitToScreen(true);
            }
        });

        // Touch
        let touchStartDist = 0;
        this.canvas.addEventListener('touchstart', e => {
            if (e.touches.length === 1) {
                const t = e.touches[0];
                const hit = this.getNodeAt(t.clientX, t.clientY);
                if (hit) {
                    this.dragNode = hit;
                    this.selectedNode = hit;
                    this.showDetail(hit);
                } else {
                    this.isPanning = true;
                    this.startPanX = t.clientX - this.panX;
                    this.startPanY = t.clientY - this.panY;
                }
            } else if (e.touches.length === 2) {
                this.isPanning = false;
                this.dragNode = null;
                const dx = e.touches[0].clientX - e.touches[1].clientX;
                const dy = e.touches[0].clientY - e.touches[1].clientY;
                touchStartDist = Math.hypot(dx, dy);
            }
        }, { passive: false });

        this.canvas.addEventListener('touchmove', e => {
            e.preventDefault();
            if (e.touches.length === 1) {
                const t = e.touches[0];
                if (this.dragNode) {
                    const rect = this.canvas.getBoundingClientRect();
                    this.dragNode.x = (t.clientX - rect.left - this.panX) / this.zoom;
                    this.dragNode.y = (t.clientY - rect.top - this.panY) / this.zoom;
                } else if (this.isPanning) {
                    this.panX = t.clientX - this.startPanX;
                    this.panY = t.clientY - this.startPanY;
                }
            } else if (e.touches.length === 2) {
                const dx = e.touches[0].clientX - e.touches[1].clientX;
                const dy = e.touches[0].clientY - e.touches[1].clientY;
                const dist = Math.hypot(dx, dy);
                if (touchStartDist > 0) {
                    const scaleFactor = dist / touchStartDist;
                    const nextZoom = Math.min(Math.max(this.zoom * scaleFactor, 0.3), 3.5);
                    const rect = this.canvas.getBoundingClientRect();
                    const midX = (e.touches[0].clientX + e.touches[1].clientX) / 2 - rect.left;
                    const midY = (e.touches[0].clientY + e.touches[1].clientY) / 2 - rect.top;
                    this.panX = midX - (midX - this.panX) * (nextZoom / this.zoom);
                    this.panY = midY - (midY - this.panY) * (nextZoom / this.zoom);
                    this.zoom = nextZoom;
                    touchStartDist = dist;
                }
            }
        }, { passive: false });

        this.canvas.addEventListener('touchend', () => {
            this.isPanning = false;
            this.dragNode = null;
            touchStartDist = 0;
        });

        // Minimap click
        if (this.minimapCanvas) {
            this.minimapCanvas.addEventListener('click', e => {
                const rect = this.minimapCanvas.getBoundingClientRect();
                const mx = e.clientX - rect.left;
                const my = e.clientY - rect.top;

                const minX = 0, maxX = 1000, minY = 20, maxY = 750;
                const mW = this.minimapCanvas.width;
                const mH = this.minimapCanvas.height;
                const scaleX = (mW - 16) / (maxX - minX);
                const scaleY = (mH - 16) / (maxY - minY);
                const scale = Math.min(scaleX, scaleY);
                const offX = (mW - (maxX - minX) * scale) / 2;
                const offY = (mH - (maxY - minY) * scale) / 2;

                const worldX = (mx - offX) / scale + minX;
                const worldY = (my - offY) / scale + minY;

                const targetX = (this.width / 2) - worldX * this.zoom;
                const targetY = (this.height / 2) - worldY * this.zoom;
                this.animateViewportTo(targetX, targetY, this.zoom);
            });
        }
    }
}
