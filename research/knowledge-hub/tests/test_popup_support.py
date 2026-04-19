from __future__ import annotations

import pytest

from knowledge_hub.popup_support import (
    build_popup_payload,
    detect_popup_trigger,
    render_popup_markdown,
    resolve_popup_choice,
)


class MockService:
    def __init__(self):
        self.kernel_root = None
        self.calls: list[dict] = []

    def approve_promotion(self, **kwargs):
        self.calls.append({"method": "approve_promotion", "kwargs": kwargs})
        return {"status": "approved", **kwargs}

    def reject_promotion(self, **kwargs):
        self.calls.append({"method": "reject_promotion", "kwargs": kwargs})
        return {"status": "rejected", **kwargs}

    def resolve_operator_checkpoint(self, **kwargs):
        self.calls.append({"method": "resolve_operator_checkpoint", "kwargs": kwargs})
        return {"status": "resolved", **kwargs}

    def steer_topic(self, **kwargs):
        self.calls.append({"method": "steer_topic", "kwargs": kwargs})
        return {"status": "steered", **kwargs}


def test_detect_popup_trigger__promotion_gate_pending():
    result = detect_popup_trigger(
        topic_slug="t1",
        promotion_gate={"status": "pending_human_approval", "candidate_id": "c1"},
        operator_checkpoint={},
        pending_decision_points=[],
        h_plane_payload={},
    )
    assert result["needs_popup"] is True
    assert result["popup_kind"] == "promotion_gate"
    assert result["priority"] == 1


def test_detect_popup_trigger__operator_checkpoint():
    result = detect_popup_trigger(
        topic_slug="t1",
        promotion_gate={"status": "not_requested"},
        operator_checkpoint={"status": "requested", "question": "Q?"},
        pending_decision_points=[],
        h_plane_payload={},
    )
    assert result["needs_popup"] is True
    assert result["popup_kind"] == "operator_checkpoint"
    assert result["priority"] == 2


def test_detect_popup_trigger__decision_point():
    result = detect_popup_trigger(
        topic_slug="t1",
        promotion_gate={},
        operator_checkpoint={},
        pending_decision_points=[{"decision_id": "d1", "question": "Q?"}],
        h_plane_payload={},
    )
    assert result["needs_popup"] is True
    assert result["popup_kind"] == "decision_point"
    assert result["priority"] == 3


def test_detect_popup_trigger__h_plane_steering():
    result = detect_popup_trigger(
        topic_slug="t1",
        promotion_gate={},
        operator_checkpoint={},
        pending_decision_points=[],
        h_plane_payload={"steering": {"status": "active_redirect"}},
    )
    assert result["needs_popup"] is True
    assert result["popup_kind"] == "h_plane_steering"
    assert result["priority"] == 4


def test_detect_popup_trigger__none():
    result = detect_popup_trigger(
        topic_slug="t1",
        promotion_gate={},
        operator_checkpoint={},
        pending_decision_points=[],
        h_plane_payload={},
    )
    assert result["needs_popup"] is False
    assert result["popup_kind"] == "none"


def test_build_popup_payload__promotion_gate():
    trigger = detect_popup_trigger(
        topic_slug="t1",
        promotion_gate={"status": "pending_human_approval", "candidate_id": "c1", "candidate_type": "theorem"},
        operator_checkpoint={},
        pending_decision_points=[],
        h_plane_payload={},
    )
    popup = build_popup_payload(
        trigger=trigger,
        promotion_gate={"status": "pending_human_approval", "candidate_id": "c1", "candidate_type": "theorem", "title": "T1"},
        operator_checkpoint={},
        pending_decision_points=[],
        h_plane_payload={},
    )
    assert popup["popup_kind"] == "promotion_gate"
    assert popup["title"] == "🔷 Promotion Review Gate"
    choices = popup["choices"]
    assert len(choices) >= 2
    assert choices[0]["key"] == "approve"
    assert choices[1]["key"] == "reject"


def test_build_popup_payload__operator_checkpoint_with_options():
    trigger = detect_popup_trigger(
        topic_slug="t1",
        promotion_gate={},
        operator_checkpoint={"status": "requested", "question": "Q?", "options": [{"key": "a", "label": "A"}, {"key": "b", "label": "B"}]},
        pending_decision_points=[],
        h_plane_payload={},
    )
    popup = build_popup_payload(
        trigger=trigger,
        promotion_gate={},
        operator_checkpoint={"status": "requested", "question": "Q?", "options": [{"key": "a", "label": "A"}, {"key": "b", "label": "B"}]},
        pending_decision_points=[],
        h_plane_payload={},
    )
    assert popup["popup_kind"] == "operator_checkpoint"
    choices = popup["choices"]
    assert any(c["key"] == "a" for c in choices)
    assert any(c["key"] == "b" for c in choices)


