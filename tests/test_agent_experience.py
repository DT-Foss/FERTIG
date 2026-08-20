"""Tests for the provider-neutral append-only agent experience stream."""

from __future__ import annotations

from dataclasses import replace
import json

import pytest

from fertig.agent_experience import (
    AgentExperience,
    AgentExperienceStore,
    EventKind,
    ExperienceCorruptionError,
    ExperienceError,
    Outcome,
    OutcomeStatus,
    StateRef,
)


def test_records_interleaved_sessions_with_independent_hash_chains(tmp_path) -> None:
    store = AgentExperienceStore(tmp_path / "experience")
    a0 = store.append(
        session_id="codex:one",
        actor="user",
        kind=EventKind.GOAL,
        payload={"text": "repair parser"},
        timestamp_ns=10,
        monotonic_ns=1,
    )
    b0 = store.append(
        session_id="claude:two",
        actor="user",
        kind=EventKind.GOAL,
        payload={"text": "find invariant"},
        timestamp_ns=11,
        monotonic_ns=2,
    )
    a1 = store.append(
        session_id="codex:one",
        actor="agent",
        kind=EventKind.TOOL_CALL,
        payload={"tool": "rg", "args": ["parser"]},
        parent_event_id=a0.event_id,
        model_id="frontier-a",
        timestamp_ns=12,
        monotonic_ns=3,
    )

    assert [event.sequence for event in store.events("codex:one")] == [0, 1]
    assert a1.previous_hash == a0.event_hash
    assert b0.previous_hash is None
    assert store.sessions() == ("claude:two", "codex:one")
    assert AgentExperience.from_json(a1.to_json()) == a1


def test_blob_store_is_content_addressed_deduplicated_and_verified(tmp_path) -> None:
    store = AgentExperienceStore(tmp_path)
    first = store.put_blob(
        "diff --git a/x b/x", media_type="text/x-diff", name="x.diff"
    )
    second = store.put_blob(b"diff --git a/x b/x", media_type="text/x-diff")

    assert first.digest == second.digest
    assert store.read_blob(first) == b"diff --git a/x b/x"
    assert len(tuple((tmp_path / "blobs" / "sha256").rglob(first.digest))) == 1

    blob_path = next((tmp_path / "blobs" / "sha256").rglob(first.digest))
    blob_path.write_bytes(b"tampered")
    with pytest.raises(ExperienceCorruptionError, match="failed verification"):
        store.read_blob(first)


def test_state_delta_outcome_and_summary_are_derived(tmp_path) -> None:
    store = AgentExperienceStore(tmp_path)
    evidence = store.put_blob("3 passed", media_type="text/plain")
    before = StateRef.from_payload({"git": "clean", "tests": 2}, label="before")
    after = StateRef.from_payload({"git": "modified", "tests": 3}, label="after")

    store.append(
        session_id="run-1",
        actor="agent",
        kind=EventKind.TEST_RESULT,
        payload={"command": "pytest", "exit_code": 0},
        before=before,
        after=after,
        outcome=Outcome(OutcomeStatus.SUCCESS, 1.0, "all tests passed", (evidence,)),
        timestamp_ns=20,
        monotonic_ns=20,
    )

    summary = store.summary("run-1")
    assert summary.event_count == 1
    assert summary.kinds == {"test_result": 1}
    assert summary.outcome_statuses == {"success": 1}
    assert summary.terminal_hash == store.events()[0].event_hash


def test_truncated_final_line_is_ignored_and_repaired_before_append(tmp_path) -> None:
    store = AgentExperienceStore(tmp_path)
    first = store.append(
        session_id="run",
        actor="user",
        kind="goal",
        payload={"goal": "one"},
        timestamp_ns=1,
        monotonic_ns=1,
    )
    with store.events_path.open("ab") as handle:
        handle.write(b'{"partial":')

    assert store.events() == (first,)
    second = store.append(
        session_id="run",
        actor="agent",
        kind="assistant_message",
        payload={"text": "working"},
        timestamp_ns=2,
        monotonic_ns=2,
    )

    assert second.sequence == 1
    assert len(store.events()) == 2
    assert store.events_path.read_bytes().endswith(b"\n")


def test_complete_corruption_or_broken_chain_is_rejected(tmp_path) -> None:
    store = AgentExperienceStore(tmp_path)
    event = store.append(
        session_id="run",
        actor="agent",
        kind="observation",
        payload={"value": 1},
        timestamp_ns=1,
        monotonic_ns=1,
    )
    payload = event.to_dict()
    payload["payload"] = {"value": 2}
    store.events_path.write_text(json.dumps(payload) + "\n", encoding="utf-8")

    with pytest.raises(ExperienceCorruptionError, match="event_hash"):
        store.events()


def test_event_validation_rejects_non_json_nonfinite_and_unknown_fields() -> None:
    with pytest.raises(ExperienceError, match="non-JSON"):
        AgentExperience.create(
            session_id="run",
            sequence=0,
            actor="agent",
            kind="goal",
            payload={"bad": object()},
            previous_hash=None,
        )
    with pytest.raises(ExperienceError, match="non-finite"):
        AgentExperience.create(
            session_id="run",
            sequence=0,
            actor="agent",
            kind="goal",
            payload={"bad": float("nan")},
            previous_hash=None,
        )

    event = AgentExperience.create(
        session_id="run",
        sequence=0,
        actor="agent",
        kind="goal",
        payload={},
        previous_hash=None,
        timestamp_ns=1,
        monotonic_ns=1,
    )
    raw = event.to_dict()
    raw["invented"] = True
    with pytest.raises(ExperienceError, match="unknown fields"):
        AgentExperience.from_dict(raw)


def test_parent_must_exist_in_same_session(tmp_path) -> None:
    store = AgentExperienceStore(tmp_path)
    other = store.append(
        session_id="other",
        actor="user",
        kind="goal",
        timestamp_ns=1,
        monotonic_ns=1,
    )

    with pytest.raises(ExperienceError, match="not in this session"):
        store.append(
            session_id="run",
            actor="agent",
            kind="tool_call",
            parent_event_id=other.event_id,
        )


def test_payload_is_detached_and_event_is_content_bound() -> None:
    mutable = {"nested": [1, 2]}
    event = AgentExperience.create(
        session_id="run",
        sequence=0,
        actor="agent",
        kind="goal",
        payload=mutable,
        previous_hash=None,
        timestamp_ns=1,
        monotonic_ns=1,
    )
    mutable["nested"].append(3)

    assert event.to_dict()["payload"] == {"nested": [1, 2]}
    with pytest.raises(ExperienceCorruptionError):
        replace(event, actor="different")
