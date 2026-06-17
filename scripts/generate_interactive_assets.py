"""Generate interactive assets for the LensFit knowledge vault.

- knowledge-explorer.html: a D3.js force-directed graph of all notes and links.
- 90-maps/Learning Path.canvas: an Obsidian Canvas timeline of learning chapters.

Run from repo root:

    python scripts/generate_interactive_assets.py
"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

VAULT = Path("OpticKnowledgeSpace")
VISUALS_DIR = VAULT / "attachments" / "visuals"
LINK_RE = re.compile(r"(?<!\!)\[\[([^\]]+)\]\]")
PIPE = re.compile(r"(?<!\\)\|")

FOLDER_COLORS = {
    "00-inbox": "#9ca3af",
    "10-concepts": "#4ade80",
    "20-formulas": "#60a5fa",
    "30-domains": "#f87171",
    "40-devices": "#fbbf24",
    "50-learning": "#a78bfa",
    "80-sources": "#f472b6",
    "90-maps": "#22d3ee",
    "README.md": "#e5e7eb",
    "plan.md": "#e5e7eb",
}


def normalize_target(raw: str) -> str:
    target = (
        PIPE.split(raw.replace("\\|", "|"), 1)[0]
        .split("#", 1)[0]
        .strip()
        .replace("\\", "/")
    )
    return target


def build_graph() -> dict:
    nodes: dict[str, dict] = {}
    edges: list[dict] = []
    for md in sorted(VAULT.rglob("*.md")):
        rel = md.relative_to(VAULT)
        rel_key = str(rel.with_suffix("")).replace("\\", "/")
        if rel_key.startswith("copilot/") or ".obsidian" in rel_key:
            continue
        folder = rel.parts[0] if rel.parts else ""
        text = md.read_text(encoding="utf-8")
        title = rel.stem
        status = "unknown"
        if text.startswith("---"):
            try:
                fm = text.split("---", 2)[1]
            except IndexError:
                fm = ""
            for line in fm.splitlines():
                if line.strip().startswith("title:"):
                    title = line.split(":", 1)[1].strip().strip('"').strip("'")
                if line.strip().startswith("status:"):
                    status = line.split(":", 1)[1].strip().strip('"').strip("'")
        nodes[rel_key] = {
            "id": rel_key,
            "title": title,
            "folder": folder,
            "status": status,
            "path": str(rel).replace("\\", "/"),
        }

    for rel_key, node in nodes.items():
        md = VAULT / node["path"]
        text = md.read_text(encoding="utf-8")
        for m in LINK_RE.finditer(text):
            target = normalize_target(m.group(1))
            # Resolve target to a known node key
            resolved = None
            if target in nodes:
                resolved = target
            elif (target + ".md") in nodes:
                resolved = target + ".md"
            else:
                # Try same-folder bare target
                src_folder = Path(rel_key).parent
                candidate = str(src_folder / target).replace("\\", "/")
                if candidate in nodes:
                    resolved = candidate
            if resolved and resolved != rel_key:
                edges.append({"source": rel_key, "target": resolved})

    return {"nodes": list(nodes.values()), "links": edges}


def generate_html(graph: dict) -> Path:
    VISUALS_DIR.mkdir(parents=True, exist_ok=True)
    out = VISUALS_DIR / "knowledge-explorer.html"
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>LensFit Knowledge Explorer</title>
  <script src="https://d3js.org/d3.v7.min.js"></script>
  <style>
    :root {{ color-scheme: light dark; }}
    body {{ margin: 0; font-family: "Microsoft YaHei", "PingFang SC", sans-serif; overflow: hidden; background: #f8fafc; }}
    #sidebar {{ position: fixed; top: 0; left: 0; width: 320px; height: 100vh; background: #ffffff; border-right: 1px solid #e2e8f0; padding: 16px; box-sizing: border-box; overflow-y: auto; z-index: 2; }}
    #sidebar h1 {{ font-size: 18px; margin: 0 0 12px; }}
    #search {{ width: 100%; padding: 8px; border: 1px solid #cbd5e1; border-radius: 6px; margin-bottom: 12px; box-sizing: border-box; }}
    .legend {{ display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 12px; font-size: 12px; }}
    .legend span {{ display: flex; align-items: center; gap: 4px; }}
    .dot {{ width: 10px; height: 10px; border-radius: 50%; display: inline-block; }}
    #info h3 {{ margin: 16px 0 8px; font-size: 14px; color: #475569; }}
    #info .stat {{ font-size: 12px; color: #64748b; margin-bottom: 8px; }}
    #info a {{ color: #2563eb; text-decoration: none; }}
    #info a:hover {{ text-decoration: underline; }}
    #graph {{ position: fixed; top: 0; left: 320px; right: 0; bottom: 0; }}
    svg {{ width: 100%; height: 100%; }}
    .node circle {{ stroke: #fff; stroke-width: 1.5px; cursor: pointer; }}
    .node text {{ pointer-events: none; font-size: 10px; fill: #334155; }}
    .link {{ stroke: #94a3b8; stroke-opacity: 0.5; }}
    .controls {{ position: fixed; bottom: 16px; right: 16px; display: flex; gap: 8px; z-index: 3; }}
    .controls button {{ padding: 8px 12px; border: 1px solid #cbd5e1; background: #fff; border-radius: 6px; cursor: pointer; }}
    @media (prefers-color-scheme: dark) {{
      body {{ background: #0f172a; }}
      #sidebar {{ background: #1e293b; border-color: #334155; color: #e2e8f0; }}
      #search {{ background: #0f172a; border-color: #475569; color: #e2e8f0; }}
      .node text {{ fill: #cbd5e1; }}
    }}
  </style>
</head>
<body>
  <div id="sidebar">
    <h1>LensFit 知识库探索器</h1>
    <input id="search" type="text" placeholder="搜索笔记标题...">
    <div class="legend" id="legend"></div>
    <div id="info">
      <p class="stat">节点数：{len(graph['nodes'])} · 连接数：{len(graph['links'])}</p>
      <p>点击节点查看详情、入链和出链。</p>
    </div>
  </div>
  <div id="graph"></div>
  <div class="controls">
    <button onclick="resetZoom()">重置视图</button>
    <button onclick="toggleLabels()">切换标签</button>
  </div>

  <script>
    const data = {json.dumps(graph, ensure_ascii=False)};
    const folderColors = {json.dumps(FOLDER_COLORS, ensure_ascii=False)};

    const width = document.getElementById('graph').clientWidth;
    const height = document.getElementById('graph').clientHeight;

    const svg = d3.select('#graph').append('svg')
      .attr('viewBox', [0, 0, width, height]);

    const g = svg.append('g');

    const zoom = d3.zoom()
      .scaleExtent([0.1, 4])
      .on('zoom', (event) => g.attr('transform', event.transform));
    svg.call(zoom);

    const simulation = d3.forceSimulation(data.nodes)
      .force('link', d3.forceLink(data.links).id(d => d.id).distance(80))
      .force('charge', d3.forceManyBody().strength(-120))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collide', d3.forceCollide().radius(12));

    const link = g.append('g').attr('class', 'links')
      .selectAll('line')
      .data(data.links)
      .join('line')
      .attr('class', 'link')
      .attr('stroke-width', 1);

    const node = g.append('g').attr('class', 'nodes')
      .selectAll('g')
      .data(data.nodes)
      .join('g')
      .attr('class', 'node')
      .call(d3.drag()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended));

    node.append('circle')
      .attr('r', d => d.folder === '50-learning' || d.folder === '90-maps' ? 8 : 5)
      .attr('fill', d => folderColors[d.folder] || '#94a3b8');

    let labelsVisible = true;
    const labels = node.append('text')
      .attr('dx', 10)
      .attr('dy', 3)
      .text(d => d.title);

    node.on('click', (event, d) => showInfo(d));

    simulation.on('tick', () => {{
      link
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y);
      node.attr('transform', d => `translate(${{d.x}},${{d.y}})`);
    }});

    function dragstarted(event, d) {{
      if (!event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x; d.fy = d.y;
    }}
    function dragged(event, d) {{ d.fx = event.x; d.fy = event.y; }}
    function dragended(event, d) {{
      if (!event.active) simulation.alphaTarget(0);
      d.fx = null; d.fy = null;
    }}

    function showInfo(d) {{
      const incoming = data.links.filter(l => l.target.id === d.id).map(l => l.source.title);
      const outgoing = data.links.filter(l => l.source.id === d.id).map(l => l.target.title);
      const incomingHtml = incoming.length ? '<ul>' + incoming.slice(0, 20).map(t => `<li>${{t}}</li>`).join('') + (incoming.length > 20 ? '<li>...</li>' : '') + '</ul>' : '<p class="stat">无</p>';
      const outgoingHtml = outgoing.length ? '<ul>' + outgoing.slice(0, 20).map(t => `<li>${{t}}</li>`).join('') + (outgoing.length > 20 ? '<li>...</li>' : '') + '</ul>' : '<p class="stat">无</p>';
      document.getElementById('info').innerHTML = `
        <h2>${{d.title}}</h2>
        <p class="stat">文件夹：${{d.folder}} · 状态：${{d.status}}</p>
        <h3>入链 (${{incoming.length}})</h3>${{incomingHtml}}
        <h3>出链 (${{outgoing.length}})</h3>${{outgoingHtml}}
        <p><a href="${{d.path}}" target="_blank">在 Obsidian 中打开</a></p>
      `;
      // Highlight neighbors
      node.selectAll('circle').attr('opacity', n => (n.id === d.id || incoming.includes(n.title) || outgoing.includes(n.title)) ? 1 : 0.2);
      link.attr('stroke-opacity', l => (l.source.id === d.id || l.target.id === d.id) ? 1 : 0.05);
    }}

    // Legend
    const legend = document.getElementById('legend');
    Object.entries(folderColors).forEach(([folder, color]) => {{
      if (data.nodes.some(n => n.folder === folder)) {{
        legend.innerHTML += `<span><span class="dot" style="background:${{color}}"></span>${{folder}}</span>`;
      }}
    }});

    // Search
    document.getElementById('search').addEventListener('input', (e) => {{
      const term = e.target.value.toLowerCase();
      node.attr('opacity', d => d.title.toLowerCase().includes(term) ? 1 : 0.1);
      link.attr('stroke-opacity', term ? 0.05 : 0.5);
    }});

    function resetZoom() {{
      svg.transition().duration(750).call(zoom.transform, d3.zoomIdentity);
    }}
    function toggleLabels() {{
      labelsVisible = !labelsVisible;
      labels.attr('display', labelsVisible ? 'block' : 'none');
    }}
  </script>
</body>
</html>"""
    out.write_text(html, encoding="utf-8")
    return out