def test_build_popup_payload__decision_point():
    trigger = detect_popup_trigger(
        topic_slug="t1",
        promotion_gate={},
        operator_checkpoint={},
        pending_decision_points=[{"decision_id": "d1", "question": "Q?", "options": [{"key": "x", "label": "X"}]}],
        h_plane_payload={},
    )
    popup = build_popup_payload(
        trigger=trigger,
        promotion_gate={},
        operator_checkpoint={},
        pending_decision_points=[{"decision_id": "d1", "question": "Q?", "options": [{"key": "x", "label": "X"}]}],
        h_plane_payload={},
    )
    assert popup["popup_kind"] == "decision_point"
    assert any(c["key"] == "x" for c in popup["choices"])


def test_render_popup_markdown__promotion_gate():
    popup = build_popup_payload(
        trigger=detect_popup_trigger(
            topic_slug="t1",
            promotion_gate={"status": "pending_human_approval", "candidate_id": "c1", "candidate_type": "theorem"},
            operator_checkpoint={},
            pending_decision_points=[],
            h_plane_payload={},
        ),
        promotion_gate={"status": "pending_human_approval", "candidate_id": "c1", "candidate_type": "theorem", "title": "T1"},
        operator_checkpoint={},
        pending_decision_points=[],
        h_plane_payload={},
    )
    md = render_popup_markdown(popup)
    assert "╔" in md
    assert "🔷 Promotion Review Gate" in md
    assert "[1]" in md
    assert "[2]" in md


def test_render_popup_markdown__none():
    popup = build_popup_payload(
        trigger=detect_popup_trigger(topic_slug="t1", promotion_gate={}, operator_checkpoint={}, pending_decision_points=[], h_plane_payload={}),
        promotion_gate={},
        operator_checkpoint={},
        pending_decision_points=[],
        h_plane_payload={},
    )
    md = render_popup_markdown(popup)
    assert "AITP" in md
    assert "╔" not in md


def test_resolve_popup_choice__approve_promotion():
    svc = MockService()
    popup = build_popup_payload(
        trigger=detect_popup_trigger(
            topic_slug="t1",
            promotion_gate={"status": "pending_human_approval", "candidate_id": "c1"},
            operator_checkpoint={},
            pending_decision_points=[],
            h_plane_payload={},
        ),
        promotion_gate={"status": "pending_human_approval", "candidate_id": "c1"},
        operator_checkpoint={},
        pending_decision_points=[],
        h_plane_payload={},
    )
    result = resolve_popup_choice(svc, popup=popup, choice_index=1, comment="Looks good")
    assert result["status"] == "approved"
    assert svc.calls[0]["method"] == "approve_promotion"
    assert svc.calls[0]["kwargs"]["notes"] == "Looks good"


def test_resolve_popup_choice__reject_promotion():
    svc = MockService()
    popup = build_popup_payload(
        trigger=detect_popup_trigger(
            topic_slug="t1",
            promotion_gate={"status": "pending_human_approval", "candidate_id": "c1"},
            operator_checkpoint={},
            pending_decision_points=[],
            h_plane_payload={},
        ),
        promotion_gate={"status": "pending_human_approval", "candidate_id": "c1"},
        operator_checkpoint={},
        pending_decision_points=[],
        h_plane_payload={},
    )
    result = resolve_popup_choice(svc, popup=popup, choice_index=2)
    assert result["status"] == "rejected"
    assert svc.calls[0]["method"] == "reject_promotion"


def test_resolve_popup_choice__inspect():
    svc = MockService()
    popup = build_popup_payload(
        trigger=detect_popup_trigger(
            topic_slug="t1",
            promotion_gate={"status": "pending_human_approval", "candidate_id": "c1", "gate_note_path": "/tmp/gate.md"},
            operator_checkpoint={},
            pending_decision_points=[],
            h_plane_payload={},
        ),
        promotion_gate={"status": "pending_human_approval", "candidate_id": "c1", "gate_note_path": "/tmp/gate.md"},
        operator_checkpoint={},
        pending_decision_points=[],
        h_plane_payload={},
    )
    result = resolve_popup_choice(svc, popup=popup, choice_index=3)
    assert result["resolved"] is False
    assert result["action"] == "inspect"


def test_resolve_popup_choice__invalid_index():
    svc = MockService()
    popup = build_popup_payload(
        trigger=detect_popup_trigger(topic_slug="t1", promotion_gate={}, operator_checkpoint={}, pending_decision_points=[], h_plane_payload={}),
        promotion_gate={},
        operator_checkpoint={},
        pending_decision_points=[],
        h_plane_payload={},
    )
    with pytest.raises(ValueError):
        resolve_popup_choice(svc, popup=popup, choice_index=99)
