import json
import re

dashboard_path = r"C:\Users\zzx05\Hermes-Automation\reports\CS408_Visual_Dashboard.html"
graph_data_path = r"C:\Users\zzx05\Hermes-Automation\reports\master_408_graph_data.json"

with open(dashboard_path, "r", encoding="utf-8") as f:
    html = f.read()

with open(graph_data_path, "r", encoding="utf-8") as f:
    graph_data = json.load(f)

# Format master nodes and links as clean JS arrays
nodes_js = json.dumps(graph_data["nodes"], ensure_ascii=False, indent=12)
links_js = json.dumps(graph_data["links"], ensure_ascii=False, indent=12)

# Update the graph controls in HTML to include category filter pills and search box
old_controls = """            <div class="graph-controls">
                <div><span class="badge-legend" style="background:#3b82f6;"></span>数据结构 (45分)</div>
                <div><span class="badge-legend" style="background:#8b5cf6;"></span>组成原理 (45分)</div>
                <div><span class="badge-legend" style="background:#10b981;"></span>操作系统 (35分)</div>
                <div><span class="badge-legend" style="background:#f59e0b;"></span>计算机网络 (25分)</div>
                <div><span class="badge-legend" style="background:#f43f5e;"></span>核心技巧/高分模板</div>
            </div>"""

new_controls = """            <div class="graph-controls" style="display:flex; flex-direction:column; gap:8px;">
                <div style="display:flex; align-items:center; gap:8px;">
                    <input type="text" id="graph-search" placeholder="🔍 检索考点 (如: Cache, PV, 快排, 拥塞控制)..." 
                           style="background:#0f172a; border:1px solid #475569; color:#f8fafc; padding:4px 10px; border-radius:6px; font-size:0.75rem; width:260px; outline:none;" 
                           oninput="filterGraphSearch(this.value)">
                    <button onclick="resetGraphView()" style="background:#334155; color:#cbd5e1; border:none; padding:4px 8px; border-radius:4px; font-size:0.72rem; cursor:pointer;">重置视图</button>
                    <span style="font-size:0.72rem; color:#94a3b8;">支持滚轮平滑缩放与鼠标拖拽</span>
                </div>
                <div style="display:flex; gap:12px; font-size:0.75rem;">
                    <div style="cursor:pointer;" onclick="filterGraphCategory('all')"><span class="badge-legend" style="background:#38bdf8;"></span>全考纲拓扑 (47个核心点)</div>
                    <div style="cursor:pointer;" onclick="filterGraphCategory('ds')"><span class="badge-legend" style="background:#3b82f6;"></span>数据结构 (45分)</div>
                    <div style="cursor:pointer;" onclick="filterGraphCategory('coa')"><span class="badge-legend" style="background:#8b5cf6;"></span>组成原理 (45分)</div>
                    <div style="cursor:pointer;" onclick="filterGraphCategory('os')"><span class="badge-legend" style="background:#10b981;"></span>操作系统 (35分)</div>
                    <div style="cursor:pointer;" onclick="filterGraphCategory('cn')"><span class="badge-legend" style="background:#f59e0b;"></span>计算机网络 (25分)</div>
                    <div style="cursor:pointer;" onclick="filterGraphCategory('cross')"><span class="badge-legend" style="background:#f43f5e;"></span>跨学科贯通关联 (7条)</div>
                </div>
            </div>"""

if old_controls in html:
    html = html.replace(old_controls, new_controls)
else:
    print("Warning: old_controls not found for replacement.")

# Replace the graph implementation script with modern pan/zoom, force physics & detail inspection
old_js_start = "// Force-Directed Graph Implementation"
old_js_idx = html.find(old_js_start)

