"""CLI contract for the grounded desktop assistant."""

from __future__ import annotations

from dataclasses import dataclass
import io
import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from fertig import cli
from fertig.assistant import AssistantReply, IntentResolution
from fertig.chat import ChatReply


@dataclass
class _Calls:
    resolved: list[str]
    handled: list[tuple[str, object, object]]


class _FakeAssistant:
    def __init__(self) -> None:
        self.calls = _Calls([], [])

    def resolve(self, text: str) -> IntentResolution:
        self.calls.resolved.append(text)
        command, _, task = text.partition(" ")
        intent = {
            "teach": "teach",
            "do": "do",
            "explain": "explain",
            "list": "list",
            "HSSLM": "status",
            "help": "help",
        }.get(command, "unknown")
        return IntentResolution(
            intent,
            task or None,
            status="resolved" if intent != "unknown" else "unknown",
        )

    def handle(self, text: str, desktop=None, recorder=None) -> AssistantReply:
        self.calls.handled.append((text, desktop, recorder))
        resolution = self.resolve(text)
        return AssistantReply(
            "ok",
            resolution.intent,
            resolution.task,
            f"handled {text}",
            {"desktop": desktop is not None, "recorder": recorder is not None},
        )


class _FakeChat:
    def __init__(self, assistant: _FakeAssistant) -> None:
        self.assistant = assistant
        self.calls: list[tuple[str, object, object]] = []

    def handle(self, text: str, desktop=None, recorder=None) -> ChatReply:
        self.calls.append((text, desktop, recorder))
        raw = self.assistant.handle(text, desktop=desktop, recorder=recorder)
        return ChatReply(raw.status, "desktop", raw.text, raw.task, raw.data)


def _install_fake_surface(
    monkeypatch: pytest.MonkeyPatch,
) -> tuple[_FakeAssistant, _FakeChat]:
    assistant = _FakeAssistant()
    chat = _FakeChat(assistant)
    monkeypatch.setattr(cli, "_make_assistant", lambda _args: assistant)
    monkeypatch.setattr(cli, "_make_chat", lambda value: chat)
    return assistant, chat


def _ban_os_factories(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail(*_args, **_kwargs):
        raise AssertionError("a read-only command touched a macOS adapter")

    monkeypatch.setattr(cli, "_make_recorder", fail)
    monkeypatch.setattr(cli, "_make_desktop_environment", fail)
    monkeypatch.setattr(cli, "_make_screenshot_backend", fail)


def test_parser_exposes_chat_surface_and_defaults() -> None:
    parser = cli.build_parser()
    args = parser.parse_args(["assistant", "mach", "bericht"])
    assert args.fn is cli.cmd_assistant
    assert args.request == ["mach", "bericht"]
    assert args.store == cli.DATA / "desktop_tasks.json"
    assert args.templates == cli.DATA / "desktop_templates.json"
    assert args.recordings == cli.DATA / "desktop_recordings"
    assert args.no_hsslm is False
    assert args.resolve_only is False
    assert args.record_timeout is None

    alias = parser.parse_args(["chat", "--record-timeout", "2.5"])
    assert alias.fn is cli.cmd_assistant
    assert alias.record_timeout == 2.5


def test_parser_rejects_invalid_record_timeout() -> None:
    parser = cli.build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["teach", "--record-timeout", "0", "task"])
    with pytest.raises(SystemExit):
        parser.parse_args(["assistant", "--record-timeout", "nan"])


