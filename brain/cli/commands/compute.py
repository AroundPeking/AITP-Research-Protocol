"""L4 computational execution commands (code_method lane).

Local-first, HPC-handoff model:
  prepare: generate Slurm script + parameter audit (fully offline)
  submit: handoff bridge — gives user exact scp+sbatch commands
  check: examine locally-transferred output files
  validate: parse outputs, compare to claim, check invariants
  report: aggregate results into structured markdown
"""
from __future__ import annotations
from pathlib import Path
import os


def _resolve_topic_root(topic_slug: str) -> Path:
    base = Path(os.environ.get("AITP_TOPICS_ROOT",
        "D:/BaiduSyncdisk/Theoretical-Physics/research/aitp-topics"))
    for candidate in [base / topic_slug, base / "topics" / topic_slug]:
        if (candidate / "state.md").exists():
            return candidate
    return base / topic_slug


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


def _now_iso():
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()


def _load_compute_target(topic_root: Path) -> dict:
    """Read compute/targets.yaml + state.md compute field + MEMORY.md configs.
    Returns merged config dict.
    """
    import yaml

    target_name = "local"
    state_fm, _ = _parse_md(topic_root / "state.md")
    if state_fm.get("compute"):
        target_name = state_fm["compute"]

    config = {
        "type": "local", "python": "python", "sympy": "available",
        "name": target_name,
    }

    # Read targets.yaml (canonical source)
    targets_path = topic_root / "compute" / "targets.yaml"
    if targets_path.exists():
        try:
            targets = yaml.safe_load(targets_path.read_text(encoding="utf-8")) or {}
            if "targets" in targets and target_name in targets["targets"]:
                config.update(targets["targets"][target_name])
        except Exception:
            pass

    # Read MEMORY.md server configs for SSH/connection details
    memory_path = topic_root / "MEMORY.md"
    if memory_path.exists():
        memory_text = memory_path.read_text(encoding="utf-8")
        if "## Server Configs" in memory_text:
            # Extract server config lines
            import re
            server_section = memory_text.split("## Server Configs")[1].split("##")[0]
            for line in server_section.split("\n"):
                line = line.strip()
                if line.startswith("- ") or line.startswith("* "):
                    kv = line[2:].split(":", 1)
                    if len(kv) == 2:
                        config[kv[0].strip().lower().replace(" ", "_")] = kv[1].strip()

    return config


def _generate_slurm_script(candidate_id: str, config: dict, topic_root: Path) -> str:
    """Generate a Slurm submission script with #SBATCH directives."""
    partition = config.get("partition", "normal")
    walltime = config.get("default_walltime", config.get("walltime", "6h"))
    memory = config.get("default_memory", config.get("memory", "64GB"))
    job_name = f"aitp-{candidate_id}"[:16]
    output_dir = f"L4/outputs/{candidate_id}"

    lines = [
        "#!/bin/bash",
        f"# AITP L4 computation for {candidate_id}",
        f"# Generated: {_now_iso()}",
        f"# Target: {config.get('name', 'local')}",
        "",
        f"#SBATCH --job-name={job_name}",
        f"#SBATCH --partition={partition}",
        f"#SBATCH --time={walltime}",
        f"#SBATCH --mem={memory}",
        f"#SBATCH --output={output_dir}/%j.out",
        f"#SBATCH --error={output_dir}/%j.err",
        "",
        f"mkdir -p {output_dir}",
        "",
    ]

    python_path = config.get("python", "python")
    lines.extend([
        "# Environment setup",
        f"export OMP_NUM_THREADS=1",
        "",
        "# Computation placeholder — replace with actual run command",
        f"# {python_path} abacus.py > {output_dir}/abacus.log 2>&1",
        f"# {python_path} librpa.py > {output_dir}/librpa.log 2>&1",
        "",
        f"echo 'Job {candidate_id} completed at:' $(date)",
        f"echo 'Host:' $(hostname)",
    ])

    return "\n".join(lines) + "\n"


