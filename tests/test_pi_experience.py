"""Tests for the deliberately non-semantic Pi experience projection."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from fertig.agent_experience import AgentExperienceStore
from fertig.pi_experience import (
    PiExperienceError,
    PiExperienceSink,
    ingest_pi_trace,
)
from fertig.pi_trace import RawPiEvent


def _events() -> list[dict[str, object]]:
    return [
        {"type": "agent_start"},
        {
            "type": "session",
            "version": 3,
            "id": "pi-session-1",
            "timestamp": "2026-08-13T12:00:00.000Z",
            "cwd": "/tmp/teacher",
        },
        {
            "type": "message_end",
            "message": {
                "role": "user",
                "content": [{"type": "text", "text": "do it"}],
                "timestamp": 1_765_627_200_001,
            },
        },
        {
            "type": "message_end",
            "message": {
                "role": "assistant",
                "provider": "deepseek",
                "model": "deepseek-v4-flash",
                "content": [
                    {
                        "type": "toolCall",
                        "id": "c1",
                        "name": "bash",
                        "arguments": {"command": "pwd"},
                    }
                ],
                "timestamp": 1_765_627_200_002,
            },
        },
        {
            "type": "tool_execution_start",
            "toolCallId": "c1",
            "toolName": "bash",
            "args": {"command": "pwd"},
        },
        {"type": "tool_execution_update", "toolCallId": "c1", "partialResult": {}},
        {
            "type": "tool_execution_end",
            "toolCallId": "c1",
            "toolName": "bash",
            "result": {"content": [{"type": "text", "text": "/tmp\n"}]},
            "isError": False,
        },
        {
            "type": "message_end",
            "message": {
                "role": "toolResult",
                "toolCallId": "c1",
                "content": [{"type": "text", "text": "/tmp\n"}],
                "isError": False,
            },
        },
        {"type": "agent_end", "messages": [], "willRetry": False},
        {"type": "agent_settled"},
    ]


def _write_trace(path: Path) -> bytes:
    raw = b"".join(
        (json.dumps(event, separators=(",", ":")) + "\n").encode()
        for event in _events()
    )
    path.write_bytes(raw)
    return raw


def test_completed_import_maps_only_explicit_boundaries_and_keeps_raw_blob(
    tmp_path: Path,
) -> None:
    trace_path = tmp_path / "raw.jsonl"
    raw = _write_trace(trace_path)
    store = AgentExperienceStore(tmp_path / "experience")

    result = ingest_pi_trace(trace_path, store, max_inline_chars=1)

    assert result.session_id == "pi-session-1"
    assert result.raw_event_count == 10
    assert result.mapped_event_count == 7
    assert result.mapped_kinds == {
        "assistant_message": 1,
        "session_end": 1,
        "session_start": 1,
        "terminal": 1,
        "tool_call": 1,
        "tool_result": 1,
        "user_message": 1,
    }
    assert result.ignored_types == {
        "agent_start": 1,
        "message_end": 1,
        "tool_execution_update": 1,
    }
    assert result.capture_blob is not None
    assert store.read_blob(result.capture_blob) == raw
    stored = store.events(result.session_id)
    assert [event.kind.value for event in stored] == [
        "session_start",
        "user_message",
        "assistant_message",
        "tool_call",
        "tool_result",
        "terminal",
        "session_end",
    ]
    assert stored[2].model_id == "deepseek:deepseek-v4-flash"
    assert all(event.to_dict()["payload"].get("goal") is None for event in stored)


def test_reingest_refuses_by_default_and_exact_mode_is_idempotent(
    tmp_path: Path,
) -> None:
    path = tmp_path / "raw.jsonl"
    _write_trace(path)
    store = AgentExperienceStore(tmp_path / "experience")
    first = ingest_pi_trace(path, store)

    with pytest.raises(PiExperienceError, match="already exists"):
        ingest_pi_trace(path, store)
    second = ingest_pi_trace(path, store, reject_existing=False)

    assert second.already_present
    assert second.trace_sha256 == first.trace_sha256
    assert len(store.events("pi-session-1")) == 7


def test_live_sink_buffers_pre_session_events_and_is_callback_compatible(
    tmp_path: Path,
) -> None:
    store = AgentExperienceStore(tmp_path / "experience")
    sink = PiExperienceSink(store, max_inline_chars=16)
    raws: list[str] = []
    for line_number, parsed in enumerate(_events(), 1):
        raw = json.dumps(parsed, separators=(",", ":")) + "\n"
        raws.append(raw)
        sink(RawPiEvent(line_number, raw, parsed))

    capture = tmp_path / "capture.jsonl"
    capture.write_text("".join(raws), encoding="utf-8")
    result = sink.finalize(raw_capture_path=capture)

    assert result.session_id == "pi-session-1"
    assert result.raw_event_count == 10
    assert result.mapped_event_count == 7
    assert store.read_blob(result.capture_blob) == capture.read_bytes()
    assert sink.finalize() is result


def test_real_archived_trace_smoke(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    path = root / "data/live_experience/deepseek_flash_teacher_01/raw.jsonl"
    if not path.exists():
        pytest.skip("archived live Pi trace is not present")
    result = ingest_pi_trace(
        path,
        AgentExperienceStore(tmp_path / "real"),
        max_inline_chars=1,
    )

    assert result.raw_event_count == 92_680
    assert result.mapped_event_count == 123
    assert result.mapped_kinds == {
        "assistant_message": 37,
        "session_end": 1,
        "session_start": 1,
        "terminal": 1,
        "tool_call": 41,
        "tool_result": 41,
        "user_message": 1,
    }
