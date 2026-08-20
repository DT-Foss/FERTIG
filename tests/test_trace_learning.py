from __future__ import annotations

import json
from pathlib import Path

import pytest

from fertig.pi_trace import read_pi_trace
from fertig.trace_learning import (
    ObservableStep,
    TransitionFingerprint,
    analyze_trace,
    canonicalize_trace,
    decision_steps,
    evaluate_holdout,
    recovery_motifs,
)


def _message(role: str, **fields: object) -> dict[str, object]:
    return {"type": "message_end", "message": {"role": role, **fields}}


def test_canonicalize_completed_pi_events_without_duplicate_tool_messages() -> None:
    records = [
        _message("user", content=[{"type": "text", "text": "task"}]),
        _message(
            "assistant",
            content=[
                {
                    "type": "toolCall",
                    "id": "call-1",
                    "name": "bash",
                    "arguments": {"command": "false"},
                }
            ],
            stopReason="toolUse",
        ),
        {
            "type": "tool_execution_start",
            "toolCallId": "call-1",
            "toolName": "bash",
            "args": {"command": "false"},
        },
        {
            "type": "tool_execution_end",
            "toolCallId": "call-1",
            "toolName": "bash",
            "result": {"content": []},
            "isError": True,
        },
        _message(
            "toolResult",
            toolCallId="call-1",
            toolName="bash",
            isError=True,
            content=[{"type": "text", "text": "failed"}],
        ),
        _message(
            "assistant",
            content=[{"type": "text", "text": "done"}],
            stopReason="stop",
        ),
    ]

    steps = canonicalize_trace(records)

    assert [step.symbol for step in steps] == [
        "context:user:message",
        "decision:agent:tool/bash",
        "outcome:tool:tool/bash:error",
        "decision:agent:finish/stop",
    ]
    assert [step.symbol for step in decision_steps(steps)] == [
        "decision:agent:tool/bash",
        "decision:agent:finish/stop",
    ]


def test_message_only_host_falls_back_to_completed_tool_blocks() -> None:
    records = [
        _message(
            "assistant",
            content=[{"type": "toolCall", "id": "x", "name": "read"}],
            stopReason="toolUse",
        ),
        _message(
            "toolResult",
            toolCallId="x",
            toolName="read",
            isError=False,
            content=[],
        ),
        _message("assistant", content=[], stopReason="stop"),
    ]

    assert [step.symbol for step in canonicalize_trace(records)] == [
        "decision:agent:tool/read",
        "outcome:tool:tool/read:ok",
        "decision:agent:finish/stop",
    ]


def test_variable_order_model_roundtrips_deterministically() -> None:
    sequence = ("a", "b", "a", "b", "a", "b", "c")
    model = TransitionFingerprint.fit(sequence, max_order=3, min_count=1)

    encoded = model.to_bytes()
    restored = TransitionFingerprint.from_bytes(encoded)

    assert restored.to_bytes() == encoded
    assert restored.distribution(("a",)) == model.distribution(("a",))
    assert restored.score(("b", "a"), initial_context=("a",)) == model.score(
        ("b", "a"), initial_context=("a",)
    )
    assert len(encoded) < len(json.dumps(sequence).encode("utf-8")) * 20
    with pytest.raises(ValueError, match="invalid or too large"):
        TransitionFingerprint.from_bytes(encoded + b"junk")


def test_chronological_holdout_learns_order_and_is_deterministic() -> None:
    sequence = tuple("abcd"[index % 4] for index in range(80))

    first = evaluate_holdout(
        sequence, holdout_fraction=0.25, max_order=2, min_count=1, seed=7
    )
    second = evaluate_holdout(
        sequence, holdout_fraction=0.25, max_order=2, min_count=1, seed=7
    )

    assert first == second
    assert first.split_index == 60
    assert first.test_steps == 20
    assert first.ordered.log_loss_bits < first.unigram.log_loss_bits
    assert first.ordered.log_loss_bits < first.shuffled.log_loss_bits
    assert first.ordered_wins is True


