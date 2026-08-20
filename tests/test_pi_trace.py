"""Tests against the Pi JSON schema observed in the archived live trace."""

from __future__ import annotations

import hashlib
import io
import json
import subprocess
from typing import Any

import pytest

from fertig.pi_trace import PiTraceError, RawPiEvent, read_pi_trace, run_pi_captured


def _json_line(value: dict[str, Any]) -> bytes:
    return (json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n").encode(
        "utf-8"
    )


def _observed_fixture() -> bytes:
    usage_a = {
        "input": 2,
        "output": 3,
        "cacheRead": 4,
        "cacheWrite": 0,
        "reasoning": 2,
        "totalTokens": 9,
        "cost": {
            "input": 0.1,
            "output": 0.2,
            "cacheRead": 0.01,
            "cacheWrite": 0,
            "total": 0.31,
        },
    }
    usage_b = {
        "input": 1,
        "output": 2,
        "cacheRead": 3,
        "cacheWrite": 0,
        "reasoning": 1,
        "totalTokens": 6,
        "cost": {
            "input": 0.05,
            "output": 0.1,
            "cacheRead": 0.01,
            "cacheWrite": 0,
            "total": 0.16,
        },
    }
    events = [
        {
            "type": "session",
            "version": 3,
            "id": "session-1",
            "timestamp": "1970-01-01T00:00:01.000Z",
            "cwd": "/tmp/pi-scratch",
        },
        {"type": "agent_start"},
        {
            "type": "message_start",
            "message": {
                "role": "user",
                "content": [{"type": "text", "text": "build it"}],
                "timestamp": 1000,
            },
        },
        {
            "type": "message_end",
            "message": {
                "role": "user",
                "content": [{"type": "text", "text": "build it"}],
                "timestamp": 1000,
            },
        },
        {
            "type": "message_end",
            "message": {
                "role": "assistant",
                "content": [
                    {
                        "type": "toolCall",
                        "id": "call-a",
                        "name": "bash",
                        "arguments": {"command": "pwd"},
                    },
                    {
                        "type": "toolCall",
                        "id": "call-b",
                        "name": "edit",
                        "arguments": {"path": "x.py"},
                    },
                ],
                "api": "openai-completions",
                "provider": "deepseek",
                "model": "deepseek-v4-flash",
                "usage": usage_a,
                "stopReason": "toolUse",
                "timestamp": 2000,
            },
        },
        {
            "type": "tool_execution_start",
            "toolCallId": "call-a",
            "toolName": "bash",
            "args": {"command": "pwd"},
        },
        {
            "type": "tool_execution_start",
            "toolCallId": "call-b",
            "toolName": "edit",
            "args": {"path": "x.py"},
        },
        {
            "type": "tool_execution_update",
            "toolCallId": "call-b",
            "toolName": "edit",
            "args": {"path": "x.py"},
            "partialResult": {"content": []},
        },
        {
            "type": "tool_execution_end",
            "toolCallId": "call-a",
            "toolName": "bash",
            "result": {"content": [{"type": "text", "text": "/tmp/pi-scratch\n"}]},
            "isError": False,
        },
        {
            "type": "tool_execution_end",
            "toolCallId": "call-b",
            "toolName": "edit",
            "result": {
                "content": [{"type": "text", "text": "grüß"}],
                "details": {"code": "not_found"},
            },
            "isError": True,
        },
        {
            "type": "message_end",
            "message": {
                "role": "toolResult",
                "toolCallId": "call-a",
                "toolName": "bash",
                "content": [{"type": "text", "text": "/tmp/pi-scratch\n"}],
                "isError": False,
                "timestamp": 3000,
            },
        },
        {
            "type": "message_end",
            "message": {
                "role": "toolResult",
                "toolCallId": "call-b",
                "toolName": "edit",
                "content": [{"type": "text", "text": "grüß"}],
                "isError": True,
                "timestamp": 3100,
            },
        },
        {
            "type": "message_end",
            "message": {
                "role": "assistant",
                "content": [{"type": "text", "text": "done"}],
                "api": "openai-completions",
                "provider": "deepseek",
                "model": "deepseek-v4-flash",
                "usage": usage_b,
                "stopReason": "stop",
                "timestamp": 4500,
            },
        },
        {"type": "agent_end", "messages": [], "willRetry": False},
        {"type": "agent_settled"},
    ]
    return b"".join(_json_line(event) for event in events)


