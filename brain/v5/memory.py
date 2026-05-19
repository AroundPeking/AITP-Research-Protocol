"""L2 memory and promotion packet management for AITP v5."""

from __future__ import annotations

from brain.v5.ids import prefixed_id
from brain.v5.models import PromotionPacketRecord
from brain.v5.store import write_record
from brain.v5.workspace import WorkspacePaths


def create_promotion_packet(
    ws: WorkspacePaths,
    *,
    topic_id: str,
    claim_id: str,
    proposed_memory_kind: str = "scoped_claim",
    scope: str = "",
    evidence_refs: list[str] | None = None,
    non_claims: list[str] | None = None,
    known_failure_modes: list[str] | None = None,
) -> PromotionPacketRecord:
    packet_id = prefixed_id("packet", claim_id)
    packet = PromotionPacketRecord(
        packet_id=packet_id,
        topic_id=topic_id,
        claim_id=claim_id,
        proposed_memory_kind=proposed_memory_kind,
        scope=scope,
        evidence_refs=evidence_refs or [],
        non_claims=non_claims or [],
        known_failure_modes=known_failure_modes or [],
    )
    write_record(ws.registry_dir("promotion_packets") / f"{packet_id}.md", packet)
    return packet
