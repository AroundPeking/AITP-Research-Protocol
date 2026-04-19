from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path


def _bootstrap_path() -> None:
    package_root = Path(__file__).resolve().parents[1]
    if str(package_root) not in sys.path:
        sys.path.insert(0, str(package_root))


_bootstrap_path()

from knowledge_hub import research_notebook_support as notebook


def test_preamble_includes_notebook_layout_and_box_styling() -> None:
    assert r"\usepackage[most]{tcolorbox}" in notebook._PREAMBLE
    assert r"\usepackage{tabularx}" in notebook._PREAMBLE
    assert r"\begin{titlepage}" in notebook._PREAMBLE
    assert "TOPIC_SLUG_PLACEHOLDER" in notebook._PREAMBLE
    assert "DATE_PLACEHOLDER" in notebook._PREAMBLE


def test_render_entry_uses_kind_box_metadata_badges_and_detail_table() -> None:
    rendered = notebook._render_entry(
        {
            "kind": "candidate_update",
            "timestamp": "2026-04-18T10:20:30+08:00",
            "run_id": "run-42",
            "title": "Gap Closure Benchmark",
            "body": "Observed $E=mc^2$ agreement.\n\n$$a^2+b^2=c^2$$",
            "status": "approved",
            "details": {
                "acceptance_metric": "0.5%",
                "artifacts": ["plot.pdf", "table.csv"],
            },
        }
    )

    assert r"\section{Candidate Update: Gap Closure Benchmark}" in rendered
    assert r"\begin{tcolorbox}[" in rendered
    assert "candidateframe" in rendered
    assert r"\kindpill{candidateframe}{Candidate Update}" in rendered
    assert r"\entrytag{candidate\_update}" in rendered
    assert r"\metaitem{Time}{2026-04-18T10:20:30+08:00}" in rendered
    assert r"\metaitem{Run}{run-42}" in rendered
    assert r"\statusgood{approved}" in rendered
    assert r"\begin{tabularx}{\linewidth}" in rendered
    assert "acceptance\\_metric" in rendered
    assert "$E=mc^2$" in rendered
    assert "$$a^2+b^2=c^2$$" in rendered