def test_help_lists_product_commands_without_constructing_assistant(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(
        cli,
        "_make_assistant",
        lambda _args: (_ for _ in ()).throw(
            AssertionError("--help must not construct an assistant")
        ),
    )
    with pytest.raises(SystemExit) as stopped:
        cli.main(["--help"])
    assert stopped.value.code == 0
    output = capsys.readouterr().out
    for command in (
        "assistant",
        "teach",
        "do",
        "explain",
        "compose",
        "template",
        "correct",
        "tasks",
        "hsslm-status",
        "desktop-doctor",
    ):
        assert command in output


def test_parser_builds_explicit_composition_template_and_correction_syntax() -> None:
    parser = cli.build_parser()

    composed = parser.parse_args(
        ["compose", "publish report", "--from", "open report", "export report"]
    )
    assert cli._shortcut_text(composed) == (
        "compose 'publish report' = 'open report' + 'export report'"
    )

    template = parser.parse_args(
        [
            "template",
            "send report",
            "--base",
            "fill report",
            "--slot",
            "recipient=1",
            "--optional-slot",
            "subject=3",
        ]
    )
    assert cli._shortcut_text(template) == (
        "template 'send report' from 'fill report' recipient=1 subject?=3"
    )

    correction = parser.parse_args(["correct", "monthly report", "--step", "2"])
    assert cli._shortcut_text(correction) == "correct 'monthly report' step=2"

    invocation = parser.parse_args(["do", "send report", "recipient=Grace Hopper"])
    assert cli._shortcut_text(invocation) == (
        "do 'send report' 'recipient=Grace Hopper'"
    )


@pytest.mark.parametrize(
    ("argv", "expected"),
    [
        (["tasks"], "list tasks"),
        (["hsslm-status"], "HSSLM status"),
        (["explain", "monthly", "report"], "explain monthly report"),
        (["assistant", "help"], "help"),
    ],
)
def test_read_only_routes_never_construct_os_adapters(
    argv: list[str],
    expected: str,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    fake, chat = _install_fake_surface(monkeypatch)
    _ban_os_factories(monkeypatch)

    assert cli.main(argv) == 0
    assert chat.calls[0][0] == expected
    assert chat.calls[0][1:] == (None, None)
    assert f"handled {expected}" in capsys.readouterr().out


def test_resolve_only_is_json_and_never_handles_or_touches_os(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    fake, chat = _install_fake_surface(monkeypatch)
    _ban_os_factories(monkeypatch)

    assert (
        cli.main(["assistant", "--resolve-only", "--json", "do", "monthly", "report"])
        == 0
    )
    payload = json.loads(capsys.readouterr().out)
    assert payload == {
        "confidence": 1.0,
        "intent": "do",
        "reason": "",
        "status": "resolved",
        "task": "monthly report",
    }
    assert fake.calls.handled == []
    assert chat.calls == []


def test_teach_and_do_shortcuts_create_only_the_needed_adapter(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    fake, chat = _install_fake_surface(monkeypatch)
    recorder = object()
    desktop = object()
    made: list[str] = []
    monkeypatch.setattr(
        cli,
        "_make_recorder",
        lambda _args: made.append("recorder") or recorder,
    )
    monkeypatch.setattr(
        cli,
        "_make_desktop_environment",
        lambda _args: made.append("desktop") or desktop,
    )

    assert cli.main(["teach", "invoice", "export"]) == 0
    assert made == ["recorder"]
    assert chat.calls[-1] == ("teach invoice export", None, recorder)

    assert cli.main(["do", "invoice", "export"]) == 0
    assert made == ["recorder", "desktop"]
    assert chat.calls[-1] == ("do invoice export", desktop, None)
    capsys.readouterr()


def test_json_reply_has_stable_product_schema(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _fake, _chat = _install_fake_surface(monkeypatch)
    _ban_os_factories(monkeypatch)

    assert cli.main(["tasks", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "ok"
    assert payload["route"] == "desktop"
    assert payload["task"] == "tasks"
    assert payload["data"] == {"desktop": False, "recorder": False}


def test_empty_assistant_request_runs_repl_until_exit(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    fake, chat = _install_fake_surface(monkeypatch)
    _ban_os_factories(monkeypatch)
    monkeypatch.setattr(cli.sys, "stdin", io.StringIO("help\nlist tasks\nexit\n"))

    assert cli.main(["assistant"]) == 0
    assert [call[0] for call in chat.calls] == ["help", "list tasks"]
    assert capsys.readouterr().out.splitlines() == [
        "handled help",
        "handled list tasks",
    ]


def test_real_read_only_list_and_status_need_no_desktop(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _ban_os_factories(monkeypatch)
    store = tmp_path / "tasks.json"

    assert cli.main(["tasks", "--no-hsslm", "--store", str(store), "--json"]) == 0
    listed = json.loads(capsys.readouterr().out)
    assert listed["route"] == "list"
    assert listed["data"]["tasks"] == []

    assert (
        cli.main(["hsslm-status", "--no-hsslm", "--store", str(store), "--json"]) == 0
    )
    status = json.loads(capsys.readouterr().out)
    assert status["route"] == "status"
    assert status["status"] == "unknown"


def test_unknown_do_and_grounded_math_never_construct_os_adapters(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _ban_os_factories(monkeypatch)
    store = tmp_path / "tasks.json"

    assert (
        cli.main(["do", "--no-hsslm", "--store", str(store), "unknown", "workflow"])
        == 0
    )
    assert "do not know that task" in capsys.readouterr().out

    assert (
        cli.main(["correct", "--no-hsslm", "--store", str(store), "unknown workflow"])
        == 0
    )
    assert "unknown or ambiguous" in capsys.readouterr().out

    question = (
        "A bakery sold 12 cakes on Monday and 15 cakes on Tuesday. "
        "How many cakes did they sell in total?"
    )
    assert (
        cli.main(
            [
                "assistant",
                "--no-hsslm",
                "--store",
                str(store),
                "--json",
                question,
            ]
        )
        == 0
    )
    result = json.loads(capsys.readouterr().out)
    assert result["route"] == "math"
    assert result["data"]["answer"] == "27"


def test_desktop_doctor_captures_once_and_never_builds_input(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    class Screenshot:
        calls = 0

        def capture(self):
            self.calls += 1
            return np.zeros((12, 20, 3), dtype=np.uint8)

    screenshot = Screenshot()
    helper = tmp_path / "event-tap"
    helper.write_bytes(b"binary")
    monkeypatch.setattr(cli, "_make_screenshot_backend", lambda: screenshot)
    monkeypatch.setattr(
        cli,
        "_check_recorder_permissions",
        lambda: SimpleNamespace(
            helper=helper,
            input_monitoring=True,
            accessibility=True,
            input_sent=False,
        ),
    )
    monkeypatch.setattr(
        cli,
        "_hsslm_status",
        lambda: {"ready": True, "parameter_count": 2_214_368},
    )
    monkeypatch.setattr(
        cli,
        "_make_desktop_environment",
        lambda _args: (_ for _ in ()).throw(
            AssertionError("input adapter constructed")
        ),
    )

    assert cli.main(["desktop-doctor", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "ready"
    assert payload["screen_recording"] == "granted"
    assert payload["input_monitoring"] == "granted"
    assert payload["accessibility"] == "granted"
    assert payload["recorder_helper"] == "ready"
    assert payload["hsslm"]["parameter_count"] == 2_214_368
    assert payload["input_sent"] is False
    assert payload["shape"] == [12, 20, 3]
    assert screenshot.calls == 1
