"""Regression tests for deterministic, non-executing Pi artifact replay."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from fertig.pi_artifact_replay import (
    PiArtifactReplayer,
    PiArtifactReplayError,
    compare_replay_to_artifact,
    replay_pi_trace,
)


ROOT = Path(__file__).resolve().parent.parent
REAL_RUN = ROOT / "data" / "live_experience" / "deepseek_flash_teacher_01"
VIRTUAL_ROOT = "/private/tmp/fertig-teacher-moonshot.p71h8M"


def _call(call_id, tool, args, *, error=False):
    return [
        {
            "type": "tool_execution_start",
            "toolCallId": call_id,
            "toolName": tool,
            "args": args,
        },
        {
            "type": "tool_execution_end",
            "toolCallId": call_id,
            "toolName": tool,
            "result": {"content": []},
            "isError": error,
        },
    ]


def test_write_and_multiblock_edit_replay_transactionally() -> None:
    events = _call("w", "write", {"path": "src/a.txt", "content": "one\ntwo\n"})
    events += _call(
        "e",
        "edit",
        {
            "path": "/virtual/src/a.txt",
            "edits": [
                {"oldText": "one", "newText": "ONE"},
                {"oldText": "two", "newText": "TWO"},
            ],
        },
    )

    report = PiArtifactReplayer("/virtual").replay(events)

    assert (report.applied, report.skipped, report.failed) == (2, 0, 0)
    assert report.files[0].path == "src/a.txt"
    assert report.files[0].content == "ONE\nTWO\n"
    assert len(report.files[0].sha256) == 64


def test_failed_and_invalid_edits_do_not_partially_mutate() -> None:
    events = _call("w", "write", {"path": "a.txt", "content": "alpha beta"})
    events += _call(
        "pi-failed",
        "edit",
        {
            "path": "a.txt",
            "edits": [{"oldText": "alpha", "newText": "lost"}],
        },
        error=True,
    )
    events += _call(
        "transaction-failed",
        "edit",
        {
            "path": "a.txt",
            "edits": [
                {"oldText": "alpha", "newText": "changed"},
                {"oldText": "missing", "newText": "never"},
            ],
        },
    )

    report = PiArtifactReplayer("/virtual").replay(events)

    assert (report.applied, report.failed) == (1, 2)
    assert report.files[0].content == "alpha beta"


@pytest.mark.parametrize(
    "path",
    ["../escape", "safe/../../escape", "/outside/file", "safe\\..\\escape"],
)
def test_rejects_paths_outside_declared_virtual_root(path: str) -> None:
    report = PiArtifactReplayer("/virtual/root").replay(
        _call("w", "write", {"path": path, "content": "payload"})
    )

    assert report.applied == 0
    assert report.failed == 1
    assert report.files == ()
    assert "path" in report.issues[0].reason


def test_unsupported_and_unfinished_tools_are_never_applied() -> None:
    events = _call("bash", "bash", {"command": "touch a.txt"})
    events.append(
        {
            "type": "tool_execution_start",
            "toolCallId": "unfinished",
            "toolName": "write",
            "args": {"path": "a.txt", "content": "no"},
        }
    )

    report = PiArtifactReplayer("/virtual").replay(events)

    assert (report.applied, report.skipped, report.failed) == (0, 2, 0)
    assert report.files == ()


def test_trace_reader_rejects_non_object_json(tmp_path: Path) -> None:
    trace = tmp_path / "bad.jsonl"
    trace.write_text(json.dumps(["not", "an", "event"]) + "\n", encoding="utf-8")

    with pytest.raises(PiArtifactReplayError, match="must be an object"):
        replay_pi_trace(trace, virtual_root="/virtual")


@pytest.mark.skipif(not REAL_RUN.is_dir(), reason="archived live Pi run unavailable")
def test_real_deepseek_trace_replays_archived_authored_text_exactly() -> None:
    report = replay_pi_trace(REAL_RUN / "raw.jsonl", virtual_root=VIRTUAL_ROOT)

    assert (report.applied, report.skipped, report.failed) == (17, 23, 1)
    assert tuple(file.path for file in report.files) == (
        "LAB_REPORT.md",
        "RUN.md",
        "core.py",
        "run_experiments.py",
        "test_solomonoff.py",
    )

    comparison = compare_replay_to_artifact(report, REAL_RUN / "artifact")
    assert comparison.exact_matches == tuple(file.path for file in report.files)
    assert comparison.mismatches == ()
    assert comparison.extra_in_replay == ()
    assert comparison.missing_from_replay == ("results/results.json",)
    assert comparison.ignored_binary == (
        "__pycache__/core.cpython-313.pyc",
        "__pycache__/test_solomonoff.cpython-313.pyc",
    )
    assert comparison.all_replayed_files_match