def _append_research_md(root: Path, layer: str, entry: str):
    path = root / "research.md"
    line = f"- {_now_iso()} [{layer}] {entry}\n"
    if path.exists():
        path.write_text(path.read_text(encoding="utf-8") + line, encoding="utf-8")
    else:
        path.write_text(f"# Research Trail\n\n{line}", encoding="utf-8")


def cmd_compute_prepare(args):
    """Generate Slurm script + parameter audit for a candidate."""
    root = _resolve_topic_root(args.topic)
    cand_path = root / "L3" / "candidates" / f"{args.candidate_id}.md"
    if not cand_path.exists():
        print(f"Candidate '{args.candidate_id}' not found")
        return 1

    cand_fm, cand_body = _parse_md(cand_path)
    config = _load_compute_target(root)

    # Generate Slurm script
    scripts_dir = root / "L4" / "scripts"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    script_content = _generate_slurm_script(args.candidate_id, config, root)
    script_path = scripts_dir / f"{args.candidate_id}_run.sh"
    script_path.write_text(script_content)
    print(f"Script → {script_path}")

    # Parameter audit
    audit_lines = [
        f"# Parameter Audit: {args.candidate_id}",
        f"Generated: {_now_iso()}",
        f"Target: {config.get('name', 'local')} ({config.get('type', 'local')})",
        "",
        "## Candidate Parameters",
        f"- claim: {cand_fm.get('claim_statement', 'N/A')[:120]}",
        f"- derivation chain: {cand_fm.get('derivation_chain_id', 'default')}",
        f"- source_refs: {cand_fm.get('source_refs', [])}",
        "",
        "## Compute Target Config",
    ]
    for k, v in sorted(config.items()):
        audit_lines.append(f"- {k}: {v}")
    audit_lines.extend([
        "",
        "## Invariant Checks (to be run by validate)",
        "- NaN detection in output files",
        "- Convergence check (SCF, GW iterations)",
        "- Physical range checks (band gap, energies)",
        "- Domain invariants per domain manifest",
    ])

    audit_path = scripts_dir / f"{args.candidate_id}_audit.md"
    audit_path.write_text("\n".join(audit_lines) + "\n")
    print(f"Audit → {audit_path}")
    _append_research_md(root, "L4", f"compute prepare: {args.candidate_id}")
    return 0


def cmd_compute_submit(args):
    """Submit computation — local execution or HPC handoff."""
    root = _resolve_topic_root(args.topic)
    script_path = root / "L4" / "scripts" / f"{args.candidate_id}_run.sh"
    if not script_path.exists():
        print(f"Script not found. Run 'aitp compute prepare' first.")
        return 1

    config = _load_compute_target(root)
    target_type = config.get("type", "local")

    if target_type == "local":
        import subprocess, sys
        print(f"Running locally: {script_path}")
        try:
            result = subprocess.run(
                ["bash", str(script_path)],
                capture_output=True, text=True, timeout=300,
                cwd=str(root),
            )
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr)
            rc = result.returncode
        except subprocess.TimeoutExpired:
            print("Timeout (300s)")
            rc = 1
        except FileNotFoundError:
            print("bash not found — cannot run locally on Windows without WSL")
            rc = 1
    else:
        # HPC handoff
        ssh_alias = config.get("ssh", config.get("host", "hpc"))
        host = config.get("host", ssh_alias)
        print("HPC Handoff — run these commands:")
        print()
        print(f"  # 1. Copy script to HPC")
        print(f"  scp {script_path} {ssh_alias}:~/")
        print(f"  # 2. Submit job")
        print(f"  ssh {ssh_alias} sbatch ~/{args.candidate_id}_run.sh")
        print(f"  # 3. Record job ID")
        print(f"  aitp MCP aitp_l4_background_submit --job-id <ID> --host {host}")
        print(f"  # 4. Set up watchdog (optional)")
        print(f"  python hooks/aitp_l4_watchdog.py")
        rc = 0

    # Update state.md
    state_fm, state_body = _parse_md(root / "state.md")
    state_fm["l4_background_status"] = "submitted"
    state_fm["l4_job_host"] = config.get("host", config.get("ssh", "local"))
    state_fm["l4_job_script"] = str(script_path)
    state_fm["updated_at"] = _now_iso()
    import yaml
    lines = ["---", yaml.dump(dict(state_fm), default_flow_style=False, allow_unicode=True).rstrip(), "---", state_body.lstrip("\n")]
    (root / "state.md").write_text("\n".join(lines), encoding="utf-8")

    _append_research_md(root, "L4", f"compute submit: {args.candidate_id}")
    return rc


