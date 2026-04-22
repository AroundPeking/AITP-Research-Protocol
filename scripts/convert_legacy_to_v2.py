"""Convert shallow-migrated legacy topics to full v2 AITP L0-L4 structure.

Usage:
    python scripts/convert_legacy_to_v2.py <topics_root>

Reads each topic's legacy/ subdirectory (created by migrate_legacy_topics.py),
extracts structured data from JSON/JSONL files, and creates proper v2 Markdown
with YAML frontmatter directories: L0/sources, L1/, L3/subplanes, L3/candidates,
L3/tex, L4/.

The legacy/ directory is preserved untouched.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path


def _read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError, OSError):
        return None


def _read_md(path: Path) -> str | None:
    if not path.exists():
        return None
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None


def _read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def _yaml_str(value: str) -> str:
    """Format a string for YAML frontmatter — quote if needed."""
    if not value:
        return '""'
    needs_quote = any(c in value for c in [":", "#", '"', "'", "\n"]) or value in ("true", "false", "null")
    if needs_quote:
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    return value


def _fm_dump(fields: dict) -> str:
    """Dump a dict as YAML frontmatter block."""
    lines = ["---"]
    for k, v in fields.items():
        if v is None:
            continue
        if isinstance(v, bool):
            lines.append(f"{k}: {'true' if v else 'false'}")
        elif isinstance(v, (int, float)):
            lines.append(f"{k}: {v}")
        elif isinstance(v, list):
            if not v:
                lines.append(f"{k}: []")
            else:
                lines.append(f"{k}:")
                for item in v:
                    if isinstance(item, str):
                        lines.append(f'  - "{item}"')
                    else:
                        lines.append(f"  - {item}")
        elif isinstance(v, str):
            lines.append(f"{k}: {_yaml_str(v)}")
        else:
            lines.append(f"{k}: {_yaml_str(str(v))}")
    lines.append("---")
    return "\n".join(lines)


def _safe_filename(name: str) -> str:
    return re.sub(r"[^\w\-.]", "_", name)


def _now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _gather_run_data(legacy_path: Path) -> dict:
    """Gather all L3 run data from legacy directory."""
    runs_dir = legacy_path / "L3" / "runs"
    if not runs_dir.exists():
        return {"runs": [], "all_candidates": [], "all_strategies": [], "latest_synthesis": None}

    runs = []
    all_candidates = []
    all_strategies = []
    latest_synthesis = None
    latest_synthesis_time = None

    for run_dir in sorted(runs_dir.iterdir()):
        if not run_dir.is_dir():
            continue

        run_id = run_dir.name
        candidates = _read_jsonl(run_dir / "candidate_ledger.jsonl")
        strategies = _read_jsonl(run_dir / "strategy_memory.jsonl")
        journal = _read_json(run_dir / "iteration_journal.json")
        journal_md = _read_md(run_dir / "iteration_journal.md")

        iterations = []
        iter_base = run_dir / "iterations"
        if iter_base.exists():
            for iter_dir in sorted(iter_base.iterdir()):
                if not iter_dir.is_dir():
                    continue
                iter_data = {
                    "id": iter_dir.name,
                    "plan_md": _read_md(iter_dir / "plan.md"),
                    "plan_json": _read_json(iter_dir / "plan.contract.json"),
                    "synthesis_md": _read_md(iter_dir / "l3_synthesis.md"),
                    "synthesis_json": _read_json(iter_dir / "l3_synthesis.json"),
                    "l4_return_md": _read_md(iter_dir / "l4_return.md"),
                    "l4_return_json": _read_json(iter_dir / "l4_return.json"),
                }
                iterations.append(iter_data)

                if iter_data["synthesis_json"]:
                    ts = iter_data["synthesis_json"].get("updated_at", "")
                    if ts and (latest_synthesis_time is None or ts > latest_synthesis_time):
                        latest_synthesis_time = ts
                        latest_synthesis = iter_data["synthesis_json"]

        run_data = {
            "run_id": run_id,
            "candidates": candidates,
            "strategies": strategies,
            "journal": journal,
            "journal_md": journal_md,
            "iterations": iterations,
        }
        runs.append(run_data)
        all_candidates.extend(candidates)
        all_strategies.extend(strategies)

    return {
        "runs": runs,
        "all_candidates": all_candidates,
        "all_strategies": all_strategies,
        "latest_synthesis": latest_synthesis,
    }


def convert_l0(topic_path: Path, legacy_path: Path, state: dict) -> int:
    """Convert L0 sources from legacy format to v2."""
    l0_v2 = topic_path / "L0" / "sources"
    l0_legacy = legacy_path / "L0" / "sources"

    count = 0

    if l0_legacy.exists():
        for src_dir in sorted(l0_legacy.iterdir()):
            if not src_dir.is_dir():
                continue
            src_json = _read_json(src_dir / "source.json")
            if not src_json:
                continue

            src_id = src_json.get("source_id", src_dir.name)
            src_type = src_json.get("source_type", "local_note")
            title = src_json.get("title", src_id)
            acquired_at = src_json.get("acquired_at", "")
            summary = src_json.get("summary", "")
            provenance = src_json.get("provenance", {})
            origin = provenance.get("origin", "")
            abs_path = provenance.get("absolute_path", "")

            l0_v2.mkdir(parents=True, exist_ok=True)
            safe_id = _safe_filename(src_id.replace("local_note:", "local-note-"))
            fm = _fm_dump({
                "source_id": safe_id,
                "source_type": src_type,
                "title": title,
                "registered_at": acquired_at or state.get("created_at", ""),
                "origin": origin,
                "absolute_path": abs_path,
            })
            body_parts = [f"# {title}\n"]
            if origin:
                body_parts.append(f"**Origin:** {origin}\n")
            if abs_path:
                body_parts.append(f"**Path:** `{abs_path}`\n")
            if summary:
                body_parts.append(f"\n## Summary\n\n{summary}\n")

            body = "\n".join(body_parts)
            (l0_v2 / f"{safe_id}.md").write_text(f"{fm}\n{body}\n", encoding="utf-8")
            count += 1

    # Also check L1/sources (some topics have duplicates there)
    l1_sources = legacy_path / "L1" / "sources"
    if l1_sources.exists():
        for src_dir in sorted(l1_sources.iterdir()):
            if not src_dir.is_dir():
                continue
            src_json = _read_json(src_dir / "source.json")
            if not src_json:
                continue
            src_id = src_json.get("source_id", src_dir.name)
            safe_id = _safe_filename(src_id.replace("local_note:", "local-note-"))
            l0_v2.mkdir(parents=True, exist_ok=True)
            target = l0_v2 / f"{safe_id}.md"
            if target.exists():
                continue
            title = src_json.get("title", src_id)
            src_type = src_json.get("source_type", "local_note")
            acquired_at = src_json.get("acquired_at", "")
            summary = src_json.get("summary", "")

            fm = _fm_dump({
                "source_id": safe_id,
                "source_type": src_type,
                "title": title,
                "registered_at": acquired_at or state.get("created_at", ""),
            })
            body = f"# {title}\n"
            if summary:
                body += f"\n## Summary\n\n{summary}\n"
            target.write_text(f"{fm}\n{body}\n", encoding="utf-8")
            count += 1

    return count


def convert_l1(topic_path: Path, legacy_path: Path, state: dict, run_data: dict) -> None:
    """Convert L1 artifacts from legacy format to v2."""
    l1_v2 = topic_path / "L1"
    l1_v2.mkdir(parents=True, exist_ok=True)
    now = _now()

    # question_contract.md
    l1_data = _read_json(legacy_path / "L1" / "topic.json") or {}
    l0_data = _read_json(legacy_path / "L0" / "topic.json") or {}
    title = l1_data.get("title", l0_data.get("title", state.get("title", "")))

    question_fm = _fm_dump({
        "bounded_question": f"Investigate {title}",
        "status": "active",
        "created_at": state.get("created_at", now),
        "updated_at": now,
    })
    question_body = f"# Research Question\n\n**Topic:** {title}\n\nMigrated from legacy knowledge-hub.\n"
    (l1_v2 / "question_contract.md").write_text(f"{question_fm}\n{question_body}\n", encoding="utf-8")

    # source_basis.md
    vault_manifest = _read_json(legacy_path / "L1" / "vault" / "vault_manifest.json") or {}
    source_index = _read_jsonl(legacy_path / "L1" / "source_index.jsonl")
    l0_source_index = _read_jsonl(legacy_path / "L0" / "source_index.jsonl")

    all_sources = list(source_index) or list(l0_source_index) or []
    raw_info = vault_manifest.get("raw", {})
    wiki_info = vault_manifest.get("wiki", {})

    sb_fm = _fm_dump({
        "total_sources": raw_info.get("source_count", len(all_sources)),
        "wiki_pages": wiki_info.get("page_count", 0),
        "status": "active",
    })
    sb_body = f"# Source Basis\n\nMigrated from legacy L1 vault.\n"
    sb_body += f"- Source count: {raw_info.get('source_count', len(all_sources))}\n"
    sb_body += f"- Wiki pages: {wiki_info.get('page_count', 0)}\n"
    if all_sources:
        sb_body += "\n## Registered Sources\n\n"
        for src in all_sources:
            sid = src.get("source_id", src.get("id", "unknown"))
            stitle = src.get("title", sid)
            sb_body += f"- `{sid}`: {stitle}\n"
    (l1_v2 / "source_basis.md").write_text(f"{sb_fm}\n{sb_body}\n", encoding="utf-8")

    # convention_snapshot.md — minimal from legacy
    conv_fm = _fm_dump({
        "notation_choices": "legacy (not extracted)",
        "unit_conventions": "natural units unless specified",
        "regime": "as defined in source materials",
    })
    conv_body = "# Conventions\n\nMigrated from legacy. Convention details were not explicitly extracted.\n"
    (l1_v2 / "convention_snapshot.md").write_text(f"{conv_fm}\n{conv_body}\n", encoding="utf-8")

    # derivation_anchor_map.md — from source anchors if available
    anchor_index = _read_json(legacy_path / "L1" / "vault" / "output" / "source_anchor_index.json")
    dam_fm = _fm_dump({"status": "active"})
    dam_body = "# Derivation Anchor Map\n\n"
    if anchor_index and isinstance(anchor_index, dict):
        anchors = anchor_index.get("anchors", anchor_index)
        if isinstance(anchors, (list, dict)):
            dam_body += f"Migrated from legacy anchor index ({len(anchors)} entries).\n"
    else:
        dam_body += "No anchor data extracted from legacy.\n"
    (l1_v2 / "derivation_anchor_map.md").write_text(f"{dam_fm}\n{dam_body}\n", encoding="utf-8")

    # contradiction_register.md — empty placeholder
    cr_fm = _fm_dump({"open_contradictions": 0})
    cr_body = "# Contradiction Register\n\nNo contradictions extracted from legacy data.\n"
    (l1_v2 / "contradiction_register.md").write_text(f"{cr_fm}\n{cr_body}\n", encoding="utf-8")


def convert_l3(topic_path: Path, legacy_path: Path, state: dict, run_data: dict) -> None:
    """Convert L3 subplanes from legacy run data to v2."""
    l3_v2 = topic_path / "L3"
    now = _now()
    title = state.get("title", "")

    # --- Ideation ---
    ideation_dir = l3_v2 / "ideation"
    ideation_dir.mkdir(parents=True, exist_ok=True)
    candidates = run_data["all_candidates"]
    strategies = run_data["all_strategies"]

    idea_fm = _fm_dump({
        "idea_statement": f"Derived from legacy runs: {len(run_data['runs'])} runs, {len(candidates)} candidates",
        "motivation": f"Original research on {title}",
        "status": "active",
        "created_at": state.get("created_at", now),
    })
    idea_body = f"# Ideation\n\nMigrated from {len(run_data['runs'])} legacy L3 runs.\n\n"
    idea_body += f"## Idea Statement\n\nResearch on {title}.\n\n"
    if strategies:
        idea_body += f"## Strategy Memory ({len(strategies)} entries)\n\n"
        for s in strategies[:10]:
            stype = s.get("strategy_type", "unknown")
            ssum = s.get("summary", "")
            idea_body += f"- **{stype}**: {ssum}\n"
        if len(strategies) > 10:
            idea_body += f"\n... and {len(strategies) - 10} more.\n"
    (ideation_dir / "active_idea.md").write_text(f"{idea_fm}\n{idea_body}\n", encoding="utf-8")

    # --- Planning ---
    plan_dir = l3_v2 / "planning"
    plan_dir.mkdir(parents=True, exist_ok=True)

    # Collect all plan data from iterations
    all_plans = []
    for run in run_data["runs"]:
        for it in run["iterations"]:
            if it["plan_json"]:
                all_plans.append(it["plan_json"])

    plan_fm = _fm_dump({
        "plan_statement": f"Consolidated from {len(all_plans)} legacy iteration plans",
        "status": "active",
    })
    plan_body = f"# Planning\n\nConsolidated from {len(all_plans)} legacy iteration plans.\n\n"
    for i, plan in enumerate(all_plans[:5]):
        action_id = plan.get("selected_action_id", "")
        action_type = plan.get("selected_action_type", "")
        objective = ""
        if "objective" in str(plan):
            plan_md_content = None
            for run in run_data["runs"]:
                for it in run["iterations"]:
                    if it["plan_json"] == plan and it["plan_md"]:
                        plan_md_content = it["plan_md"]
                        break
            if plan_md_content:
                obj_match = re.search(r"## Objective\n\n(.+?)(?:\n##|\Z)", plan_md_content, re.DOTALL)
                if obj_match:
                    objective = obj_match.group(1).strip()
        plan_body += f"### Plan {i + 1}\n"
        plan_body += f"- **Action:** {action_id} ({action_type})\n"
        if objective:
            plan_body += f"- **Objective:** {objective[:200]}\n"
        plan_body += "\n"
    if len(all_plans) > 5:
        plan_body += f"... and {len(all_plans) - 5} more plans.\n"
    (plan_dir / "active_plan.md").write_text(f"{plan_fm}\n{plan_body}\n", encoding="utf-8")

    # --- Analysis ---
    analysis_dir = l3_v2 / "analysis"
    analysis_dir.mkdir(parents=True, exist_ok=True)

    # Determine round type from data
    round_type = "synthesis_round"
    if candidates:
        c_types = set()
        for c in candidates:
            ct = c.get("candidate_type", "")
            if "theorem" in ct or "proof" in ct:
                c_types.add("formal")
            if "benchmark" in ct or "numerical" in ct:
                c_types.add("numerical")
        if "formal" in c_types:
            round_type = "derivation_round"
        if "numerical" in c_types:
            round_type = "numerical_or_benchmark_round"

    # Collect derivation info from iterations
    all_syntheses = []
    for run in run_data["runs"]:
        for it in run["iterations"]:
            if it["synthesis_json"]:
                all_syntheses.append(it["synthesis_json"])

    analysis_fm = _fm_dump({
        "analysis_statement": f"Consolidated analysis from {len(all_syntheses)} L3 iterations",
        "method": "legacy_consolidation",
        "round_type": round_type,
        "status": "active",
    })
    analysis_body = f"# Analysis\n\nConsolidated from {len(all_syntheses)} legacy L3 iterations.\n"
    analysis_body += f"**Round type:** {round_type}\n\n"

    # Source anchor table from candidates
    if candidates:
        analysis_body += "## Source Anchors\n\n"
        seen_sources = set()
        for c in candidates:
            for ref in c.get("origin_refs", []):
                ref_id = ref.get("id", "")
                if ref_id and ref_id not in seen_sources:
                    seen_sources.add(ref_id)
                    analysis_body += f"- `{ref_id}`: {ref.get('title', '')} ({ref.get('layer', '')})\n"

    # Synthesis summaries
    if all_syntheses:
        analysis_body += "\n## Synthesis Summaries\n\n"
        for syn in all_syntheses[:10]:
            syn_status = syn.get("status", "")
            conclusion = syn.get("conclusion_status", "")
            promotion = syn.get("promotion_readiness", "")
            analysis_body += f"- Status: {syn_status}, Conclusion: {conclusion}, Promotion: {promotion}\n"
        if len(all_syntheses) > 10:
            analysis_body += f"\n... and {len(all_syntheses) - 10} more.\n"

    # Open obligations
    analysis_body += "\n## Open Obligations\n\n"
    analysis_body += "Extracted from legacy data — see individual run iterations for details.\n"
    (analysis_dir / "active_analysis.md").write_text(f"{analysis_fm}\n{analysis_body}\n", encoding="utf-8")

    # --- Result Integration ---
    integration_dir = l3_v2 / "result_integration"
    integration_dir.mkdir(parents=True, exist_ok=True)

    # Assess claim readiness
    claim_readiness = "blocked"
    if candidates:
        promoted = [c for c in candidates if "promot" in str(c.get("status", "")).lower() or c.get("promotion_readiness") == "promoted"]
        if promoted:
            claim_readiness = "qualified"

    int_fm = _fm_dump({
        "integration_statement": f"Integrated from {len(candidates)} candidates across {len(run_data['runs'])} runs",
        "findings": len(candidates),
        "claim_readiness": claim_readiness,
        "status": "active",
    })
    int_body = f"# Result Integration\n\n"
    int_body += f"## Integration Statement\n\n{len(candidates)} candidates from {len(run_data['runs'])} legacy runs.\n\n"

    if candidates:
        int_body += "## Findings\n\n"
        for c in candidates[:15]:
            cid = c.get("candidate_id", "unknown")
            ctype = c.get("candidate_type", "")
            ctitle = c.get("title", "")
            csum = c.get("summary", "")
            int_body += f"### {ctitle}\n"
            int_body += f"- **ID:** `{cid}`\n"
            int_body += f"- **Type:** {ctype}\n"
            int_body += f"- **Summary:** {csum[:300]}\n\n"
        if len(candidates) > 15:
            int_body += f"... and {len(candidates) - 15} more candidates.\n\n"

    int_body += f"## Claim Readiness\n\n**Overall:** {claim_readiness}\n\n"
    int_body += "## Open Obligations\n\nSee individual candidate records and iteration syntheses.\n"
    (integration_dir / "active_integration.md").write_text(f"{int_fm}\n{int_body}\n", encoding="utf-8")

    # --- Distillation ---
    distill_dir = l3_v2 / "distillation"
    distill_dir.mkdir(parents=True, exist_ok=True)

    distilled_claim = ""
    confidence = "low"
    if candidates:
        best = candidates[0]
        distilled_claim = best.get("summary", best.get("title", ""))
        if claim_readiness == "qualified":
            confidence = "medium"

    dist_fm = _fm_dump({
        "distilled_claim": distilled_claim or "No claim distilled (legacy migration)",
        "evidence_summary": f"{len(candidates)} candidates from legacy runs",
        "confidence": confidence,
        "status": "active",
    })
    dist_body = "# Distillation\n\n"
    dist_body += f"## Distilled Claim\n\n{distilled_claim or 'No claim distilled during legacy migration.'}\n\n"
    dist_body += f"## Evidence Summary\n\n{len(candidates)} candidates from {len(run_data['runs'])} legacy runs.\n\n"
    dist_body += f"**Confidence:** {confidence}\n\n"
    dist_body += "## Obligation Check\n\n"
    dist_body += f"- Checked against: active_integration.md\n"
    dist_body += f"- Blocking obligations: inherited from legacy\n"
    dist_body += f"- Claim scope adjusted: no\n"
    dist_body += "## Open Questions\n\nLegacy migration — all open questions preserved in iteration data.\n"
    (distill_dir / "active_distillation.md").write_text(f"{dist_fm}\n{dist_body}\n", encoding="utf-8")

    # --- Candidates ---
    cand_dir = l3_v2 / "candidates"
    if candidates:
        cand_dir.mkdir(parents=True, exist_ok=True)
        for c in candidates:
            cid = c.get("candidate_id", f"candidate-{len(candidates)}")
            safe_cid = _safe_filename(cid)
            ctitle = c.get("title", cid)
            ctype = c.get("candidate_type", "unknown")
            csum = c.get("summary", "")
            cstatus = c.get("status", "unknown")
            origin_refs = c.get("origin_refs", [])
            assumptions = c.get("assumptions", [])

            cfm = _fm_dump({
                "candidate_id": cid,
                "candidate_type": ctype,
                "title": ctitle,
                "status": cstatus,
                "registered_at": now,
                "origin_refs": [r.get("id", "") for r in origin_refs if isinstance(r, dict)],
            })
            cbody = f"# {ctitle}\n\n"
            cbody += f"**Type:** {ctype}\n**Status:** {cstatus}\n\n"
            cbody += f"## Summary\n\n{csum}\n\n"
            if origin_refs:
                cbody += "## Origin References\n\n"
                for r in origin_refs:
                    if isinstance(r, dict):
                        cbody += f"- `{r.get('id', '')}`: {r.get('title', '')} ({r.get('layer', '')})\n"
                cbody += "\n"
            if assumptions:
                cbody += "## Assumptions\n\n"
                for a in assumptions:
                    cbody += f"- {a}\n"
                cbody += "\n"
            cbody += f"## Question\n\n{c.get('question', 'N/A')}\n"
            (cand_dir / f"{safe_cid}.md").write_text(f"{cfm}\n{cbody}\n", encoding="utf-8")

    # --- L3 tex ---
    tex_dir = l3_v2 / "tex"
    tex_dir.mkdir(parents=True, exist_ok=True)

    # Copy existing research_notebook.tex if available
    legacy_tex = legacy_path / "L3" / "research_notebook.tex"
    if legacy_tex.exists():
        shutil.copy2(legacy_tex, tex_dir / "flow_notebook.tex")
    else:
        # Also check human_dossier
        dossier_tex = legacy_path / "L3" / "human_dossier" / "main.tex"
        if dossier_tex.exists():
            shutil.copy2(dossier_tex, tex_dir / "flow_notebook.tex")
        else:
            # Minimal placeholder
            tex_content = f"""% Updated: {now} — legacy migration
