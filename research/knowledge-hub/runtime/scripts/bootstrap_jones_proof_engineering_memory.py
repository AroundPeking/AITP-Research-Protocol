from __future__ import annotations

import argparse
import json
from pathlib import Path

from knowledge_hub.proof_engineering_bootstrap import materialize_jones_proof_engineering_seed


ROOT = Path(__file__).resolve().parents[2]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Seed the Jones proof-engineering strategy memory rows and canonical proof_fragment into a kernel root.",
    )
    parser.add_argument("--kernel-root", default=str(ROOT))
    parser.add_argument("--topic-slug", default="jones-von-neumann-algebras")
    parser.add_argument("--run-id", default="2026-04-12-jones-proof-engineering-bootstrap")
    parser.add_argument("--updated-by", default="aitp-cli")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = materialize_jones_proof_engineering_seed(
        Path(args.kernel_root),
        topic_slug=args.topic_slug,
        run_id=args.run_id,
        updated_by=args.updated_by,
    )
    if args.json:
        print(json.dumps(payload, ensure_ascii=True, indent=2))
    else:
        print(json.dumps(payload, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