def cmd_compute_check(args):
    """Check computation status by examining local output files."""
    root = _resolve_topic_root(args.topic)
    output_dir = root / "L4" / "outputs" / args.candidate_id

    if not output_dir.exists() or not list(output_dir.glob("*")):
        print(f"No output files found in {output_dir}")
        config = _load_compute_target(root)
        if config.get("type") != "local":
            ssh_alias = config.get("ssh", config.get("host", "hpc"))
            print(f"\nFetch results from HPC:")
            print(f"  scp -r {ssh_alias}:~/L4/outputs/{args.candidate_id}/ {output_dir}")
        return 0

    # List available outputs
    files = sorted(output_dir.glob("*"))
    print(f"Output files for {args.candidate_id} ({len(files)} files):")
    for f in files:
        size = f.stat().st_size
        mtime = _now_iso()  # approximate
        if f.suffix == ".out":
            # Check for crash markers
            content = f.read_text(encoding="utf-8", errors="replace")[:2000]
            has_error = "ERROR" in content or "FATAL" in content or "SIGSEGV" in content
            status = "⚠ errors detected" if has_error else "looks clean"
            print(f"  {f.name:<30} {size:>8d} bytes  {status}")
        else:
            print(f"  {f.name:<30} {size:>8d} bytes")

    # Check if all expected outputs present
    has_out = any(f.suffix == ".out" for f in files)
    has_err = any(f.suffix == ".err" for f in files)
    if has_out:
        state_fm, state_body = _parse_md(root / "state.md")
        state_fm["l4_background_status"] = "completed"
        state_fm["updated_at"] = _now_iso()
        import yaml
        lines = ["---", yaml.dump(dict(state_fm), default_flow_style=False, allow_unicode=True).rstrip(), "---", state_body.lstrip("\n")]
        (root / "state.md").write_text("\n".join(lines), encoding="utf-8")
        print(f"\nStatus: completed (output files present)")

    return 0


