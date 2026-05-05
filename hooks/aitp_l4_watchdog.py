"""AITP L4 Watchdog — poll HPC background jobs and record completions.

Designed to be called from a cron job (Claude Code CronCreate or system cron).
Scans topics for active L4 background jobs, checks them via SSH, and records
completions via aitp_event.py and state.md updates.

Usage:
  python hooks/aitp_l4_watchdog.py <topics_root> [--topic <slug>]

  --topic <slug>: Check only one topic (faster for per-job crons)
  (no --topic):   Scan all topics for active L4 background jobs

Exit codes:
  0 — all jobs still running, or no active jobs
  1 — at least one job completed (caller should notify agent)
  2 — error (SSH connection failed, state file corruption, etc.)
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


# ── helpers (minimal copies from hook_utils to stay standalone) ──

def _parse_md(path: Path) -> tuple[dict, str]:
    """Parse YAML frontmatter + Markdown body."""
    import yaml
    text = path.read_text(encoding="utf-8")
    fm = {}
    body = text
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            try:
                fm = yaml.safe_load(parts[1]) or {}
            except yaml.YAMLError:
                pass
            body = parts[2]
    return fm, body


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _topics_dir(root: str) -> Path:
    return Path(root)


# ── job checking ──

def check_slurm_job(host: str, job_id: str, ssh_cmd: str = "ssh") -> dict:
    """Check a Slurm job status on a remote host.

    Returns: {"status": "running"|"completed"|"failed"|"timeout"|"cancelled"|"unknown",
              "exit_code": str, "raw": str}
    """
    cmd = [
        ssh_cmd, host,
        f"sacct -j {job_id} --noheader --format=State,ExitCode 2>/dev/null; "
        f"squeue -j {job_id} --noheader -o '%T' 2>/dev/null"
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        output = result.stdout.strip()
    except (subprocess.TimeoutExpired, OSError) as e:
        return {"status": "unknown", "exit_code": "", "raw": str(e)}

    if not output:
        return {"status": "unknown", "exit_code": "", "raw": "no output"}

    # Parse sacct states
    states = set()
    exit_codes = set()
    for line in output.splitlines():
        parts = line.split()
        if not parts:
            continue
        state = parts[0].rstrip("+")
        states.add(state)
        if len(parts) >= 2:
            exit_codes.add(parts[1])

    # squeue output gives live state
    live_state = ""
    for line in output.splitlines():
        if line.strip() in ("RUNNING", "PENDING", "COMPLETING", "SUSPENDED"):
            live_state = line.strip()

    # Determine combined status
    if live_state in ("RUNNING", "PENDING", "COMPLETING", "SUSPENDED"):
        return {"status": "running", "exit_code": "", "raw": live_state}

    # Not running — check final states
    terminal = {"COMPLETED", "FAILED", "TIMEOUT", "CANCELLED", "DEADLINE", "OUT_OF_MEMORY"}
    terminal_found = states & terminal
    if not terminal_found:
        # Maybe it's in transition — still treat as running
        if "RUNNING" in states:
            return {"status": "running", "exit_code": "", "raw": output}
        return {"status": "unknown", "exit_code": "|".join(sorted(exit_codes)), "raw": output}

    if "COMPLETED" in states:
        all_ok = all(ec in ("0:0", "0") for ec in exit_codes if ec)
        if all_ok:
            return {"status": "completed", "exit_code": "0:0", "raw": output}
        return {"status": "completed_with_errors",
                "exit_code": "|".join(sorted(exit_codes)),
                "raw": output}
    if "FAILED" in states:
        return {"status": "failed", "exit_code": "|".join(sorted(exit_codes)), "raw": output}
    if "CANCELLED" in states:
        return {"status": "cancelled", "exit_code": "|".join(sorted(exit_codes)), "raw": output}
    if "TIMEOUT" in states:
        return {"status": "timeout", "exit_code": "|".join(sorted(exit_codes)), "raw": output}
    if "OUT_OF_MEMORY" in states:
        return {"status": "oom", "exit_code": "|".join(sorted(exit_codes)), "raw": output}

    return {"status": "completed", "exit_code": "|".join(sorted(exit_codes)), "raw": output}


# ── topic scanning ──

def get_active_jobs(topics_root: str) -> list[dict]:
    """Scan all topics for active L4 background jobs.

    Returns list of {topic_slug, job_id, host, submitted_at, state_path}
    """
    active = []
    td = _topics_dir(topics_root)
    if not td.exists():
        return active

    for topic_dir in sorted(td.iterdir()):
        if not topic_dir.is_dir():
            continue
        state_path = topic_dir / "state.md"
        if not state_path.exists():
            continue

        fm, _ = _parse_md(state_path)
        l4_status = fm.get("l4_background_status", "")
        if l4_status != "submitted":
            continue

        job_id = fm.get("l4_job_id", "")
        host = fm.get("l4_job_host", "")
        if not job_id or not host:
            continue

        active.append({
            "topic_slug": topic_dir.name,
            "job_id": job_id,
            "host": host,
            "submitted_at": fm.get("l4_job_submitted_at", ""),
            "state_path": state_path,
            "topic_root": topic_dir,
        })

    return active


def record_completion(topic_root: Path, job_status: str, job_result_raw: str = "") -> None:
    """Record L4 job completion: update state.md and append to runtime/log.md."""
    import yaml

    state_path = topic_root / "state.md"
    if not state_path.exists():
        print(f"ERROR: state.md not found at {state_path}", file=sys.stderr)
        return

    fm, body = _parse_md(state_path)
    old_status = fm.get("l4_background_status", "")
    fm["l4_background_status"] = "completed"
    fm["l4_job_result"] = job_status
    fm["l4_job_completed_at"] = _now()
    if job_result_raw:
        fm.setdefault("l4_job_output_summary", job_result_raw[:200])
    fm["updated_at"] = _now()

    # Write state.md with safe YAML values
    state_text = "---\n"
    for k, v in fm.items():
        if isinstance(v, str) and (":" in v or "#" in v or v.startswith("{") or v.startswith("[")):
            state_text += f"{k}: '{v}'\n"
        else:
            state_text += f"{k}: {v}\n"
    state_text += "---\n" + body
    state_path.write_text(state_text, encoding="utf-8")

    # Append to runtime/log.md
    log_path = topic_root / "runtime" / "log.md"
    event = f"L4_watchdog_completion: job {job_status}. {job_result_raw}"
    _append_log(log_path, event)

    print(f"Recorded: {topic_root.name} L4 job → {job_status}", file=sys.stderr)


def _append_log(log_path: Path, event: str) -> None:
    if log_path.exists():
        existing = log_path.read_text(encoding="utf-8")
    else:
        existing = "# Topic Log\n\n## Events\n"
    if not existing.endswith("\n"):
        existing += "\n"
    log_path.write_text(existing + f"- {_now()} {event}\n", encoding="utf-8")


# ── SSH host mapping ──

_HOST_ALIASES = {
    "dongfang": "dongfang",
    "df": "dongfang",
    "fisher": "dongfang",
    "kouxiang": "kouxiang",
    "el": "elhacedor@10.0.0.1",  # adjust as needed
}


def resolve_host(host: str) -> tuple[str, str]:
    """Resolve a host alias to (ssh_target, display_name)."""
    alias = host.lower().strip()
    ssh_target = _HOST_ALIASES.get(alias, host)
    return ssh_target, host


# ── main ──

def main():
    import argparse
    p = argparse.ArgumentParser(description="AITP L4 Watchdog — poll HPC background jobs")
    p.add_argument("topics_root", help="Path to AITP topics directory")
    p.add_argument("--topic", "-t", help="Check only this topic slug")
    p.add_argument("--ssh", default="ssh", help="SSH command (default: ssh)")
    args = p.parse_args()

    # Collect jobs
    if args.topic:
        topic_root = Path(args.topics_root) / args.topic
        state_path = topic_root / "state.md"
        if not state_path.exists():
            print(f"ERROR: Topic {args.topic} not found", file=sys.stderr)
            sys.exit(2)
        fm, _ = _parse_md(state_path)
        jobs = [{
            "topic_slug": args.topic,
            "job_id": fm.get("l4_job_id", ""),
            "host": fm.get("l4_job_host", ""),
            "submitted_at": fm.get("l4_job_submitted_at", ""),
            "state_path": state_path,
            "topic_root": topic_root,
        }]
    else:
        jobs = get_active_jobs(args.topics_root)

    if not jobs:
        print("No active L4 background jobs.")
        sys.exit(0)

    any_completed = False

    for job in jobs:
        ssh_target, display_host = resolve_host(job["host"])
        result = check_slurm_job(ssh_target, job["job_id"], ssh_cmd=args.ssh)

        status = result["status"]
        print(f"[{job['topic_slug']}] Job {job['job_id']}@{display_host}: {status}")

        if status == "running":
            continue

        # Terminal state — record it
        record_completion(job["topic_root"], status, json.dumps(result)[:500])
        any_completed = True

    if any_completed:
        print("\nOne or more L4 background jobs completed.", file=sys.stderr)
        sys.exit(1)  # Signal caller: job completed
    else:
        sys.exit(0)  # All still running


if __name__ == "__main__":
    main()