def generate_canvas() -> Path:
    """Create an Obsidian Canvas for the learning path timeline."""
    canvas_path = VAULT / "90-maps" / "Learning Path.canvas"
    # Allow specific canvas files to be tracked by unignoring in .gitignore later
    chapters = []
    learning_dir = VAULT / "50-learning"
    for md in sorted(learning_dir.glob("??-*.md")):
        text = md.read_text(encoding="utf-8")
        title = md.stem
        if text.startswith("---"):
            for line in text.split("---", 2)[1].splitlines():
                if line.strip().startswith("title:"):
                    title = line.split(":", 1)[1].strip().strip('"').strip("'")
        try:
            num = int(md.stem.split("-", 1)[0])
        except ValueError:
            num = 99
        chapters.append({"num": num, "file": f"50-learning/{md.name}", "title": title})

    nodes = []
    edges = []
    x = -400
    y = 0
    # Title node
    nodes.append({
        "id": "title",
        "type": "text",
        "text": "# LensFit 学习路径\n\n按阶段拖动浏览，点击卡片进入对应章节。",
        "x": -600,
        "y": -200,
        "width": 500,
        "height": 150,
    })

    phases = [
        (0, "入门", -400, "#dcfce7"),
        (10, "匹配", 600, "#dbeafe"),
        (12, "像质", 1400, "#fce7f3"),
        (14, "工程", 1900, "#fef9c3"),
        (15, "进阶", 2500, "#f3e8ff"),
        (16, "光谱", 3400, "#fee2e2"),
    ]
    phase_index = 0
    for ch in chapters:
        while phase_index + 1 < len(phases) and ch["num"] >= phases[phase_index + 1][0]:
            phase_index += 1
        x = phases[phase_index][2] + (ch["num"] % 10) * 220
        y = 80 if (ch["num"] % 2) == 0 else 280
        node_id = f"ch{ch['num']}"
        nodes.append({
            "id": node_id,
            "type": "file",
            "file": ch["file"],
            "x": x,
            "y": y,
            "width": 180,
            "height": 120,
        })
        if len(nodes) > 2:
            edges.append({"id": f"e{len(edges)}", "fromNode": nodes[-2]["id"], "fromSide": "right", "toNode": node_id, "toSide": "left"})

    # Phase labels
    for start, label, x_pos, color in phases:
        nodes.append({
            "id": f"phase-{label}",
            "type": "text",
            "text": f"<h2 style='color:{color};border-left:6px solid {color};padding-left:8px'>{label}阶段</h2>",
            "x": x_pos,
            "y": -120,
            "width": 200,
            "height": 60,
        })

    # Visual gallery node
    nodes.append({
        "id": "visuals",
        "type": "file",
        "file": "90-maps/Visual Index.md",
        "x": 3500,
        "y": -200,
        "width": 220,
        "height": 100,
    })

    canvas = {"nodes": nodes, "edges": edges}
    canvas_path.write_text(json.dumps(canvas, ensure_ascii=False, indent=2), encoding="utf-8")
    return canvas_path


def main():
    graph = build_graph()
    html_path = generate_html(graph)
    canvas_path = generate_canvas()
    print(f"Generated {html_path}")
    print(f"Generated {canvas_path}")


if __name__ == "__main__":
    main()