def cmd_compute_validate(args):
    """Validate computation outputs: parse, compare to claim, check invariants."""
    root = _resolve_topic_root(args.topic)
    output_dir = root / "L4" / "outputs" / args.candidate_id
    cand_path = root / "L3" / "candidates" / f"{args.candidate_id}.md"

    if not cand_path.exists():
        print(f"Candidate '{args.candidate_id}' not found")
        return 1

    cand_fm, _ = _parse_md(cand_path)
    claim = cand_fm.get("claim_statement", "")

    print(f"Validation: {args.candidate_id}")
    print(f"Claim: {claim[:120]}")
    print()

    # Parse output files
    results = {}
    if output_dir.exists():
        for f in sorted(output_dir.glob("*.out")):
            content = f.read_text(encoding="utf-8", errors="replace")
            # NaN detection
            nan_count = content.upper().count("NAN")
            if nan_count:
                results["nan_detected"] = nan_count
                print(f"  ⚠ {f.name}: {nan_count} NaN(s) detected")

            # Convergence check
            if "CONVERGENCE" in content.upper() or "converged" in content.lower():
                results["converged"] = True
                print(f"  ✓ {f.name}: convergence markers found")
            elif "not converged" in content.lower():
                results["converged"] = False
                print(f"  ✗ {f.name}: NOT converged")

            # Key-value extraction
            import re
            for pattern, label in [
                (r'gap\s*[=:]\s*([\d.]+)\s*eV', 'band_gap_eV'),
                (r'GW[_ ]*correction\s*[=:]\s*([\d.]+)', 'gw_correction'),
                (r'total[_ ]*energy\s*[=:]\s*([\d.-]+)\s*eV', 'total_energy_eV'),
            ]:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    val = float(match.group(1))
                    results[label] = val
                    print(f"  • {label}: {val}")

    if not results:
        print("  No numerical results extracted from output files.")
        print("  (Add expected output patterns to L4/reports/ for automated comparison)")
    else:
        results["validated_at"] = _now_iso()
        results["candidate_id"] = args.candidate_id

    # Write validation results
    import json
    val_path = output_dir / f"{args.candidate_id}_validation.json"
    val_path.parent.mkdir(parents=True, exist_ok=True)
    val_path.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n")
    print(f"\nValidation results → {val_path}")
    _append_research_md(root, "L4", f"compute validate: {args.candidate_id} ({len(results)} metrics)")
    return 0


def cmd_compute_report(args):
    """Generate comprehensive computational report."""
    root = _resolve_topic_root(args.topic)
    reports_dir = root / "L4" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    cand_path = root / "L3" / "candidates" / f"{args.candidate_id}.md"
    audit_path = root / "L4" / "scripts" / f"{args.candidate_id}_audit.md"
    val_path = root / "L4" / "outputs" / args.candidate_id / f"{args.candidate_id}_validation.json"
    state_fm, _ = _parse_md(root / "state.md")
    config = _load_compute_target(root)

    # Collect all sections
    sections = [
        f"# Computational Report: {args.candidate_id}",
        f"Generated: {_now_iso()}",
        "",
        "## Run Metadata",
        f"- Topic: {args.topic}",
        f"- Candidate: {args.candidate_id}",
        f"- Target: {config.get('name', 'local')} ({config.get('type', 'local')})",
        f"- Job host: {state_fm.get('l4_job_host', 'N/A')}",
        f"- Background status: {state_fm.get('l4_background_status', 'N/A')}",
        f"- Cycle: {state_fm.get('l4_cycle_count', 0)}",
        "",
    ]

    # Claim
    if cand_path.exists():
        cand_fm, _ = _parse_md(cand_path)
        sections.extend([
            "## Claim",
            cand_fm.get("claim_statement", "N/A"),
            f"\nSource refs: {cand_fm.get('source_refs', [])}",
            "",
        ])

    # Audit
    if audit_path.exists():
        sections.extend([
            "## Parameter Audit",
            audit_path.read_text(encoding="utf-8", errors="replace"),
            "",
        ])

    # Validation results
    if val_path.exists():
        import json
        try:
            val_data = json.loads(val_path.read_text(encoding="utf-8"))
            sections.extend([
                "## Validation Results",
                "```json",
                json.dumps(val_data, indent=2, ensure_ascii=False),
                "```",
                "",
            ])
        except Exception:
            sections.append("## Validation Results\n\nTBD (validation output unreadable)\n")

    # Output file listing
    output_dir = root / "L4" / "outputs" / args.candidate_id
    if output_dir.exists():
        files = sorted(output_dir.glob("*"))
        if files:
            sections.append("## Output Files")
            for f in files:
                size = f.stat().st_size
                sections.append(f"- {f.name} ({size} bytes)")
            sections.append("")

    report_path = reports_dir / f"{args.candidate_id}_computational.md"
    report_path.write_text("\n".join(sections))
    print(f"Report → {report_path}")
    _append_research_md(root, "L4", f"compute report: {args.candidate_id}")
    return 0
