from __future__ import annotations

import json
from pathlib import Path


def locate_reference_topic_dir(
    *,
    package_root: Path,
    repo_root: Path,
    topic_slug: str,
) -> Path:
    candidates = [
        package_root / "topics" / topic_slug,
        repo_root / "research" / "knowledge-hub" / "topics" / topic_slug,
    ]

    repo_parts = list(repo_root.parts)
    if ".worktrees" in repo_parts:
        worktrees_index = repo_parts.index(".worktrees")
        common_repo_root = Path(*repo_parts[:worktrees_index])
        candidates.append(
            common_repo_root / "research" / "knowledge-hub" / "topics" / topic_slug
        )

    for candidate in candidates:
        if candidate.exists():
            return candidate

    searched = "\n".join(str(candidate) for candidate in candidates)
    raise FileNotFoundError(
        f"Reference topic directory is missing for topic '{topic_slug}'. Searched:\n{searched}"
    )


def locate_reference_topic_root(
    *,
    package_root: Path,
    repo_root: Path,
    topic_slug: str,
) -> Path:
    return locate_reference_topic_dir(
        package_root=package_root,
        repo_root=repo_root,
        topic_slug=topic_slug,
    ) / "L0"


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")


def create_minimal_tpkn_backend(target_root: Path) -> None:
    for relative in (
        "docs",
        "schema",
        "scripts",
        "sources",
        "units/concepts",
        "units/definitions",
        "units/notations",
        "units/assumptions",
        "units/regimes",
        "units/theorems",
        "units/claims",
        "units/proof-fragments",
        "units/derivation-steps",
        "units/derivations",
        "units/methods",
        "units/topic-skill-projections",
        "units/bridges",
        "units/examples",
        "units/caveats",
        "units/equivalences",
        "units/symbol-bindings",
        "units/equations",
        "units/quantities",
        "units/models",
        "units/source-maps",
        "units/warnings",
        "units/regression-questions",
        "units/question-oracles",
        "edges",
        "indexes",
        "portal",
        "human-mirror",
    ):
        (target_root / relative).mkdir(parents=True, exist_ok=True)
    for relative in (
        "docs/PROTOCOLS.md",
        "docs/L2_RETRIEVAL_PROTOCOL.md",
        "docs/OBJECT_MODEL.md",
        "docs/L2_BRIDGE_PROTOCOL.md",
    ):
        (target_root / relative).write_text("# Minimal TPKN backend seed\n", encoding="utf-8")
    (target_root / "edges" / "edges.jsonl").write_text("", encoding="utf-8")
    _write_json(target_root / "schema" / "unit.schema.json", {"title": "minimal-unit-schema"})
    _write_json(target_root / "schema" / "source-manifest.schema.json", {"title": "minimal-source-schema"})
    (target_root / "scripts" / "kb.py").write_text(
        """from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UNIT_DIRS = {
    "concept": ROOT / "units" / "concepts",
    "definition": ROOT / "units" / "definitions",
    "notation": ROOT / "units" / "notations",
    "assumption": ROOT / "units" / "assumptions",
    "regime": ROOT / "units" / "regimes",
    "theorem": ROOT / "units" / "theorems",
    "claim": ROOT / "units" / "claims",
    "proof_fragment": ROOT / "units" / "proof-fragments",
    "derivation_step": ROOT / "units" / "derivation-steps",
    "derivation": ROOT / "units" / "derivations",
    "method": ROOT / "units" / "methods",
    "topic_skill_projection": ROOT / "units" / "topic-skill-projections",
    "bridge": ROOT / "units" / "bridges",
    "example": ROOT / "units" / "examples",
    "caveat": ROOT / "units" / "caveats",
    "equivalence": ROOT / "units" / "equivalences",
    "symbol_binding": ROOT / "units" / "symbol-bindings",
    "equation": ROOT / "units" / "equations",
    "quantity": ROOT / "units" / "quantities",
    "model": ROOT / "units" / "models",
    "source_map": ROOT / "units" / "source-maps",
    "warning": ROOT / "units" / "warnings",
    "regression_question": ROOT / "units" / "regression-questions",
    "question_oracle": ROOT / "units" / "question-oracles",
}

def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

def build() -> None:
    rows = []
    for unit_dir in UNIT_DIRS.values():
        unit_dir.mkdir(parents=True, exist_ok=True)
        for path in sorted(unit_dir.glob("*.json")):
            payload = read_json(path)
            rows.append(
                {
                    "id": payload["id"],
                    "type": payload["type"],
                    "title": payload["title"],
                    "summary": payload["summary"],
                    "path": str(path.relative_to(ROOT)),
                }
            )
    unit_index = ROOT / "indexes" / "unit_index.jsonl"
    unit_index.parent.mkdir(parents=True, exist_ok=True)
    unit_index.write_text(
        "".join(json.dumps(row, ensure_ascii=True) + "\\n" for row in rows),
        encoding="utf-8",
    )

def main() -> int:
    if len(sys.argv) < 2:
        return 1
    command = sys.argv[1]
    if command == "check":
        for unit_dir in UNIT_DIRS.values():
            unit_dir.mkdir(parents=True, exist_ok=True)
        return 0
    if command == "build":
        build()
        return 0
    return 1

if __name__ == "__main__":
    raise SystemExit(main())
""",
        encoding="utf-8",
    )