def test_decision_view_cannot_learn_call_result_alternation() -> None:
    steps = []
    for index in range(12):
        steps.extend(
            [
                ObservableStep(
                    len(steps), "decision", "agent", f"tool/{'a' if index % 2 else 'b'}"
                ),
                ObservableStep(
                    len(steps) + 1,
                    "outcome",
                    "tool",
                    f"tool/{'a' if index % 2 else 'b'}",
                    "ok",
                ),
            ]
        )

    decisions = decision_steps(steps)

    assert len(decisions) == 12
    assert all(step.kind == "decision" for step in decisions)
    assert all("outcome" not in step.symbol for step in decisions)


def test_recovery_motif_is_literal_and_correlation_grounded() -> None:
    steps = [
        ObservableStep(0, "decision", "agent", "tool/bash", correlation_id="bad"),
        ObservableStep(1, "outcome", "tool", "tool/bash", "error", "bad"),
        ObservableStep(2, "decision", "agent", "tool/edit", correlation_id="fix"),
        ObservableStep(3, "outcome", "tool", "tool/edit", "ok", "other"),
        ObservableStep(4, "outcome", "tool", "tool/edit", "ok", "fix"),
    ]

    motif = recovery_motifs(steps)[0]

    assert motif.error_index == 1
    assert motif.decision_action == "tool/edit"
    assert motif.result_index == 4
    assert motif.subsequent_success_observed is True


def test_recovery_without_id_does_not_claim_an_unrelated_tool_result() -> None:
    steps = [
        ObservableStep(0, "outcome", "tool", "tool/bash", "error", "bad"),
        ObservableStep(1, "decision", "agent", "tool/edit"),
        ObservableStep(2, "outcome", "tool", "tool/bash", "ok", "other"),
    ]

    motif = recovery_motifs(steps)[0]

    assert motif.decision_action == "tool/edit"
    assert motif.result_index is None
    assert motif.subsequent_success_observed is False


def test_invalid_models_and_too_short_holdout_fail_closed() -> None:
    with pytest.raises(ValueError, match="empty"):
        TransitionFingerprint.fit(())
    with pytest.raises(ValueError, match="at least four"):
        evaluate_holdout(("a", "b", "c"))
    with pytest.raises(ValueError, match="not a FERTIG"):
        TransitionFingerprint.from_bytes(b"not-a-model")


def test_real_deepseek_trace_smoke_and_honest_dual_report() -> None:
    path = (
        Path(__file__).parents[1]
        / "data/live_experience/deepseek_flash_teacher_01/raw.jsonl"
    )
    if not path.exists():
        pytest.skip("live observation archive is not present")
    with path.open("r", encoding="utf-8") as handle:
        records = [json.loads(line) for line in handle if line.strip()]

    report = analyze_trace(records)
    compact_report = analyze_trace(read_pi_trace(path).completed_trace)

    assert report.observable_steps == 84
    assert compact_report == report
    assert report.decision_steps == 42
    assert len(report.recovery_motifs) == 3
    assert all(motif.subsequent_success_observed for motif in report.recovery_motifs)
    assert report.full_stream.ordered_wins is True
    # This is the important negative result: protocol order is predictable,
    # but this one session does not support a decision-strategy claim.
    assert report.decision_stream.ordered_wins is False
    assert report.decision_stream.gain_vs_unigram_bits < 0
    assert report.fingerprint_bytes < 1024
    decisions = decision_steps(canonicalize_trace(records))
    train = decisions[: report.decision_stream.split_index]
    expected = TransitionFingerprint.fit(train, max_order=4)
    assert report.fingerprint_bytes == len(expected.to_bytes()) == 491
    assert all(
        item.index >= report.decision_stream.split_index
        for item in report.surprising_decisions
    )