def test_reader_is_lossless_and_projects_only_completed_pi_records(tmp_path) -> None:
    raw = _observed_fixture()
    path = tmp_path / "raw.jsonl"
    path.write_bytes(raw)

    trace = read_pi_trace(path)

    assert "".join(event.raw for event in trace.events).encode("utf-8") == raw
    assert [event.line_number for event in trace.events] == list(range(1, 16))
    assert [message.role for message in trace.completed_messages] == [
        "user",
        "assistant",
        "toolResult",
        "toolResult",
        "assistant",
    ]
    assert all(message.event.type == "message_end" for message in trace.messages)

    assert [tool.tool_call_id for tool in trace.tool_executions] == [
        "call-a",
        "call-b",
    ]
    bash, edit = trace.tool_executions
    assert bash.args == {"command": "pwd"}
    assert bash.result == {"content": [{"type": "text", "text": "/tmp/pi-scratch\n"}]}
    assert bash.is_error is False
    assert bash.completed
    assert edit.args == {"path": "x.py"}
    assert len(edit.updates) == 1
    assert edit.updates[0].line_number == 8
    assert edit.is_error is True

    source_lines = raw.splitlines(keepends=True)
    expected_projection = b"".join(
        source_lines[line_number - 1] for line_number in (4, 5, 6, 7, 9, 10, 11, 12, 13)
    )
    projection = trace.completed_trace
    assert projection is trace.completed is trace.projection
    assert [event.line_number for event in projection.events] == [
        4,
        5,
        6,
        7,
        9,
        10,
        11,
        12,
        13,
    ]
    assert projection.messages == trace.completed_messages
    assert projection.tool_executions == trace.tool_executions
    assert projection.to_bytes() == expected_projection
    assert projection.to_jsonl().encode("utf-8") == expected_projection


def test_summary_uses_observed_counts_usage_tools_errors_and_identity(tmp_path) -> None:
    raw = _observed_fixture()
    path = tmp_path / "raw.jsonl"
    path.write_bytes(raw)

    summary = read_pi_trace(path).summary

    assert summary.event_count == 15
    assert summary.event_types == {
        "agent_end": 1,
        "agent_settled": 1,
        "agent_start": 1,
        "message_end": 5,
        "message_start": 1,
        "session": 1,
        "tool_execution_end": 2,
        "tool_execution_start": 2,
        "tool_execution_update": 1,
    }
    assert summary.completed_message_count == 5
    assert summary.message_roles == {"assistant": 2, "toolResult": 2, "user": 1}
    assert summary.tool_execution_count == 2
    assert summary.completed_tool_execution_count == 2
    assert summary.unpaired_tool_execution_count == 0
    assert summary.tool_pairing_fidelity == 1.0
    assert summary.duration_seconds == pytest.approx(3.5)
    assert summary.usage == {
        "input": 3,
        "output": 5,
        "cacheRead": 7,
        "cacheWrite": 0,
        "reasoning": 3,
        "totalTokens": 15,
        "cost": {
            "input": pytest.approx(0.15),
            "output": pytest.approx(0.3),
            "cacheRead": pytest.approx(0.02),
            "cacheWrite": 0,
            "total": pytest.approx(0.47),
        },
    }
    assert summary.tools == {"bash": 1, "edit": 1}
    assert summary.errors == 1
    assert summary.error_tool_call_ids == ("call-b",)
    assert summary.session_id == "session-1"
    assert summary.session_version == 3
    assert summary.provider == "deepseek"
    assert summary.model == "deepseek-v4-flash"
    assert summary.cwd == "/tmp/pi-scratch"
    assert summary.started_at == "1970-01-01T00:00:01.000Z"
    assert summary.sha256 == hashlib.sha256(raw).hexdigest()
    assert summary.hash == summary.trace_hash == summary.sha256
    assert summary.raw_bytes == len(raw)
    assert summary.size_bytes == len(raw)
    assert summary.projected_bytes == read_pi_trace(path).projection.byte_count
    assert summary.projection_ratio == pytest.approx(
        summary.projected_bytes / summary.raw_bytes
    )
    assert summary.ratio == summary.projection_ratio


def test_reader_ignores_only_a_malformed_unterminated_final_line(tmp_path) -> None:
    raw = _observed_fixture()
    path = tmp_path / "raw.jsonl"
    path.write_bytes(raw + b'{"type":"message_update"')

    trace = read_pi_trace(path)

    assert len(trace.events) == 15
    assert trace.truncated_tail == b'{"type":"message_update"'
    assert trace.summary.sha256 == hashlib.sha256(path.read_bytes()).hexdigest()

    path.write_bytes(raw + b'{"type":\n')
    with pytest.raises(PiTraceError, match=r"line 16.*invalid JSON"):
        read_pi_trace(path)