if old_js_idx != -1:
    new_js = f"""// Force-Directed Graph Implementation (Master Syllabus Grade)
        const canvas = document.getElementById('graph-canvas');
        const ctx = canvas.getContext('2d');
        let width, height;

        const allNodes = {nodes_js};
        const allLinks = {links_js};

        let nodes = [...allNodes];
        let links = [...allLinks];

        // Zoom & Pan state
        let zoom = 0.95;
        let panX = 40;
        let panY = 20;
        let isPanning = false;
        let startPanX = 0, startPanY = 0;

        function resize() {{
            if (!canvas.parentElement) return;
            width = canvas.parentElement.clientWidth - 380;
            height = canvas.parentElement.clientHeight;
            if (width > 50 && height > 50) {{
                canvas.width = width;
                canvas.height = height;
            }}
        }}
        window.addEventListener('resize', resize);
        setTimeout(resize, 100);

        let selectedNode = null;
        let dragNode = null;
        let hoveredNode = null;
        let activeCategory = 'all';

        function resetGraphView() {{
            zoom = 0.95;
            panX = 40;
            panY = 20;
            selectedNode = null;
            nodes = [...allNodes];
            links = [...allLinks];
        }}

        function filterGraphCategory(cat) {{
            activeCategory = cat;
            if (cat === 'all') {{
                nodes = [...allNodes];
                links = [...allLinks];
            }} else if (cat === 'cross') {{
                const crossLinkSources = new Set(allLinks.filter(l => l.cross).map(l => l.source));
                const crossLinkTargets = new Set(allLinks.filter(l => l.cross).map(l => l.target));
                nodes = allNodes.filter(n => crossLinkSources.has(n.id) || crossLinkTargets.has(n.id));
                links = allLinks.filter(l => l.cross);
            }} else {{
                nodes = allNodes.filter(n => n.cat === cat || n.cat === 'center');
                const nodeIds = new Set(nodes.map(n => n.id));
                links = allLinks.filter(l => nodeIds.has(l.source) && nodeIds.has(l.target));
            }}
        }}

        function filterGraphSearch(query) {{
            const q = query.toLowerCase().trim();
            if (!q) {{
                filterGraphCategory(activeCategory);
                return;
            }}
            const match = allNodes.find(n => n.name.toLowerCase().includes(q) || n.desc.toLowerCase().includes(q));
            if (match) {{
                selectedNode = match;
                showDetail(match);
                // Center on node smoothly
                panX = (width / 2) - match.x * zoom;
                panY = (height / 2) - match.y * zoom;
            }}
        }}

        // Canvas Zoom via Mouse Wheel
        canvas.addEventListener('wheel', e => {{
            e.preventDefault();
            const zoomFactor = 1.08;
            const mouseX = e.clientX - canvas.getBoundingClientRect().left;
            const mouseY = e.clientY - canvas.getBoundingClientRect().top;

            if (e.deltaY < 0) {{
                if (zoom < 2.5) {{
                    panX = mouseX - (mouseX - panX) * zoomFactor;
                    panY = mouseY - (mouseY - panY) * zoomFactor;
                    zoom *= zoomFactor;
                }}
            }} else {{
                if (zoom > 0.45) {{
                    panX = mouseX - (mouseX - panX) / zoomFactor;
                    panY = mouseY - (mouseY - panY) / zoomFactor;
                    zoom /= zoomFactor;
                }}
            }}
        }}, {{ passive: false }});

        function draw() {{
            if (!canvas.width || !canvas.height) return;
            ctx.clearRect(0, 0, width, height);

            ctx.save();
            ctx.translate(panX, panY);
            ctx.scale(zoom, zoom);

            // Draw links
            links.forEach(link => {{
                const s = nodes.find(n => n.id === link.source);
                const t = nodes.find(n => n.id === link.target);
                if (s && t) {{
                    ctx.beginPath();
                    ctx.moveTo(s.x, s.y);
                    ctx.lineTo(t.x, t.y);
                    if (link.cross) {{
                        ctx.strokeStyle = 'rgba(244, 63, 94, 0.7)';
                        ctx.setLineDash([5, 5]);
                        ctx.lineWidth = 2.0;
                    }} else {{
                        ctx.strokeStyle = 'rgba(148, 163, 184, 0.28)';
                        ctx.setLineDash([]);
                        ctx.lineWidth = 1.4;
                    }}
                    ctx.stroke();

                    // Optional label on cross link
                    if (link.cross && zoom > 0.8) {{
                        const mx = (s.x + t.x) / 2;
                        const my = (s.y + t.y) / 2;
                        ctx.fillStyle = '#fda4af';
                        ctx.font = '9px sans-serif';
                        ctx.textAlign = 'center';
                        ctx.fillText(link.label || '跨学科贯通', mx, my - 4);
                    }}
                }}
            }});
            ctx.setLineDash([]);

            // Draw nodes
            nodes.forEach(node => {{
                const isSelected = (selectedNode === node);
                const isHovered = (hoveredNode === node);

                // Outer aura
                ctx.beginPath();
                ctx.arc(node.x, node.y, node.r + 6, 0, Math.PI * 2);
                ctx.fillStyle = node.color + '22';
                ctx.fill();

                // Core Node
                ctx.beginPath();
                ctx.arc(node.x, node.y, node.r, 0, Math.PI * 2);
                ctx.fillStyle = node.color;
                ctx.shadowColor = node.color;
                ctx.shadowBlur = isSelected ? 22 : (isHovered ? 14 : 6);
                ctx.fill();
                ctx.shadowBlur = 0;

                // Border
                ctx.strokeStyle = isSelected ? '#38bdf8' : '#ffffff';
                ctx.lineWidth = isSelected ? 3.5 : 1.5;
                ctx.stroke();

                // Text label
                ctx.fillStyle = '#f8fafc';
                ctx.font = (node.r >= 22 ? 'bold 11px' : '10px') + ' sans-serif';
                ctx.textAlign = 'center';
                ctx.fillText(node.name, node.x, node.y + node.r + 13);
            }});

            ctx.restore();
            requestAnimationFrame(draw);
        }}

        draw();

        // Mouse Drag / Pan / Click Handler
        canvas.addEventListener('mousedown', e => {{
            const rect = canvas.getBoundingClientRect();
            const clickX = (e.clientX - rect.left - panX) / zoom;
            const clickY = (e.clientY - rect.top - panY) / zoom;

            let hitNode = null;
            for (let n of nodes) {{
                const dist = Math.hypot(n.x - clickX, n.y - clickY);
                if (dist <= n.r + 4) {{
                    hitNode = n;
                    break;
                }}
            }}

            if (hitNode) {{
                dragNode = hitNode;
                selectedNode = hitNode;
                showDetail(hitNode);
            }} else {{
                isPanning = true;
                startPanX = e.clientX - panX;
                startPanY = e.clientY - panY;
            }}
        }});

        window.addEventListener('mousemove', e => {{
            const rect = canvas.getBoundingClientRect();
            if (dragNode) {{
                dragNode.x = (e.clientX - rect.left - panX) / zoom;
                dragNode.y = (e.clientY - rect.top - panY) / zoom;
            }} else if (isPanning) {{
                panX = e.clientX - startPanX;
                panY = e.clientY - startPanY;
            }}
        }});

        window.addEventListener('mouseup', () => {{
            dragNode = null;
            isPanning = false;
        }});

        function showDetail(node) {{
            document.getElementById('drawer-node-name').innerText = node.name;
            let html = `<p style="line-height:1.7; color:#f1f5f9; font-size:0.9rem;">${{node.desc}}</p>`;
            
            // Find connected neighbors
            const neighbors = [];
            links.forEach(l => {{
                if (l.source === node.id) {{
                    const targetNode = allNodes.find(n => n.id === l.target);
                    if (targetNode) neighbors.push({{ name: targetNode.name, cross: l.cross, label: l.label }});
                }} else if (l.target === node.id) {{
                    const sourceNode = allNodes.find(n => n.id === l.source);
                    if (sourceNode) neighbors.push({{ name: sourceNode.name, cross: l.cross, label: l.label }});
                }}
            }});

            if (neighbors.length > 0) {{
                html += `<h5 style="margin-top:18px; margin-bottom:8px; color:var(--accent-amber); font-size:0.85rem;">🔗 关联考点与综合命题链路：</h5><ul style="padding-left:18px; font-size:0.82rem; line-height:1.6; color:#94a3b8;">`;
                neighbors.forEach(nbr => {{
                    if (nbr.cross) {{
                        html += `<li style="color:#f43f5e; margin-bottom:4px;"><strong>[跨学科考查]</strong> ${{nbr.name}} ${{nbr.label ? '— ' + nbr.label : ''}}</li>`;
                    }} else {{
                        html += `<li>${{nbr.name}}</li>`;
                    }}
                }});
                html += `</ul>`;
            }}

            document.getElementById('drawer-node-body').innerHTML = html;
        }}
    </script>
</body>
</html>"""

    html = html[:old_js_idx] + new_js

with open(dashboard_path, "w", encoding="utf-8") as f:
    f.write(html)

print("Successfully injected 47-node Master Knowledge Graph into CS408_Visual_Dashboard.html!")