def test_topic_notebook_prefers_physicist_reading_order_and_stepwise_derivation() -> None:
    with tempfile.TemporaryDirectory() as td:
        topic_root = Path(td) / "topics" / "demo-topic"
        l3_root = topic_root / "L3"
        runtime_root = topic_root / "runtime"
        run_root = l3_root / "runs" / "run-001"
        l3_root.mkdir(parents=True, exist_ok=True)
        runtime_root.mkdir(parents=True, exist_ok=True)
        run_root.mkdir(parents=True, exist_ok=True)

        (runtime_root / "research_question.contract.json").write_text(
            json.dumps(
                {
                    "title": "Demo Topic",
                    "question": "Recover the bounded derivation and benchmark route.",
                    "scope": ["Stay within the currently registered source set."],
                    "assumptions": ["Only persisted evidence counts."],
                    "open_ambiguities": ["The sign convention for the response coefficient remains unresolved."],
                    "formalism_and_notation": [
                        "Use Euclidean-signature notation unless a source explicitly says otherwise."
                    ],
                    "l1_source_intake": {
                        "reading_depth_rows": [
                            {"source_title": "Lecture Notes A", "reading_depth": "full_read"},
                            {"source_title": "Benchmark Paper B", "reading_depth": "skim"},
                        ],
                        "notation_tension_candidates": [
                            {
                                "summary": "Paper A uses k while Paper B uses sigma_xy for the same response coefficient."
                            }
                        ],
                    },
                    "l1_vault": {
                        "wiki": {
                            "page_paths": [
                                "topics/demo-topic/L1/vault/wiki/home.md",
                                "topics/demo-topic/L1/vault/wiki/source-bridge.md",
                            ]
                        }
                    },
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        (runtime_root / "unfinished_work.json").write_text(
            json.dumps(
                {
                    "items": [
                        {
                            "summary": "Recover the missing intermediate derivation step from the cited source.",
                            "missing_block": "derivation_spine",
                            "status": "pending",
                        }
                    ]
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        (run_root / "candidate_ledger.jsonl").write_text(
            json.dumps(
                {
                    "candidate_id": "candidate:demo-bound",
                    "candidate_type": "derivation_object",
                    "title": "Bounded response derivation",
                    "summary": "A source-grounded derivation candidate for the response coefficient.",
                    "status": "ready_for_validation",
                    "question": "Does the reconstructed derivation agree with the benchmark regime?",
                    "assumptions": ["Weak-coupling regime", "Translation invariance"],
                    "proposed_validation_route": "benchmark_review",
                },
                ensure_ascii=False,
                separators=(",", ":"),
            )
            + "\n",
            encoding="utf-8",
        )
        (run_root / "strategy_memory.jsonl").write_text(
            json.dumps(
                {
                    "summary": "Check notation alignment before comparing benchmark formulas.",
                    "strategy_type": "verification_guardrail",
                    "outcome": "helpful",
                    "confidence": 0.81,
                },
                ensure_ascii=False,
                separators=(",", ":"),
            )
            + "\n",
            encoding="utf-8",
        )
        (runtime_root / "research_report.active.json").write_text(
            json.dumps(
                {
                    "status": "available",
                    "topic_slug": "demo-topic",
                    "run_id": "run-001",
                    "problem": {
                        "question": "Can the bounded route survive the benchmark comparison without hiding the normalization caveat?",
                        "literature_position": "Primary source basis: Lecture Notes A, Benchmark Note B",
                    },
                    "physical_target": "Hall-response coefficient in the bounded weak-coupling regime",
                    "observables_or_decision_targets": ["Hall-response coefficient"],
                    "current_dispute_or_bottleneck": "One normalization factor remains unresolved.",
                    "physical_motivation": "Make the normalization caveat explicit instead of polishing it away.",
                    "setup": {
                        "scope": ["Keep the bounded route explicit."],
                        "assumptions": ["Weak coupling."],
                        "notation": ["Use source convention first."],
                        "deliverables": ["One bounded derivation note."],
                    },
                    "convention_ledger": [
                        {
                            "symbol": "k",
                            "meaning": "source-side response coefficient",
                            "normalization": "Lecture-note convention",
                            "source": "Lecture Notes A §2 eq.(4)",
                            "bridge_status": "open",
                            "notes": "Not yet fully bridged to sigma_xy.",
                        },
                        {
                            "symbol": "sigma_xy",
                            "meaning": "benchmark transport coefficient",
                            "normalization": "Benchmark transport convention",
                            "source": "Benchmark Note B §3",
                            "bridge_status": "open",
                            "notes": "Needs explicit bridge from k.",
                        },
                    ],
                    "round_development": [
                        {
                            "iteration_id": "iteration-001",
                            "round_type": "derivation_round",
                            "round_question": "Check the normalization bridge.",
                            "plan_summary": "Keep factor bookkeeping explicit before comparing against the benchmark note.",
                            "returned_result_summary": "The main backbone survives, but one factor remains unresolved.",
                            "understanding_delta": "The caveat is real, not cosmetic.",
                            "next_step_summary": "Recover the omitted factor before promotion.",
                            "claim_readiness": "qualified",
                            "missing_blocks": [],
                            "hard_blocking_gaps": [],
                            "qualified_gaps": ["One normalization factor remains unresolved."],
                            "eligible_for_current_claims": True,
                        }
                    ],
                    "main_derivation_spine": [
                        {
                            "derivation_id": "candidate:demo-bound",
                            "title": "Source reconstruction: Hall-response coefficient from Lecture Notes A",
                            "derivation_kind": "source_reconstruction",
                            "status": "in_progress",
                            "source_statement": "The source gives the curvature-side coefficient formula.",
                            "source_omissions": ["The source omits the bridge from k to sigma_xy."],
                            "l3_restoration_notes": "L3 restores the omitted bridge as a separate bounded step instead of silently identifying the symbols.",
                            "assumptions": ["Weak-coupling regime", "Translation invariance"],
                            "source_refs": ["Lecture Notes A §2 eq.(4)", "Benchmark Note B §3"],
                            "provenance_note": "This derivation is reconstructed in L3 from the cited source, not copied as an authoritative result.",
                            "derivation_steps": [
                                {
                                    "label": "Step 1",
                                    "equation": "$$k = \\frac{1}{2\\pi} \\int_{\\mathcal{B}} F$$",
                                    "justification": "Source equation.",
                                    "equality_reason": "Direct transcription of the cited source equation.",
                                    "source_anchor": "Lecture Notes A §2 eq.(4)",
                                    "formula_anchor": "lecture-a#eq:4",
                                    "step_origin": "source_statement",
                                    "is_l3_completion": False,
                                    "assumption_dependencies": ["Weak-coupling regime"],
                                },
                                {
                                    "label": "Step 2",
                                    "equation": "$$\\sigma_{xy} = k + \\delta$$",
                                    "justification": "Benchmark bridge note.",
                                    "equality_reason": "This bridge step is reconstructed from the benchmark convention.",
                                    "source_anchor": "Benchmark Note B §3",
                                    "formula_anchor": "benchmark-b#eq:transport-3",
                                    "step_origin": "l3_completion",
                                    "is_l3_completion": True,
                                    "assumption_dependencies": ["Weak-coupling regime", "Translation invariance"],
                                    "open_gap_note": "The normalization bridge is still incomplete.",
                                },
                            ],
                            "target_source_location": "Lecture Notes A §2 eq.(4)",
                            "source_anchor_table": [
                                {
                                    "step_label": "Step 1",
                                    "source_anchor": "Lecture Notes A §2 eq.(4)",
                                    "formula_anchor": "lecture-a#eq:4",
                                    "step_origin": "source_statement",
                                    "anchor_notes": "",
                                },
                                {
                                    "step_label": "Step 2",
                                    "source_anchor": "Benchmark Note B §3",
                                    "formula_anchor": "benchmark-b#eq:transport-3",
                                    "step_origin": "l3_completion",
                                    "anchor_notes": "",
                                },
                            ],
                        }
                    ],
                    "current_best_statements": [
                        {
                            "statement": "The bounded derivation backbone survives the benchmark comparison.",
                            "validity_regime": "Weak-coupling regime with explicit normalization caveat.",
                            "depends_on": ["L3 derivation", "L2 comparison receipt"],
                            "breaks_if": "The transport convention inserts an additional factor.",
                            "still_unclosed": ["One normalization factor remains unresolved."],
                            "claim_readiness": "qualified",
                            "next_action": "Recover the omitted factor before promotion.",
                        }
                    ],
                    "active_routes_not_yet_claim_worthy": [],
                    "excluded_routes": [
                        {
                            "title": "Failed attempt: direct identification of k with sigma_xy",
                            "why_plausible": "Both sources discuss the same observable and the shortcut made the story look cleaner.",
                            "exact_failure_point": "The convention bridge was assumed rather than derived.",
                            "lesson": "Do not identify the symbols before the normalization bridge is written explicitly.",
                            "revive_conditions": ["A later source may prove the bridge under extra assumptions."],
                        }
                    ],
                    "open_obligations": [
                        {
                            "summary": "Recover the omitted factor from the benchmark convention note.",
                            "missing_block": "convention_ledger",
                            "recommended_round_type": "derivation_round",
                        }
                    ],
                    "current_conclusion": "The route is usable but still caveated.",
                    "open_problems": ["Recover the omitted normalization factor."],
                    "recommended_skills": [
                        {
                            "skill_name": "aitp-topic-report-author",
                            "path": "skills/aitp-topic-report-author/SKILL.md",
                            "purpose": "Assemble the topic into a physicist-readable report.",
                        }
                    ],
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        notebook.append_notebook_entry(
            l3_root,
            kind="candidate_update",
            title="Seed entry",
            body="Seed notebook rebuild.",
            status="ready_for_validation",
            run_id="run-001",
        )

        tex = (l3_root / "research_notebook.tex").read_text(encoding="utf-8")

        assert r"\section{Research Problem, Physical Target, And Motivation}" in tex
        assert "Hall-response coefficient in the bounded weak-coupling regime" in tex
        assert "One normalization factor remains unresolved." in tex
        assert r"\section{Setup, Regime, And Convention Ledger}" in tex
        assert "source-side response coefficient" in tex
        assert "Benchmark transport convention" in tex
        assert r"\section{Round-by-Round Research Development}" in tex
        assert "Check the normalization bridge." in tex
        assert "Keep factor bookkeeping explicit before comparing against the benchmark note." in tex
        assert "Recover the omitted factor before promotion." in tex
        assert r"\section{Main Derivation Spine}" in tex
        assert "Step 1" in tex
        assert "Source equation." in tex
        assert "Formula anchor." in tex
        assert "lecture-a\\#eq:4" in tex
        assert "The source omits the bridge from k to sigma\\_xy." in tex
        assert "L3 restores the omitted bridge as a separate bounded step" in tex
        assert r"\section{Current Best Statements}" in tex
        assert "Validity regime" in tex
        assert "Breaks if" in tex
        assert "Still unclosed" in tex
        assert r"\section{Excluded Routes And Lessons}" in tex
        assert "The convention bridge was assumed rather than derived." in tex
        assert "Do not identify the symbols before the normalization bridge is written explicitly." in tex
        assert r"\section{Open Obligations And Next Research Direction}" in tex
        assert "Recover the omitted factor from the benchmark convention note." in tex
        assert r"\section{Source Provenance And Reading Map}" in tex
        assert "Lecture Notes A" in tex
        assert r"\section{Chronological Entry Log}" in tex
        assert r"\section{Iterative L3-L4 Research Record}" not in tex
        assert r"\section{Current Claims And Stable Results}" not in tex
        assert r"\section{Consolidated Derivation And Validation Status}" not in tex


def test_long_topic_notebook_moves_intermediate_rounds_and_derivations_into_appendix_archives() -> None:
    with tempfile.TemporaryDirectory() as td:
        topic_root = Path(td) / "topics" / "demo-topic"
        l3_root = topic_root / "L3"
        runtime_root = topic_root / "runtime"
        l3_root.mkdir(parents=True, exist_ok=True)
        runtime_root.mkdir(parents=True, exist_ok=True)

        round_rows = []
        derivation_rows = []
        for index in range(1, 7):
            round_rows.append(
                {
                    "iteration_id": f"iteration-{index:03d}",
                    "round_type": "derivation_round",
                    "round_question": f"Round question {index}",
                    "plan_summary": f"Plan summary {index}",
                    "returned_result_summary": f"Result summary {index}",
                    "understanding_delta": f"Understanding delta {index}",
                    "next_step_summary": f"Next step {index}",
                    "claim_readiness": "qualified",
                    "missing_blocks": [],
                    "hard_blocking_gaps": [],
                    "qualified_gaps": [],
                    "eligible_for_current_claims": True,
                }
            )
        for index in range(1, 6):
            derivation_rows.append(
                {
                    "derivation_id": f"derivation:demo-{index}",
                    "title": f"Supplementary derivation {index}",
                    "derivation_kind": "source_reconstruction" if index % 2 else "analysis_derivation",
                    "status": "in_progress",
                    "source_statement": f"Source statement {index}",
                    "l3_restoration_notes": f"Reconstruction note {index}",
                    "target_source_location": f"paper-a#eq:{index}",
                    "source_anchor_table": [
                        {
                            "step_label": "Step 1",
                            "source_anchor": f"paper-a §{index}",
                            "formula_anchor": f"paper-a#eq:{index}",
                            "step_origin": "source_statement",
                            "anchor_notes": "",
                        }
                    ],
                    "derivation_steps": [
                        {
                            "label": "Step 1",
                            "equation": f"k_{index} = F_{index}",
                            "justification": "Source equation.",
                            "equality_reason": "Directly quoted from the source.",
                            "source_anchor": f"paper-a §{index}",
                            "formula_anchor": f"paper-a#eq:{index}",
                            "step_origin": "source_statement",
                            "is_l3_completion": False,
                            "assumption_dependencies": ["Weak-coupling regime"],
                        }
                    ],
                }
            )

        (runtime_root / "research_report.active.json").write_text(
            json.dumps(
                {
                    "status": "available",
                    "topic_slug": "demo-topic",
                    "run_id": "run-001",
                    "problem": {"question": "Can the topic stay readable as it grows long?"},
                    "physical_target": "Long-topic notebook readability",
                    "physical_motivation": "Keep the main narrative readable while preserving the full archive.",
                    "setup": {"scope": ["Long topic"], "assumptions": ["Preserve all records"], "notation": []},
                    "convention_ledger": [],
                    "round_development": round_rows,
                    "main_derivation_spine": derivation_rows,
                    "current_best_statements": [],
                    "active_routes_not_yet_claim_worthy": [],
                    "excluded_routes": [
                        {
                            "title": f"Excluded route {index}",
                            "why_plausible": f"Why plausible {index}",
                            "exact_failure_point": f"Failure {index}",
                            "lesson": f"Lesson {index}",
                            "revive_conditions": [f"Revive {index}"],
                        }
                        for index in range(1, 5)
                    ],
                    "open_obligations": [],
                    "open_problems": [],
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        notebook.append_notebook_entry(
            l3_root,
            kind="candidate_update",
            title="Seed entry",
            body="Seed notebook rebuild.",
            status="ready_for_validation",
            run_id="run-001",
        )

        tex = (l3_root / "research_notebook.tex").read_text(encoding="utf-8")

        assert "intermediate round(s) are moved to the appendix archive" in tex
        assert "supplementary derivation file(s) are moved to the appendix" in tex
        assert r"\section{Extended Round Archive}" in tex
        assert r"\section{Supplementary Derivation Files}" in tex
        assert r"\section{Supplementary Excluded Routes}" in tex
        assert "Round question 2" in tex
        assert "Supplementary derivation 2" in tex
        assert "Excluded route 4" in tex


def test_notebook_surfaces_blocked_routes_without_promoting_them_to_current_best_statements() -> None:
    with tempfile.TemporaryDirectory() as td:
        topic_root = Path(td) / "topics" / "demo-topic"
        l3_root = topic_root / "L3"
        runtime_root = topic_root / "runtime"
        l3_root.mkdir(parents=True, exist_ok=True)
        runtime_root.mkdir(parents=True, exist_ok=True)

        (runtime_root / "research_report.active.json").write_text(
            json.dumps(
                {
                    "status": "available",
                    "topic_slug": "demo-topic",
                    "run_id": "run-001",
                    "problem": {"question": "Can the blocked route be repaired?"},
                    "physical_target": "Blocked derivation route",
                    "physical_motivation": "Expose what is still missing instead of pretending the route is ready.",
                    "setup": {"scope": ["Keep the blocked route visible."], "assumptions": [], "notation": []},
                    "convention_ledger": [],
                    "round_development": [
                        {
                            "iteration_id": "iteration-001",
                            "round_type": "derivation_round",
                            "round_question": "Can the route be quoted yet?",
                            "claim_readiness": "blocked",
                            "missing_blocks": ["derivation_spine"],
                            "hard_blocking_gaps": ["derivation_spine"],
                            "qualified_gaps": [],
                            "eligible_for_current_claims": False,
                            "next_step_summary": "Write the missing stepwise derivation before quoting the route.",
                        }
                    ],
                    "main_derivation_spine": [],
                    "current_best_statements": [],
                    "active_routes_not_yet_claim_worthy": [
                        {
                            "statement": "The route might still work, but it is not yet claim-worthy.",
                            "claim_readiness": "blocked",
                            "still_unclosed": ["Missing obligation block: derivation_spine"],
                            "next_action": "Write the missing stepwise derivation before quoting the route.",
                        }
                    ],
                    "excluded_routes": [],
                    "open_obligations": [
                        {
                            "summary": "Write the missing stepwise derivation before quoting the route.",
                            "missing_block": "derivation_spine",
                            "recommended_round_type": "derivation_round",
                        }
                    ],
                    "open_problems": ["Write the missing stepwise derivation before quoting the route."],
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        notebook.append_notebook_entry(
            l3_root,
            kind="candidate_update",
            title="Seed entry",
            body="Seed notebook rebuild.",
            status="ready_for_validation",
            run_id="run-001",
        )

        tex = (l3_root / "research_notebook.tex").read_text(encoding="utf-8")

        assert r"\section{Current Best Statements}" in tex
        assert "No claim is currently stable enough to quote as a best statement." in tex
        assert "Active But Not Yet Claim-Worthy Routes" in tex
        assert "Missing obligation block: derivation\\_spine" in tex