def test_valid_final_json_without_newline_is_not_dropped(tmp_path) -> None:
    raw = _observed_fixture().removesuffix(b"\n")
    path = tmp_path / "raw.jsonl"
    path.write_bytes(raw)

    trace = read_pi_trace(path)

    assert len(trace.events) == 15
    assert trace.events[-1].raw == '{"type":"agent_settled"}'
    assert trace.truncated_tail is None


def test_pairing_fidelity_reports_a_complete_but_unpaired_tool_start(tmp_path) -> None:
    raw = _observed_fixture() + _json_line(
        {
            "type": "tool_execution_start",
            "toolCallId": "call-orphan",
            "toolName": "read",
            "args": {"path": "unfinished"},
        }
    )
    path = tmp_path / "raw.jsonl"
    path.write_bytes(raw)

    trace = read_pi_trace(path)

    assert trace.summary.tool_execution_count == 3
    assert trace.summary.completed_tool_execution_count == 2
    assert trace.summary.unpaired_tool_execution_count == 1
    assert trace.summary.tool_pairing_fidelity == pytest.approx(2 / 3)
    assert [tool.tool_call_id for tool in trace.projection.tool_executions] == [
        "call-a",
        "call-b",
    ]
    assert b"call-orphan" not in trace.projection.to_bytes()


class _LiveStdout:
    def __init__(self, process: _FakeProcess, lines: list[bytes]) -> None:
        self.process = process
        self.lines = lines

    def __iter__(self):
        for line in self.lines:
            assert self.process.returncode is None
            yield line
        self.process.stdout_exhausted = True


class _FakeProcess:
    def __init__(self, lines: list[bytes], *, stderr: bytes, returncode: int) -> None:
        self.returncode: int | None = None
        self.final_returncode = returncode
        self.stdout_exhausted = False
        self.wait_called = False
        self.killed = False
        self.stdout = _LiveStdout(self, lines)
        self.stderr = io.BytesIO(stderr)

    def poll(self) -> int | None:
        return self.returncode

    def wait(self) -> int:
        self.wait_called = True
        self.returncode = self.final_returncode
        return self.final_returncode

    def kill(self) -> None:
        self.killed = True
        self.returncode = -9


def test_capture_uses_argv_and_delivers_live_callbacks_before_completion(
    tmp_path,
) -> None:
    lines = [
        _json_line(
            {
                "type": "session",
                "version": 3,
                "id": "captured",
                "timestamp": "1970-01-01T00:00:00.000Z",
                "cwd": str(tmp_path),
            }
        ),
        _json_line({"type": "agent_settled"}),
    ]
    process = _FakeProcess(lines, stderr=b"provider diagnostic\n", returncode=7)
    invocation: dict[str, Any] = {}

    def factory(argv, **kwargs):
        invocation["argv"] = argv
        invocation["kwargs"] = kwargs
        return process

    raw_path = tmp_path / "capture" / "raw.jsonl"
    callbacks: list[RawPiEvent] = []

    def on_event(event: RawPiEvent) -> None:
        assert process.returncode is None
        assert not process.wait_called
        assert not process.stdout_exhausted
        assert raw_path.read_bytes().endswith(event.raw.encode("utf-8"))
        callbacks.append(event)

    result = run_pi_captured(
        "say $HOME; do not invoke a shell",
        raw_path,
        cwd=tmp_path,
        provider="deepseek",
        model="deepseek-v4-flash",
        session_dir=tmp_path / "sessions",
        name="capture test",
        pi_executable=tmp_path / "fake pi",
        on_event=on_event,
        process_factory=factory,
    )

    expected_argv = [
        str(tmp_path / "fake pi"),
        "--mode",
        "json",
        "--print",
        "--provider",
        "deepseek",
        "--model",
        "deepseek-v4-flash",
        "--session-dir",
        str(tmp_path / "sessions"),
        "--name",
        "capture test",
        "say $HOME; do not invoke a shell",
    ]
    assert invocation["argv"] == expected_argv
    assert "shell" not in invocation["kwargs"]
    assert invocation["kwargs"] == {
        "cwd": str(tmp_path),
        "stdout": subprocess.PIPE,
        "stderr": subprocess.PIPE,
        "bufsize": 0,
    }
    assert [event.type for event in callbacks] == ["session", "agent_settled"]
    assert raw_path.read_bytes() == b"".join(lines)
    assert result.argv == tuple(expected_argv)
    assert result.returncode == 7
    assert result.stderr == b"provider diagnostic\n"
    assert result.stderr_text == "provider diagnostic\n"
    assert result.trace.summary.event_count == 2