\\documentclass[11pt,a4paper]{{article}}
\\usepackage{{amsmath,amssymb}}
\\usepackage{{hyperref}}
\\title{{Research Notebook: {title}}}
\\author{{AITP v2 (migrated from legacy)}}
\\date{{\\today}}
\\begin{{document}}
\\maketitle
\\section{{Overview}}
Migrated from legacy knowledge-hub. Full notebook content will be populated
during active L3 derivation in the v2 protocol.
\\end{{document}}
"""
            (tex_dir / "flow_notebook.tex").write_text(tex_content, encoding="utf-8")


def convert_l4(topic_path: Path, legacy_path: Path, state: dict, run_data: dict) -> None:
    """Convert L4 validation data from legacy to v2."""
    l4_v2 = topic_path / "L4"
    l4_v2.mkdir(parents=True, exist_ok=True)
    now = _now()

    # Collect all L4 return data
    l4_returns = []
    for run in run_data["runs"]:
        for it in run["iterations"]:
            if it["l4_return_json"] and it["l4_return_json"].get("returned_result_status"):
                l4_returns.append(it)

    # validation_contract.md
    vc_fm = _fm_dump({
        "status": "active" if l4_returns else "pending",
        "created_at": now,
    })
    vc_body = "# Validation Contract\n\n"
    if l4_returns:
        vc_body += f"Found {len(l4_returns)} L4 return records in legacy data.\n\n"
        vc_body += "## Validation History\n\n"
        for lr in l4_returns:
            rj = lr["l4_return_json"]
            vc_body += f"- **{lr['id']}** (run {rj.get('run_id', '')}): status={rj.get('returned_result_status', '')}\n"
    else:
        vc_body += "No L4 validation records found in legacy data.\n"
    (l4_v2 / "validation_contract.md").write_text(f"{vc_fm}\n{vc_body}\n", encoding="utf-8")

    # L4 reviews — one per candidate with L4 return data
    reviews_dir = l4_v2 / "reviews"
    if l4_returns:
        reviews_dir.mkdir(parents=True, exist_ok=True)
        for lr in l4_returns:
            rj = lr["l4_return_json"]
            rid = rj.get("returned_result_id", lr["id"])
            safe_rid = _safe_filename(rid)
            rstatus = rj.get("returned_result_status", "unknown")
            rsummary = rj.get("returned_result_summary", "")

            rfm = _fm_dump({
                "review_id": rid,
                "status": rstatus,
                "reviewed_at": rj.get("updated_at", now),
            })
            rbody = f"# L4 Review: {rid}\n\n"
            rbody += f"**Status:** {rstatus}\n\n"
            if rsummary:
                rbody += f"## Result Summary\n\n{rsummary}\n\n"
            if lr["l4_return_md"]:
                rbody += "## Original L4 Return Notes\n\n"
                # Strip header lines from legacy md
                lines = lr["l4_return_md"].splitlines()
                content_lines = [l for l in lines if not l.startswith("# L4 Return") and not l.startswith("- Topic slug:") and not l.startswith("- Run id:") and not l.startswith("- Iteration id:") and not l.startswith("- Status:") and not l.startswith("- Execution task:") and not l.startswith("- Validation review")]
                cleaned = "\n".join(content_lines).strip()
                if cleaned:
                    rbody += cleaned + "\n"
            (reviews_dir / f"{safe_rid}.md").write_text(f"{rfm}\n{rbody}\n", encoding="utf-8")


def update_runtime(topic_path: Path, state: dict, run_data: dict, sources_count: int) -> None:
    """Update runtime files with conversion summary."""
    now = _now()
    runtime_dir = topic_path / "runtime"
    runtime_dir.mkdir(parents=True, exist_ok=True)

    # Append to log.md
    log_path = runtime_dir / "log.md"
    if log_path.exists():
        existing = log_path.read_text(encoding="utf-8")
        new_entry = f"- {now} converted legacy data to v2 L0-L4 structure ({sources_count} sources, {len(run_data['all_candidates'])} candidates, {len(run_data['runs'])} runs)\n"
        log_path.write_text(existing + new_entry, encoding="utf-8")
    else:
        log_content = f"# Topic Log\n\n## Events\n\n- {now} converted legacy data to v2 L0-L4 structure\n"
        log_path.write_text(log_content, encoding="utf-8")

    # Update index.md
    title = state.get("title", "")
    slug = topic_path.name
    index_content = f"# {title}\n\n"
    index_content += f"- Slug: `{slug}`\n"
    index_content += f"- Lane: {state.get('lane', 'unknown')}\n"
    index_content += f"- Status: {state.get('stage', 'unknown')}\n"
    index_content += f"- Sources: {sources_count}\n"
    index_content += f"- L3 runs: {len(run_data['runs'])}\n"
    index_content += f"- Candidates: {len(run_data['all_candidates'])}\n"
    index_content += f"- Legacy data: `legacy/`\n"
    (runtime_dir / "index.md").write_text(index_content, encoding="utf-8")


def convert_topic(topic_path: Path) -> dict | None:
    """Convert a single topic from legacy to v2 structure."""
    legacy_path = topic_path / "legacy"
    if not legacy_path.exists():
        return None

    # Read existing state.md to get lane/title info
    state_path = topic_path / "state.md"
    state = {}
    if state_path.exists():
        state_text = state_path.read_text(encoding="utf-8")
        if state_text.startswith("---"):
            end = state_text.find("---", 3)
            if end > 0:
                fm_text = state_text[3:end]
                for line in fm_text.splitlines():
                    line = line.strip()
                    if ":" in line:
                        k, v = line.split(":", 1)
                        state[k.strip()] = v.strip().strip('"')

    slug = topic_path.name

    # Gather all run data
    run_data = _gather_run_data(legacy_path)

    # Convert each layer
    sources_count = convert_l0(topic_path, legacy_path, state)
    convert_l1(topic_path, legacy_path, state, run_data)
    convert_l3(topic_path, legacy_path, state, run_data)
    convert_l4(topic_path, legacy_path, state, run_data)
    update_runtime(topic_path, state, run_data, sources_count)

    return {
        "slug": slug,
        "sources": sources_count,
        "runs": len(run_data["runs"]),
        "candidates": len(run_data["all_candidates"]),
        "strategies": len(run_data["all_strategies"]),
    }


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <topics_root>")
        sys.exit(1)

    topics_root = Path(sys.argv[1])
    if not topics_root.exists():
        print(f"Error: {topics_root} does not exist")
        sys.exit(1)

    # Only convert topics that have a legacy/ directory
    topic_dirs = sorted([
        d for d in topics_root.iterdir()
        if d.is_dir() and (d / "legacy").exists()
    ])

    print(f"Found {len(topic_dirs)} topics with legacy data to convert")

    converted = []
    errors = []

    for topic_path in topic_dirs:
        try:
            result = convert_topic(topic_path)
            if result:
                converted.append(result)
                print(f"  OK: {result['slug']} ({result['sources']} src, {result['runs']} runs, {result['candidates']} cands)")
            else:
                print(f"  SKIP: {topic_path.name} (no legacy data)")
        except Exception as e:
            errors.append((topic_path.name, str(e)))
            print(f"  ERR: {topic_path.name}: {e}")

    # Summary
    total_sources = sum(r["sources"] for r in converted)
    total_runs = sum(r["runs"] for r in converted)
    total_cands = sum(r["candidates"] for r in converted)
    print(f"\nConversion complete: {len(converted)} topics, {total_sources} sources, {total_runs} runs, {total_cands} candidates, {len(errors)} errors")

    # Write conversion manifest
    manifest = {
        "converted_at": _now(),
        "total_topics": len(converted),
        "total_sources": total_sources,
        "total_runs": total_runs,
        "total_candidates": total_cands,
        "errors": len(errors),
        "topics": converted,
        "error_details": [(s, e) for s, e in errors],
    }
    manifest_path = topics_root / "conversion_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Manifest: {manifest_path}")


if __name__ == "__main__":
    main()
