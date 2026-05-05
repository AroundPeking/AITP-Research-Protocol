"""Protocol version migration: v0.6 → v1.0.

Adds missing v1.0 state.md fields to topics created with older protocol versions.
Idempotent — safe to run multiple times.
"""
from __future__ import annotations
from pathlib import Path
import os

DEFAULT_TOPICS_ROOT = os.environ.get(
    "AITP_TOPICS_ROOT",
    "D:/BaiduSyncdisk/Theoretical-Physics/research/aitp-topics"
)

_POSTURE_MAP = {"L0": "discover", "L1": "read", "L3": "derive", "L4": "verify"}


def migrate_topic(topic_root: Path) -> dict[str, str]:
    """Add missing v1.0 fields to a topic's state.md. Returns {field: new_value}."""
    from brain.cli.state import _parse_md_local, _write_md_local

    state_path = topic_root / "state.md"
    if not state_path.exists():
        return {"error": "state.md not found"}

    fm, body = _parse_md_local(state_path)
    protocol = fm.get("protocol_version", "v0.6")
    if protocol == "v1.0":
        return {"status": "already v1.0"}

    added = {}

    # v1.0 required fields — always set protocol_version
    fm["protocol_version"] = "v1.0"
    added["protocol_version"] = "v1.0"

    defaults = {
        "research_intensity": "standard",
        "memory_gate_enabled": False,
        "research_loop_active": False,
        "l4_cycle_count": 0,
    }
    for key, default in defaults.items():
        if key not in fm:
            fm[key] = default
            added[key] = str(default)

    # posture if missing
    if "posture" not in fm:
        stage = fm.get("stage", "L0")
        fm["posture"] = _POSTURE_MAP.get(stage, "discover")
        added["posture"] = fm["posture"]

    # l3_activity if missing and stage is L3
    if "l3_activity" not in fm and fm.get("stage") == "L3":
        fm["l3_activity"] = "derive"
        added["l3_activity"] = "derive"

    fm["updated_at"] = _now_iso()
    _write_md_local(state_path, fm, body)

    if added:
        added["status"] = f"migrated v0.6 → v1.0 ({len(added)} fields)"
    return added


def _now_iso() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()


def cmd_migrate(args):
    """Migrate a topic from v0.6 to v1.0 protocol."""
    base = Path(DEFAULT_TOPICS_ROOT)
    slug = args.topic
    for candidate in [base / slug, base / "topics" / slug]:
        if (candidate / "state.md").exists():
            result = migrate_topic(candidate)
            for k, v in result.items():
                print(f"  {k}: {v}")
            return 0 if "error" not in result else 1

    print(f"Topic '{slug}' not found")
    return 1
