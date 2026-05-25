"""Records for legacy source-reconstruction repair provenance."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class LegacySourceReconstructionRepairRecord:
    repair_id: str
    migration_run_id: str
    migration_dir: str
    topic: str
    active_claim_id: str
    review_id: str
    repair_type: str
    evidence_id: str
    basis_refs: list[str] = field(default_factory=list)
    applied: bool = False
    required_actions: list[str] = field(default_factory=list)
    summary_inputs_trusted: bool = False
    can_update_claim_trust: bool = False
    kind: str = "legacy_source_reconstruction_repair"

    @property
    def record_id(self) -> str:
        return self.repair_id
