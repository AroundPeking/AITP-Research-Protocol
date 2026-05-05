"""Pydantic contract models for AITP artifacts.

Provides typed schemas for Candidate and Review artifacts.
Model-level validation replaces the current string-matching / character-counting
gate checks in checks.py.

Usage:
    try:
        cand = CandidateContract.model_validate(data, context={"topic_root": root})
    except ValidationError as e:
        return {"error": str(e)}
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator, ValidationInfo, model_validator


class CandidateContract(BaseModel):
    """Schema for L3 candidate artifacts."""

    model_config = {"extra": "forbid"}

    candidate_id: str = Field(..., min_length=1, description="Unique candidate slug")
    status: Literal["draft", "validated", "rejected", "promoted"] = "draft"
    derivation_chain_id: str = Field(..., min_length=1, description="Must reference an existing derivation chain")
    source_refs: list[str] = Field(..., min_length=1, description="At least one source reference required")
    claim_statement: str = Field(..., min_length=20, description="The claim in one sentence")
    mathematical_expression: str = ""
    depends_on: list[str] = []

    @field_validator("derivation_chain_id")
    @classmethod
    def chain_must_exist(cls, v: str, info: ValidationInfo) -> str:
        """Verify the derivation_chain_id resolves to actual derivation steps."""
        topic_root = info.context.get("topic_root") if info.context else None
        if topic_root:
            steps_dir = Path(topic_root) / "L2" / "graph" / "steps"
            if not steps_dir.exists():
                raise ValueError(f"Derivation chain '{v}': no steps directory found")
            # Check for steps referencing this chain
            import yaml
            chain_steps = []
            for step_path in steps_dir.glob("*.md"):
                fm = {}
                if step_path.exists():
                    text = step_path.read_text(encoding="utf-8")
                    if text.startswith("---"):
                        parts = text.split("---", 2)
                        if len(parts) >= 3:
                            try:
                                fm = yaml.safe_load(parts[1]) or {}
                            except Exception:
                                pass
                if fm.get("chain_id") == v:
                    chain_steps.append(step_path.stem)
            if not chain_steps:
                raise ValueError(f"Derivation chain '{v}' has no recorded steps")
        return v


class ReviewContract(BaseModel):
    """Schema for L4 review artifacts."""

    model_config = {"extra": "forbid"}

    candidate_id: str = Field(..., min_length=1)
    verifier_type: Literal["algebraic", "physical", "numerical", "skeptic", "matrix"] = "algebraic"
    outcome: Literal["pass", "fail", "uncertain", "contradiction"] = "uncertain"
    check_results: dict[str, str] = Field(
        default_factory=dict,
        description="Must contain all required physics check fields"
    )
    counterargument: str = ""
    issues: list[dict[str, str]] = []
    l2_citations: list[str] = []

    @field_validator("counterargument")
    @classmethod
    def required_for_pass(cls, v: str, info: ValidationInfo) -> str:
        if info.data.get("outcome") == "pass" and len(v.strip()) < 50:
            raise ValueError("Counterargument ≥50 chars required for 'pass' outcome")
        return v

    @field_validator("check_results")
    @classmethod
    def required_fields_for_pass(cls, v: dict, info: ValidationInfo) -> dict:
        if info.data.get("outcome") == "pass":
            required = [
                "dimensional_consistency",
                "symmetry_compatibility",
                "limiting_case_check",
                "conservation_check",
                "correspondence_check",
            ]
            missing = [f for f in required if not v.get(f, "").strip()]
            if missing:
                raise ValueError(f"Missing required check results for 'pass': {missing}")
        return v


# ── Validation helpers ───────────────────────────────────────────────────

def validate_candidate(data: dict[str, Any], topic_root: Path | None = None) -> CandidateContract:
    """Validate and return a CandidateContract. Raises ValidationError on failure."""
    ctx = {"topic_root": topic_root} if topic_root else None
    return CandidateContract.model_validate(data, context=ctx)


def validate_review(data: dict[str, Any]) -> ReviewContract:
    """Validate and return a ReviewContract. Raises ValidationError on failure."""
    return ReviewContract.model_validate(data)
