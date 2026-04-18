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


def test_topic_notebook_compiles_runtime_l1_and_l3_surfaces_into_archive_sections() -> None:
    with tempfile.TemporaryDirectory() as td:
        topic_root = Path(td) / "topics" / "demo-topic"
        l3_root = topic_root / "L3"
        runtime_root = topic_root / "runtime"
        run_root = l3_root / "runs" / "run-001"
        iteration_root = run_root / "iterations" / "iteration-002"
        l3_root.mkdir(parents=True, exist_ok=True)
        runtime_root.mkdir(parents=True, exist_ok=True)
        run_root.mkdir(parents=True, exist_ok=True)
        iteration_root.mkdir(parents=True, exist_ok=True)

        (runtime_root / "research_question.contract.json").write_text(
            json.dumps(
                {
                    "title": "Demo Topic",
                    "question": "Recover the bounded derivation and benchmark route.",
                    "scope": [
                        "Stay within the currently registered source set.",
                        "Track notation and validation obligations explicitly.",
                    ],
                    "assumptions": [
                        "Only persisted evidence counts.",
                    ],
                    "open_ambiguities": [
                        "The sign convention for the response coefficient remains unresolved.",
                    ],
                    "formalism_and_notation": [
                        "Use Euclidean-signature notation unless a source explicitly says otherwise.",
                    ],
                    "deliverables": [
                        "Produce a bounded candidate and one explicit validation route.",
                    ],
                    "l1_source_intake": {
                        "source_count": 2,
                        "reading_depth_rows": [
                            {
                                "source_title": "Lecture Notes A",
                                "reading_depth": "full_read",
                            },
                            {
                                "source_title": "Benchmark Paper B",
                                "reading_depth": "skim",
                            },
                        ],
                        "method_specificity_rows": [
                            {
                                "source_title": "Lecture Notes A",
                                "method_family": "derivation",
                                "specificity_tier": "high",
                            }
                        ],
                        "notation_tension_candidates": [
                            {
                                "summary": "Paper A uses k while Paper B uses sigma_xy for the same response coefficient."
                            }
                        ],
                        "contradiction_candidates": [
                            {
                                "summary": "Benchmark ranges disagree outside the weak-coupling regime."
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
        (runtime_root / "idea_packet.json").write_text(
            json.dumps(
                {
                    "status": "approved_for_execution",
                    "initial_idea": "Understand the literature derivation and turn it into a bounded executable question.",
                    "novelty_target": "Clarify the derivation path and benchmark boundary.",
                    "first_validation_route": "Bounded benchmark comparison",
                    "initial_evidence_bar": "Persisted derivation notes plus one explicit validation artifact.",
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
                            "status": "pending",
                        }
                    ]
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        (run_root / "derivation_records.jsonl").write_text(
            json.dumps(
                {
                    "derivation_id": "derivation:demo-reconstruction",
                    "title": "Response-coefficient reconstruction from source A",
                    "derivation_kind": "source_reconstruction",
                    "status": "in_progress",
                    "body": "Starting from the source statement, we recover\n\n$$k = \\frac{1}{2\\pi} \\int F$$",
                    "source_refs": [
                        "paper-a §2 eq.(4)",
                        "paper-b §3 benchmark discussion",
                    ],
                    "assumptions": ["Weak-coupling regime", "Translation invariance"],
                    "provenance_note": "This derivation is reconstructed in L3 from the cited source, not copied as an authoritative result.",
                },
                ensure_ascii=False,
                separators=(",", ":"),
            )
            + "\n",
            encoding="utf-8",
        )
        (run_root / "l2_comparison_receipts.jsonl").write_text(
            json.dumps(
                {
                    "comparison_id": "comparison:demo-benchmark-check",
                    "candidate_ref_id": "candidate:demo-bound",
                    "title": "Benchmark-facing derivation comparison",
                    "comparison_summary": "The reconstructed route matches the nearby L2 derivation up to one normalization convention that remains explicit.",
                    "compared_unit_ids": [
                        "derivation:chern-benchmark-demo",
                    ],
                    "comparison_scope": "bounded benchmark route",
                    "outcome": "partial_match",
                    "limitations": [
                        "Normalization differs by a convention-dependent factor pending explicit closure.",
                    ],
                },
                ensure_ascii=False,
                separators=(",", ":"),
            )
            + "\n",
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
                    "intended_l2_targets": ["derivation:demo-bound"],
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
        (run_root / "iteration_journal.json").write_text(
            json.dumps(
                {
                    "run_id": "run-001",
                    "status": "iterating",
                    "current_iteration_id": "iteration-002",
                    "iteration_ids": ["iteration-001", "iteration-002"],
                    "latest_conclusion_status": "continue_iteration",
                    "latest_staging_decision": "defer",
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        (iteration_root / "plan.contract.json").write_text(
            json.dumps(
                {
                    "topic_slug": "demo-topic",
                    "run_id": "run-001",
                    "iteration_id": "iteration-002",
                    "selected_action_summary": "Check whether the reconstructed response coefficient survives the benchmark normalization bridge.",
                    "verification_focus": "Bounded benchmark comparison",
                    "pass_conditions": [
                        "Keep the normalization bridge explicit.",
                        "Do not collapse k and sigma_xy before the comparison receipt is written.",
                    ],
                    "failure_signals": [
                        "A hidden factor appears in the benchmark convention.",
                    ],
                    "planned_outputs": [
                        "Updated derivation note",
                        "Comparison receipt",
                    ],
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        (iteration_root / "l4_return.json").write_text(
            json.dumps(
                {
                    "topic_slug": "demo-topic",
                    "run_id": "run-001",
                    "iteration_id": "iteration-002",
                    "status": "returned",
                    "returned_result_status": "partial",
                    "returned_result_summary": "The benchmark comparison agrees with the derivation backbone, but still leaves one normalization factor explicit rather than closed.",
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        (iteration_root / "l3_synthesis.json").write_text(
            json.dumps(
                {
                    "topic_slug": "demo-topic",
                    "run_id": "run-001",
                    "iteration_id": "iteration-002",
                    "status": "summarized",
                    "conclusion_status": "continue_iteration",
                    "staging_decision": "defer",
                    "synthesis_summary": "The bounded route is still useful, but the normalization caveat stays explicit and blocks any stronger claim.",
                    "next_step_summary": "Recover the omitted normalization factor from the cited benchmark note before widening the claim.",
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        notebook.append_notebook_entry(
            l3_root,
            kind="candidate_update",
            title="Bounded response derivation",
            body="A first candidate has been recorded.",
            status="ready_for_validation",
            run_id="run-001",
            details={"candidate_id": "candidate:demo-bound"},
        )

        tex = (l3_root / "research_notebook.tex").read_text(encoding="utf-8")

        assert r"\section{Research Question And Background}" in tex
        assert "Recover the bounded derivation and benchmark route." in tex
        assert r"\section{Setup, Notation, And Regime}" in tex
        assert "Use Euclidean-signature notation unless a source explicitly says otherwise." in tex
        assert r"\section{Working Ideas, Hypotheses, And Candidate Routes}" not in tex
        assert "A source-grounded derivation candidate for the response coefficient." in tex
        assert "Does the reconstructed derivation agree with the benchmark regime?" in tex
        assert r"\section{Iterative L3-L4 Research Record}" in tex
        assert "Check whether the reconstructed response coefficient survives the benchmark normalization bridge." in tex
        assert "Guiding candidate routes in this run" in tex
        assert "The benchmark comparison agrees with the derivation backbone" in tex
        assert "Recover the omitted normalization factor from the cited benchmark note" in tex
        assert "Derivation notes accumulated in this run" in tex
        assert "Comparison receipts accumulated in this run" in tex
        assert r"\section{Consolidated Derivation And Validation Status}" in tex
        assert "Response-coefficient reconstruction from source A" in tex
        assert "paper-a" in tex
        assert "This derivation is reconstructed in L3 from the cited source" in tex
        assert "Benchmark-facing derivation comparison" in tex
        assert "Normalization differs by a convention-dependent factor" in tex
        assert r"\section{Current Conclusion And Open Problems}" in tex
        assert "The sign convention for the response coefficient remains unresolved." in tex
        assert r"\section{Source Provenance And Reading Map}" in tex
        assert "Lecture Notes A" in tex
        assert "Paper A uses k while Paper B uses sigma\\_xy" in tex
        assert r"\section{Candidate Catalog}" in tex
        assert "candidate:demo-bound" in tex
        assert r"\section{Strategy And Failure Memory}" in tex
        assert "Check notation alignment before comparing benchmark formulas." in tex
        assert r"\section{Chronological Entry Log}" in tex


def test_notebook_prefers_research_report_surface_when_present() -> None:
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
                    "problem": {
                        "question": "Can the bounded route survive the benchmark comparison without hiding the normalization caveat?",
                        "literature_position": "Primary source basis: Lecture Notes A, Benchmark Note B",
                    },
                    "physical_motivation": "Make the normalization caveat explicit instead of polishing it away.",
                    "setup": {
                        "scope": ["Keep the bounded route explicit."],
                        "assumptions": ["Weak coupling."],
                        "notation": ["Use source convention first."],
                        "deliverables": ["One bounded derivation note."],
                    },
                    "candidate_routes": [
                        {
                            "title": "Bounded route",
                            "summary": "A bounded route to the response coefficient.",
                            "question": "Does the benchmark note preserve the same coefficient?",
                            "status": "ready_for_validation",
                            "validation_route": "benchmark_review",
                            "assumptions": ["Weak coupling."],
                        }
                    ],
                    "iteration_rounds": [
                        {
                            "iteration_id": "iteration-001",
                            "round_question": "Check the normalization bridge.",
                            "pass_conditions": ["Keep factor bookkeeping explicit."],
                            "failure_signals": ["A hidden factor appears."],
                            "returned_result_summary": "The main backbone survives, but one factor remains unresolved.",
                            "understanding_delta": "The caveat is real, not cosmetic.",
                            "next_step_summary": "Recover the omitted factor before promotion.",
                            "conclusion_status": "continue_iteration",
                            "staging_decision": "defer",
                        }
                    ],
                    "current_claims": [
                        {
                            "claim": "The bounded derivation backbone survives the benchmark comparison.",
                            "status": "validated_partial",
                            "support": "L3 derivation, L2 comparison receipt",
                            "limitation": "One normalization factor remains unresolved.",
                            "next_action": "Recover the omitted factor before promotion.",
                        }
                    ],
                    "current_derivation_spine": [],
                    "failed_routes": [],
                    "comparison_receipts": [],
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

        assert r"\section{Working Ideas, Hypotheses, And Candidate Routes}" not in tex
        assert "Check the normalization bridge." in tex
        assert r"\section{Current Claims And Stable Results}" in tex
        assert "The bounded derivation backbone survives the benchmark comparison." in tex
        assert "One normalization factor remains unresolved." in tex
        assert "Can the bounded route survive the benchmark comparison" in tex
