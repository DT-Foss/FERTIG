"""Tests for the literal process projection built from Pi traces."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
import json
from pathlib import Path
from typing import Any

import pytest

from fertig.pi_trace import read_pi_trace
from fertig.process_distillation import (
    ProcessDistillationError,
    TrainingArm,
    build_process_corpus,
    iter_training_records,
    read_training_jsonl,
    training_jsonl,
    write_training_jsonl,
)


def _line(value: dict[str, Any]) -> bytes:
    return (json.dumps(value, separators=(",", ":")) + "\n").encode()


def _fixture() -> bytes:
    events = [
        {
            "type": "session",
            "version": 3,
            "id": "observed-session",
            "timestamp": "1970-01-01T00:00:01.000Z",
            "cwd": "/tmp/observed",
        },
        {
            "type": "message_end",
            "message": {
                "role": "user",
                "content": [{"type": "text", "text": "build"}],
                "timestamp": 1000,
            },
        },
        {
            "type": "message_end",
            "message": {
                "role": "assistant",
                "provider": "teacher-provider",
                "model": "teacher-model",
                "timestamp": 2000,
                "stopReason": "toolUse",
                "content": [
                    {"type": "thinking", "thinking": "aaaa"},
                    {"type": "text", "text": "trying"},
                    {
                        "type": "toolCall",
                        "id": "bad",
                        "name": "bash",
                        "arguments": {"command": "false"},
                    },
                    {
                        "type": "toolCall",
                        "id": "parallel-ok",
                        "name": "read",
                        "arguments": {"path": "x"},
                    },
                ],
            },
        },
        {
            "type": "tool_execution_start",
            "toolCallId": "bad",
            "toolName": "bash",
            "args": {"command": "false"},
        },
        {
            "type": "tool_execution_start",
            "toolCallId": "parallel-ok",
            "toolName": "read",
            "args": {"path": "x"},
        },
        {
            "type": "tool_execution_end",
            "toolCallId": "parallel-ok",
            "toolName": "read",
            "result": {"content": [{"type": "text", "text": "x"}]},
            "isError": False,
        },
        {
            "type": "tool_execution_end",
            "toolCallId": "bad",
            "toolName": "bash",
            "result": {"content": [{"type": "text", "text": "exit 1"}]},
            "isError": True,
        },
        {
            "type": "message_end",
            "message": {
                "role": "toolResult",
                "toolCallId": "parallel-ok",
                "toolName": "read",
                "content": [{"type": "text", "text": "x"}],
                "isError": False,
                "timestamp": 2100,
            },
        },
        {
            "type": "message_end",
            "message": {
                "role": "toolResult",
                "toolCallId": "bad",
                "toolName": "bash",
                "content": [{"type": "text", "text": "exit 1"}],
                "isError": True,
                "timestamp": 2200,
            },
        },
        {
            "type": "message_end",
            "message": {
                "role": "assistant",
                "provider": "teacher-provider",
                "model": "teacher-model",
                "timestamp": 3000,
                "stopReason": "toolUse",
                "content": [
                    {"type": "thinking", "thinking": "bb"},
                    {
                        "type": "toolCall",
                        "id": "recovered",
                        "name": "edit",
                        "arguments": {"path": "x", "replacement": "fixed"},
                    },
                ],
            },
        },
        {
            "type": "tool_execution_start",
            "toolCallId": "recovered",
            "toolName": "edit",
            "args": {"path": "x", "replacement": "fixed"},
        },
        {
            "type": "tool_execution_end",
            "toolCallId": "recovered",
            "toolName": "edit",
            "result": {"content": [{"type": "text", "text": "done"}]},
            "isError": False,
        },
        {
            "type": "message_end",
            "message": {
                "role": "toolResult",
                "toolCallId": "recovered",
                "toolName": "edit",
                "content": [{"type": "text", "text": "done"}],
                "isError": False,
                "timestamp": 3100,
            },
        },
        {
            "type": "message_end",
            "message": {
                "role": "assistant",
                "provider": "teacher-provider",
                "model": "teacher-model",
                "timestamp": 4000,
                "stopReason": "stop",
                "content": [
                    {"type": "thinking", "thinking": "c"},
                    {"type": "text", "text": "finished"},
                ],
            },
        },
    ]
    return b"".join(_line(event) for event in events)


def _nested_keys(value: Any) -> set[str]:
    if isinstance(value, dict):
        return set(value).union(*(_nested_keys(item) for item in value.values()))
    if isinstance(value, list):
        return set().union(*(_nested_keys(item) for item in value))
    return set()


def test_builds_immutable_turns_in_teacher_call_order_with_literal_results(
    tmp_path: Path,
) -> None:
    path = tmp_path / "observed.jsonl"
    path.write_bytes(_fixture())

    corpus = build_process_corpus(path)

    assert corpus.session_id == "observed-session"
    assert corpus.provider == "teacher-provider"
    assert corpus.model == "teacher-model"
    assert len(corpus.inputs) == 1
    assert [turn.index for turn in corpus.turns] == [0, 1, 2]
    first = corpus.turns[0]
    # Runtime completion was parallel-ok then bad.  The corpus correctly keeps
    # the teacher's requested source order instead.
    assert [tool.tool_call_id for tool in first.tools] == ["bad", "parallel-ok"]
    assert first.thinking == ("aaaa",)
    assert first.text == ("trying",)
    assert first.tools[0].requested_arguments == {"command": "false"}
    assert first.tools[0].execution_arguments == {"command": "false"}
    assert first.tools[0].result == {"content": ({"type": "text", "text": "exit 1"},)}
    assert first.tools[0].is_error is True
    assert first.immediate_tool_errors == (first.tools[0],)
    assert first.tools[0].result_message_is_error is True

    with pytest.raises(TypeError):
        first.content[0]["thinking"] = "mutated"  # type: ignore[index]
    with pytest.raises(FrozenInstanceError):
        first.index = 99  # type: ignore[misc]


def test_recovery_and_terminal_evidence_are_literal_and_do_not_claim_causality(
    tmp_path: Path,
) -> None:
    path = tmp_path / "observed.jsonl"
    path.write_bytes(_fixture())
    corpus = build_process_corpus(path)

    assert len(corpus.recoveries) == 1
    recovery = corpus.recoveries[0]
    assert recovery.error_turn_index == 0
    assert recovery.recovery_turn_index == 1
    assert recovery.provenance == "literal_error_then_later_success"
    assert recovery.observationally_comparable is False
    assert recovery.causal_claim is False
    assert recovery.to_dict(corpus.turns)["error_tool_call_id"] == "bad"
    assert recovery.to_dict(corpus.turns)["recovery_tool_call_id"] == "recovered"

    assert len(corpus.terminal_evidence) == 1
    evidence = corpus.terminal_evidence[0]
    assert evidence.terminal_turn_index == 2
    assert [tool.tool_call_id for tool in evidence.tools(corpus.turns)] == ["recovered"]
    assert evidence.semantic_verification_claim is False

    stats = corpus.stats
    assert stats.assistant_turns == 3
    assert stats.paired_tools == 3
    assert stats.tool_errors == 1
    assert stats.recovery_spans == 1
    assert stats.thinking_chars == 7
    assert stats.top_two_thinking_chars == 6
    assert stats.thinking_burstiness == pytest.approx(6 / 7)


def test_jsonl_arms_are_deterministic_roundtrip_safe_and_have_honest_pairs(
    tmp_path: Path,
) -> None:
    trace_path = tmp_path / "observed.jsonl"
    trace_path.write_bytes(_fixture())
    corpus = build_process_corpus(read_pi_trace(trace_path))

    encoded = training_jsonl(corpus)
    assert training_jsonl(build_process_corpus(trace_path)) == encoded
    records = tuple(json.loads(line) for line in encoded.splitlines())
    assert [record["arm"] for record in records] == [
        "answer_only",
        "raw_cot",
        "tool_sequence",
        "process_pair",
    ]
    assert "thinking" not in json.dumps(records[0]["target"])
    assert len(records[2]["target"]["tools"]) == 3
    pair = records[3]
    assert pair["preference_claim"] is False
    assert pair["provenance"]["observationally_comparable"] is False
    assert pair["negative"]["tools"][0]["is_error"] is True
    assert pair["positive"]["tools"][0]["is_error"] is False

    forbidden = {"recipe", "operator", "operator_label"}
    assert _nested_keys(list(records)).isdisjoint(forbidden)

    destination = write_training_jsonl(corpus, tmp_path / "out" / "training.jsonl")
    assert destination.read_text(encoding="utf-8") == encoded
    assert read_training_jsonl(destination) == records

    answer = list(
        iter_training_records(corpus, arms=[TrainingArm.ANSWER_ONLY, "answer_only"])
    )
    assert len(answer) == 1
    with pytest.raises(ValueError, match="unknown training arm"):
        list(iter_training_records(corpus, arms=["imaginary"]))


def test_reader_rejects_non_corpus_jsonl(tmp_path: Path) -> None:
    path = tmp_path / "wrong.jsonl"
    path.write_text('{"schema":"other","arm":"answer_only"}\n')

    with pytest.raises(ProcessDistillationError, match="unsupported schema"):
        read_training_jsonl(path)


def test_real_deepseek_trace_counts_and_thinking_burstiness() -> None:
    path = (
        Path(__file__).parents[1]
        / "data/live_experience/deepseek_flash_teacher_01/raw.jsonl"
    )
    if not path.exists():
        pytest.skip("live observation archive is not present")

    corpus = build_process_corpus(path)
    stats = corpus.stats

    assert stats.assistant_turns == 37
    assert stats.paired_tools == 41
    assert stats.unpaired_tools == 0
    assert stats.tool_errors == 3
    assert stats.recovery_spans == 3
    assert stats.unresolved_tool_errors == 0
    assert stats.observed_terminal_turns == 1
    assert stats.terminal_evidence_tools == 2
    assert stats.thinking_chars == 197_097
    assert stats.top_two_thinking_chars == 146_432
    assert stats.top_two_thinking_share == pytest.approx(0.743, abs=0.001)
    assert stats.turns_with_thinking == 25

    assert [span.error_turn_index for span in corpus.recoveries] == [2, 7, 17]
    assert [span.recovery_turn_index for span in corpus.recoveries] == [3, 8, 18]
    assert all(not span.causal_claim for span in corpus.recoveries)
    assert len(corpus.terminal_evidence) == 1
    assert [
        tool.tool_call_id for tool in corpus.terminal_evidence[0].tools(corpus.turns)
    ] == [
        "call_00_ossUpqzh5ID40FAO8R4w9177",
        "call_01_rDC8rbpqXo2iQvZltnHX9036",
    ]

    records = list(iter_training_records(corpus))
    assert [record["arm"] for record in records] == [
        "answer_only",
        "raw_cot",
        "tool_sequence",
        "process_pair",
        "process_pair",
        "process_pair",
    ]
    assert len(records[2]["target"]["tools"]) == 41
    assert all(record["preference_claim"] is False for record in records[3:])
