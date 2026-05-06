"""Regenerate the L2 graph (nodes, edges, index.html) from canonical entries.

The v5 entries in L2/entries/ are the single source of truth.
Graph nodes, edges, and the D3.js visualization are derived views
that are rebuilt from entries after every write.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


def _now_iso():
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()


def _parse_md(path: Path):
    import yaml
    if not path.exists():
        return {}, ""
    text = path.read_text(encoding="utf-8")
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            try:
                fm = yaml.safe_load(parts[1]) or {}
            except Exception:
                fm = {}
            return fm, parts[2] if len(parts) > 2 else ""
    return {}, text


def _write_md(path: Path, fm: dict, body: str):
    import yaml
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "---",
        yaml.dump(dict(fm), default_flow_style=False, allow_unicode=True).rstrip(),
        "---",
        str(body).lstrip("\n"),
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


# Shape/color mapping for entry roles in the vis-network graph
_ENTRY_ROLE_STYLE = {
    "claim":    {"shape": "star",   "color": "#4C72B0"},
    "system":   {"shape": "dot",    "color": "#55A868"},
    "method":   {"shape": "box",    "color": "#C44E52"},
    "pitfall":  {"shape": "triangle", "color": "#DD8452"},
    "question": {"shape": "diamond","color": "#937860"},
}

# Trust/status color overrides
_STATUS_COLOR = {
    "verified": "#3fb950",
    "consistent": "#d29922",
    "unverified": "#999999",
    "failed": "#f85149",
    "conjectured": "#f85149",
}


def _entry_to_js_node(entry_id: str, fm: dict[str, Any]) -> dict[str, Any]:
    """Convert a v5 entry frontmatter to a vis-network node dict."""
    role = str(fm.get("role", "claim"))
    style = _ENTRY_ROLE_STYLE.get(role, {"shape": "dot", "color": "#999999"})
    status = str(fm.get("status", "unverified"))
    color = _STATUS_COLOR.get(status, "#999999")

    # Build label: use title, truncated for display
    label = str(fm.get("title", entry_id))
    if len(label) > 80:
        label = label[:77] + "..."

    # Collect expression text
    expression = ""
    if role == "claim":
        expression = str(fm.get("mathematical_expression", ""))
    elif role == "system":
        expression = str(fm.get("formula_or_identifier", ""))

    # Collect meaning text
    meaning = ""
    if role == "claim":
        meaning = str(fm.get("statement", ""))
    elif role == "pitfall":
        meaning = str(fm.get("symptom", ""))
    elif role == "question":
        meaning = str(fm.get("question_statement", ""))
    elif role == "method":
        meaning = ", ".join(fm.get("toolchain", [])) if fm.get("toolchain") else ""
    elif role == "system":
        meaning = str(fm.get("formula_or_identifier", ""))

    return {
        "id": entry_id,
        "label": label,
        "type": role,
        "domain": "entries",
        "color": color,
        "shape": style["shape"],
        "trust": status,
        "expression": expression[:200],
        "meaning": meaning[:300],
        "regime": str(fm.get("regime", ""))[:200],
        "source": str(fm.get("source_ref", ""))[:120],
        "energy": "",
        "version": fm.get("version", 1),
    }


def _parse_entry_relationships(fm: dict[str, Any], body: str) -> list[dict[str, Any]]:
    """Parse relationships from entry body text and frontmatter."""
    edges: list[dict[str, Any]] = []
    from_id = str(fm.get("entry_id", ""))

    # Parse body relationships: "- edge_type: target_id"
    rel_section = body.find("## Relationships")
    if rel_section != -1:
        rel_text = body[rel_section:]
        for match in re.finditer(r'[-*]\s+(\w+)\s*:\s*([a-z][a-z0-9-]+)', rel_text):
            edge_type = match.group(1)
            to_id = match.group(2).strip()
            # Skip non-edge annotations
            if edge_type in ("note",):
                continue
            edge_id = f"e-{from_id}--{edge_type}--{to_id}"
            edges.append({
                "id": edge_id,
                "from": from_id,
                "to": to_id,
                "type": edge_type,
                "label": edge_type,
                "evidence": "",
                "source": f"entry:{from_id}",
                "dashes": False,
                "arrows": "to",
            })

    # Parse frontmatter list fields
    for field, edge_type in [
        ("depends_on_claims", "depends_on"),
        ("affects_methods", "affects"),
    ]:
        values = fm.get(field, [])
        if isinstance(values, str):
            values = [v.strip() for v in values.split(",") if v.strip()]
        if not isinstance(values, list):
            continue
        for v in values:
            v = str(v).strip()
            if not v:
                continue
            edge_id = f"e-{from_id}--{edge_type}--{v}"
            edges.append({
                "id": edge_id,
                "from": from_id,
                "to": v,
                "type": edge_type,
                "label": edge_type,
                "evidence": "",
                "source": f"entry:{from_id}",
                "dashes": False,
                "arrows": "to",
            })

    return edges


def _rebuild_graph_nodes(global_l2: Path) -> int:
    """Rebuild graph/nodes/ from entries. Returns count of nodes written."""
    entries_dir = global_l2 / "entries"
    nodes_dir = global_l2 / "graph" / "nodes"
    nodes_dir.mkdir(parents=True, exist_ok=True)

    count = 0
    for ep in sorted(entries_dir.glob("*.md")):
        if ep.stem.startswith("INDEX"):
            continue
        fm, body = _parse_md(ep)
        entry_id = str(fm.get("entry_id", ep.stem))

        # Build graph node frontmatter
        role = str(fm.get("role", "claim"))
        node_fm: dict[str, Any] = {
            "node_id": entry_id,
            "type": role,
            "title": str(fm.get("title", entry_id)),
            "domain": "entries",
            "trust_basis": str(fm.get("status", "unverified")),
            "trust_scope": str(fm.get("regime", "")),
            "version": fm.get("version", 1),
            "regime_of_validity": str(fm.get("regime", "")),
            "mathematical_expression": str(fm.get("mathematical_expression", ""))[:500],
            "source_ref": str(fm.get("source_ref", ""))[:200],
            "created_at": fm.get("created_at", _now_iso()),
            "updated_at": _now_iso(),
        }

        # Role-specific meaning
        if role == "claim":
            node_fm["physical_meaning"] = str(fm.get("statement", ""))
        elif role == "pitfall":
            node_fm["physical_meaning"] = str(fm.get("symptom", ""))
        elif role == "question":
            node_fm["physical_meaning"] = str(fm.get("question_statement", ""))
        elif role == "method":
            node_fm["physical_meaning"] = ", ".join(fm.get("steps", []))[:500] if fm.get("steps") else ""
        elif role == "system":
            node_fm["physical_meaning"] = str(fm.get("formula_or_identifier", ""))

        node_body = (
            f"# {node_fm['title']}\n\n"
            f"## Physical Meaning\n{node_fm.get('physical_meaning', '')}\n\n"
            f"## Mathematical Expression\n{node_fm.get('mathematical_expression', '')}\n\n"
            f"## Regime and Limits\n{node_fm.get('regime_of_validity', '')}\n\n"
            f"## Source\n{node_fm.get('source_ref', '')}\n"
        )

        _write_md(nodes_dir / f"{entry_id}.md", node_fm, node_body)
        count += 1

    return count


def _rebuild_graph_edges(global_l2: Path) -> int:
    """Rebuild graph/edges/ from entry relationships. Returns count of edges written."""
    entries_dir = global_l2 / "entries"
    edges_dir = global_l2 / "graph" / "edges"
    edges_dir.mkdir(parents=True, exist_ok=True)

    count = 0
    seen_edge_ids: set[str] = set()
    for ep in sorted(entries_dir.glob("*.md")):
        if ep.stem.startswith("INDEX"):
            continue
        fm, body = _parse_md(ep)
        edges = _parse_entry_relationships(fm, body)
        for edge in edges:
            if edge["id"] in seen_edge_ids:
                continue
            seen_edge_ids.add(edge["id"])
            edge_fm = {
                "edge_id": edge["id"],
                "from_node": edge["from"],
                "to_node": edge["to"],
                "type": edge["type"],
                "source_ref": edge.get("source", ""),
                "regime_condition": "",
                "created_at": _now_iso(),
            }
            edge_body = (
                f"# Edge: {edge['from']} --[{edge['type']}]--> {edge['to']}\n\n"
                f"## Evidence\n{edge.get('evidence', '')}\n"
            )
            _write_md(edges_dir / f"{edge['id']}.md", edge_fm, edge_body)
            count += 1

    return count


def _rebuild_graph_html(global_l2: Path) -> None:
    """Regenerate graph/index.html from entries + steps + towers."""
    entries_dir = global_l2 / "entries"
    steps_dir = global_l2 / "graph" / "steps"
    edges_dir = global_l2 / "graph" / "edges"
    towers_dir = global_l2 / "graph" / "towers"
    html_path = global_l2 / "graph" / "index.html"

    # Load entries → nodes
    entries: list[dict[str, Any]] = []
    if entries_dir.is_dir():
        for ep in sorted(entries_dir.glob("*.md")):
            if ep.stem.startswith("INDEX"):
                continue
            fm, body = _parse_md(ep)
            entries.append((fm, body))

    # Build nodes JS
    nodes_js_objects: list[str] = []
    for fm, _ in entries:
        entry_id = str(fm.get("entry_id", ""))
        node = _entry_to_js_node(entry_id, fm)
        nodes_js_objects.append(json.dumps(node, ensure_ascii=False))

    # Load graph edges
    all_edges: list[dict[str, Any]] = []
    if edges_dir.is_dir():
        for ep in sorted(edges_dir.glob("*.md")):
            efm, _ = _parse_md(ep)
            all_edges.append({
                "id": efm.get("edge_id", ep.stem),
                "from": efm.get("from_node", ""),
                "to": efm.get("to_node", ""),
                "type": efm.get("type", ""),
                "label": efm.get("type", ""),
                "evidence": efm.get("evidence", ""),
                "source": efm.get("source_ref", ""),
                "dashes": False,
                "arrows": "to",
            })

    edges_js_objects = [json.dumps(e, ensure_ascii=False) for e in all_edges]

    # Load towers
    towers: list[dict[str, Any]] = []
    if towers_dir.is_dir():
        for tp in sorted(towers_dir.glob("*.md")):
            tfm, _ = _parse_md(tp)
            towers.append({
                "name": tfm.get("name", tp.stem),
                "energy_range": tfm.get("energy_range", ""),
                "layers": tfm.get("layers", []),
            })
    towers_js = json.dumps(towers, ensure_ascii=False)

    # Load steps
    steps: list[dict[str, Any]] = []
    chains: dict[str, list[dict[str, Any]]] = {}
    if steps_dir.is_dir():
        for sp in sorted(steps_dir.glob("*.md")):
            sfm, _ = _parse_md(sp)
            chain_id = str(sfm.get("chain_id", "default"))
            step = {
                "id": sfm.get("step_id", sp.stem),
                "chain_id": chain_id,
                "order": str(sfm.get("order", "0")),
                "input_expr": str(sfm.get("input_expr", "")),
                "output_expr": str(sfm.get("output_expr", "")),
                "transform": str(sfm.get("transform", "")),
                "justification_type": sfm.get("justification_type", ""),
                "justification_detail": str(sfm.get("justification_detail", "")),
                "rigor_level": sfm.get("rigor_level", ""),
                "source_ref": str(sfm.get("source_ref", "")),
                "gap_marker": sfm.get("gap_marker", ""),
                "depends_on_steps": sfm.get("depends_on_steps", []),
            }
            steps.append(step)
            chains.setdefault(chain_id, []).append(step)

    steps_js = json.dumps(steps, ensure_ascii=False)
    chains_js = json.dumps(chains, ensure_ascii=False)

    # Read existing HTML to extract template structure
    if html_path.exists():
        html = html_path.read_text(encoding="utf-8")
    else:
        html = "<html></html>"

    # Replace the JS data arrays using regex
    # nodes = new vis.DataSet([...]);
    html = re.sub(
        r'var nodes = new vis\.DataSet\(\[.*?\]\);',
        f'var nodes = new vis.DataSet([{", ".join(nodes_js_objects)}]);',
        html, count=1, flags=re.DOTALL
    )
    # edges = new vis.DataSet([...]);
    html = re.sub(
        r'var edges = new vis\.DataSet\(\[.*?\]\);',
        f'var edges = new vis.DataSet([{", ".join(edges_js_objects)}]);',
        html, count=1, flags=re.DOTALL
    )
    # towers = [...];
    html = re.sub(
        r'var towers = \[.*?\];',
        f'var towers = {towers_js};',
        html, count=1, flags=re.DOTALL
    )
    # steps = [...];
    html = re.sub(
        r'var steps = \[.*?\];',
        f'var steps = {steps_js};',
        html, count=1, flags=re.DOTALL
    )
    # chains = {...};
    html = re.sub(
        r'var chains = \{.*?\};',
        f'var chains = {chains_js};',
        html, count=1, flags=re.DOTALL
    )

    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(html, encoding="utf-8")


def _rebuild_graph_from_entries(global_l2: Path) -> dict[str, int]:
    """Rebuild all graph artifacts from entries. Returns counts."""
    n_nodes = _rebuild_graph_nodes(global_l2)
    n_edges = _rebuild_graph_edges(global_l2)
    try:
        _rebuild_graph_html(global_l2)
        html_size = (global_l2 / "graph" / "index.html").stat().st_size
    except Exception:
        html_size = 0

    return {
        "nodes": n_nodes,
        "edges": n_edges,
        "html_bytes": html_size,
    }
