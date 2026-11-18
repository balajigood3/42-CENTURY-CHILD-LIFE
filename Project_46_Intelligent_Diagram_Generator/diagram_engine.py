"""Deterministic text-to-diagram conversion with SVG and Mermaid exporters."""
from __future__ import annotations
import html
import re

MAX_NODES = 30

def parse_process(description: str, diagram_type: str = "Flowchart"):
    if not isinstance(description, str) or not description.strip():
        raise ValueError("Please provide a process description.")
    if diagram_type not in {"Flowchart", "Sequence of steps"}:
        raise ValueError("Unsupported diagram layout.")
    raw_lines = [line.strip() for line in description.splitlines() if line.strip()]
    if not raw_lines:
        raise ValueError("No process steps were found.")

    nodes, edges, lookup = [], [], {}
    def get_node(label):
        label = re.sub(r"\s+", " ", label).strip()
        if not label:
            raise ValueError("A diagram node cannot have an empty label.")
        key = label.casefold()
        if key not in lookup:
            if len(nodes) >= MAX_NODES:
                raise ValueError(f"Diagrams are limited to {MAX_NODES} nodes.")
            node_id = f"N{len(nodes)+1}"
            lookup[key] = node_id
            nodes.append({"id": node_id, "label": label})
        return lookup[key]

    previous = None
    for line in raw_lines:
        if "->" in line:
            parts = [part.strip() for part in line.split("->")]
            if len(parts) < 2 or any(not part for part in parts):
                raise ValueError(f"Invalid connection: {line}")
            ids = [get_node(part) for part in parts]
            edges.extend((ids[i], ids[i+1]) for i in range(len(ids)-1))
            previous = ids[-1]
        else:
            current = get_node(line)
            if previous is not None:
                edges.append((previous, current))
            elif nodes and current != nodes[0]["id"]:
                # Plain lines form a sequential process.
                prior_id = nodes[-2]["id"] if len(nodes) > 1 else None
                if prior_id:
                    edges.append((prior_id, current))
            previous = current

    # Remove duplicate edges while preserving order.
    edges = list(dict.fromkeys(edges))
    return nodes, edges

def to_mermaid(nodes, edges):
    if not nodes:
        raise ValueError("At least one node is required.")
    lines = ["flowchart TD"]
    for node in nodes:
        label = node["label"].replace('"', "'")
        lines.append(f'    {node["id"]}["{label}"]')
    for source, target in edges:
        lines.append(f"    {source} --> {target}")
    return "\n".join(lines) + "\n"

def render_svg(nodes, edges, title="Process Diagram"):
    if not nodes:
        raise ValueError("At least one node is required.")
    width, box_h, gap = 900, 76, 54
    margin = 50
    height = margin*2 + len(nodes)*box_h + max(0, len(nodes)-1)*gap
    positions = {node["id"]: (width//2, margin + i*(box_h+gap))
                 for i, node in enumerate(nodes)}
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#52627a"/></marker></defs>',
        '<rect width="100%" height="100%" fill="#f7f9fc"/>',
        f'<text x="{width//2}" y="32" text-anchor="middle" font-family="Arial" font-size="22" font-weight="bold" fill="#17243a">{html.escape(title)}</text>'
    ]
    for source, target in edges:
        if source not in positions or target not in positions:
            raise ValueError("An edge references a node that does not exist.")
        x1, y1 = positions[source]
        x2, y2 = positions[target]
        parts.append(f'<path d="M{x1} {y1+box_h} L{x2} {y2-8}" stroke="#52627a" stroke-width="2" fill="none" marker-end="url(#arrow)"/>')
    for node in nodes:
        x, y = positions[node["id"]]
        label = html.escape(node["label"])
        parts.append(f'<rect x="{x-260}" y="{y}" width="520" height="{box_h}" rx="14" fill="#e8efff" stroke="#4969a8" stroke-width="2"/>')
        parts.append(f'<text x="{x}" y="{y+45}" text-anchor="middle" font-family="Arial" font-size="20" fill="#17243a">{label}</text>')
    parts.append("</svg>")
    return "\n".join(parts)
