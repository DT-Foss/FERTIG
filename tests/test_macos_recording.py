"""Offline coverage for the passive macOS demonstration recorder."""

from __future__ import annotations

import io
import json
import subprocess
import threading

import numpy as np
import pytest

from fertig.desktop import DesktopAction, DesktopDemonstration, DesktopPermissionError
from fertig.macos_recording import (
    EventTapBuildError,
    EventTapProtocolError,
    EventTapEvent,
    MacOSPassiveRecorder,
    ScreenSample,
    build_event_tap,
    check_macos_permissions,
    correlate_events,
    parse_event_line,
)


def _frame(value: int) -> np.ndarray:
    return np.full((4, 6, 3), value, dtype=np.uint8)


def _sample(milliseconds: int, value: int) -> ScreenSample:
    return ScreenSample(milliseconds * 1_000_000, _frame(value))


def test_jsonl_parser_validates_mouse_key_stop_and_metadata():
    mouse = parse_event_line(
        json.dumps(
            {
                "type": "mouse_up",
                "timestamp_ns": 12,
                "x": 10.25,
                "y": -2,
                "button": 0,
                "modifiers": ["shift"],
                "click_state": 1,
            }
        )
    )
    assert mouse == EventTapEvent(
        kind="mouse_up",
        timestamp_ns=12,
        x=10.25,
        y=-2.0,
        button=0,
        modifiers=("shift",),
    )
    assert mouse.metadata == {"click_state": 1}

    key = parse_event_line(
        b'{"type":"key_down","timestamp_ns":13,"keycode":0,'
        b'"modifiers":[],"text":"a","repeat":false}'
    )
    assert key.text == "a"
    assert key.keycode == 0
    stop = parse_event_line(
        '{"type":"stop","timestamp_ns":14,"keycode":100,"modifiers":[],"reason":"f8"}'
    )
    assert stop.kind == "stop" and stop.reason == "f8"


@pytest.mark.parametrize(
    "line,match",
    [
        ("not-json", "malformed"),
        ('{"type":"mouse_up","timestamp_ns":1}', "coordinates"),
        (
            '{"type":"key_down","timestamp_ns":1,"keycode":0,"modifiers":["hyper"]}',
            "unknown modifiers",
        ),
        ('{"type":"mystery","timestamp_ns":1}', "unknown event type"),
        ('{"type":"stop","timestamp_ns":true,"keycode":100}', "timestamp_ns"),
    ],
)
def test_malformed_jsonl_is_rejected(line, match):
    with pytest.raises(EventTapProtocolError, match=match):
        parse_event_line(line)


def test_correlation_builds_click_grouped_text_and_supported_key_steps():
    events = [
        EventTapEvent("ready", 10),
        EventTapEvent("mouse_down", 50_000_000, x=10, y=20, button=0),
        EventTapEvent("mouse_up", 80_000_000, x=11.6, y=20.4, button=0),
        EventTapEvent("key_down", 1_020_000_000, keycode=4, text="H"),
        EventTapEvent("key_down", 1_050_000_000, keycode=34, text="i"),
        EventTapEvent("key_down", 2_020_000_000, keycode=36),
        EventTapEvent("stop", 3_000_000_000, keycode=100, reason="f8"),
        # Nothing after stop can accidentally enter the demonstration.
        EventTapEvent("key_down", 3_100_000_000, keycode=0, text="x"),
    ]
    samples = [
        _sample(0, 0),
        _sample(200, 1),
        _sample(1_000, 2),
        _sample(1_200, 3),
        _sample(2_000, 4),
        _sample(2_200, 5),
        _sample(3_200, 6),
    ]
    demo = correlate_events(events, samples, label="open and title")

    assert [step.action for step in demo.steps] == [
        DesktopAction.click_at(12, 20),
        DesktopAction.enter_text("Hi"),
        DesktopAction.press_key("return"),
    ]
    assert [int(step.before[0, 0, 0]) for step in demo.steps] == [0, 2, 4]
    assert [int(step.after[0, 0, 0]) for step in demo.steps] == [1, 3, 5]
    assert demo.steps[0].elapsed_seconds == pytest.approx(0.03)


def test_unreplayable_or_safely_suppressed_input_fails_instead_of_corrupting_demo():
    samples = [_sample(0, 0), _sample(100, 1)]
    with pytest.raises(EventTapProtocolError, match="shortcuts with modifiers"):
        correlate_events(
            [
                EventTapEvent(
                    "key_down", 10_000_000, keycode=8, text="c", modifiers=("command",)
                )
            ],
            samples,
        )
    with pytest.raises(EventTapProtocolError, match="safely suppressed"):
        correlate_events(
            [
                EventTapEvent(
                    "key_down",
                    10_000_000,
                    keycode=0,
                    text_suppressed="secure_text_field",
                )
            ],
            samples,
        )
    with pytest.raises(EventTapProtocolError, match="left clicks only"):
        correlate_events(
            [EventTapEvent("mouse_up", 10_000_000, x=1, y=2, button=1)],
            samples,
        )


class _FakeSampler:
    def __init__(self, samples):
        self.samples = samples
        self.started = False
        self.finished = False

    def start(self):
        self.started = True

    def finish(self, settle_seconds):
        assert settle_seconds == pytest.approx(0.12)
        self.finished = True
        return self.samples


class _FakeProcess:
    def __init__(self, lines: list[str], *, returncode=None, stderr=""):
        self.stdout = io.StringIO("\n".join(lines) + "\n")
        self.stderr = io.StringIO(stderr)
        self.returncode = returncode
        self.terminated = False

    def poll(self):
        return self.returncode

    def terminate(self):
        self.terminated = True
        self.returncode = -15

    def kill(self):
        self.returncode = -9

    def wait(self, timeout=None):
        if self.returncode is None:
            raise subprocess.TimeoutExpired("fake-helper", timeout)
        return self.returncode


def test_fake_process_recording_stops_on_f8_and_returns_save_ready_demo(tmp_path):
    helper = tmp_path / "event-tap"
    helper.write_text("offline fake")
    helper.chmod(0o755)
    lines = [
        json.dumps({"type": "ready", "timestamp_ns": 1, "stop_key": "f8"}),
        json.dumps(
            {
                "type": "mouse_down",
                "timestamp_ns": 10_000_000,
                "x": 2,
                "y": 3,
                "button": 0,
                "modifiers": [],
            }
        ),
        json.dumps(
            {
                "type": "mouse_up",
                "timestamp_ns": 20_000_000,
                "x": 2,
                "y": 3,
                "button": 0,
                "modifiers": [],
            }
        ),
        json.dumps(
            {
                "type": "stop",
                "timestamp_ns": 30_000_000,
                "keycode": 100,
                "modifiers": [],
                "reason": "f8",
            }
        ),
    ]
    process = _FakeProcess(lines)
    sampler = _FakeSampler([_sample(0, 0), _sample(200, 1)])
    invocations = []

    def factory(command, **kwargs):
        invocations.append((command, kwargs))
        return process

    class NeverCapturedDirectly:
        def capture(self):
            raise AssertionError("injected sampler must own screenshots")

    recorder = MacOSPassiveRecorder(
        NeverCapturedDirectly(),
        helper_path=helper,
        process_factory=factory,
        sampler_factory=lambda screenshot, hz: sampler,
    )
    demo = recorder.record(label="click it")

    assert recorder.last_stop_reason == "f8"
    assert process.terminated
    assert sampler.started and sampler.finished
    assert invocations[0][0] == [str(helper)]
    assert invocations[0][1]["stdout"] == subprocess.PIPE
    assert [step.action for step in demo.steps] == [DesktopAction.click_at(2, 3)]
    paths = demo.save(tmp_path / "passive-demo")
    restored = DesktopDemonstration.load(paths.metadata)
    assert restored.label == "click it"
    assert restored.steps[0].action == DesktopAction.click_at(2, 3)


def test_helper_permission_error_is_actionable_and_sampler_is_closed(tmp_path):
    helper = tmp_path / "event-tap"
    helper.write_text("offline fake")
    helper.chmod(0o755)
    process = _FakeProcess(
        [
            json.dumps(
                {
                    "type": "error",
                    "timestamp_ns": 1,
                    "code": "input_monitoring_denied",
                    "message": "denied",
                }
            )
        ],
        returncode=77,
    )
    sampler = _FakeSampler([_sample(0, 0)])
    recorder = MacOSPassiveRecorder(
        helper_path=helper,
        process_factory=lambda *args, **kwargs: process,
        sampler_factory=lambda screenshot, hz: sampler,
    )
    with pytest.raises(DesktopPermissionError, match="Input Monitoring"):
        recorder.record()
    assert sampler.finished


def test_constructor_and_external_stop_have_no_os_side_effects(monkeypatch, tmp_path):
    calls = []
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: calls.append(args))
    recorder = MacOSPassiveRecorder(helper_path=tmp_path / "not-yet-used")
    recorder.stop()
    assert recorder.last_stop_reason is None
    assert calls == []


def test_external_stop_ends_active_recording_without_an_input_event(tmp_path):
    helper = tmp_path / "event-tap"
    helper.write_text("offline fake")
    helper.chmod(0o755)
    release_reader = threading.Event()

    class BlockingOutput:
        def __iter__(self):
            return self

        def __next__(self):
            release_reader.wait(2)
            raise StopIteration

    process = _FakeProcess([])
    process.stdout = BlockingOutput()
    sampler = _FakeSampler([_sample(0, 0), _sample(200, 1)])
    recorder = MacOSPassiveRecorder(
        helper_path=helper,
        process_factory=lambda *args, **kwargs: process,
        sampler_factory=lambda screenshot, hz: sampler,
    )
    outcome = []

    def run():
        outcome.append(recorder.record())

    thread = threading.Thread(target=run)
    thread.start()
    for _ in range(100):
        if recorder._active_process is process:
            break
        threading.Event().wait(0.005)
    recorder.stop()
    release_reader.set()
    thread.join(2)

    assert not thread.is_alive()
    assert recorder.last_stop_reason == "requested"
    assert outcome[0].steps == []
    assert process.terminated


def test_screen_sample_owns_normalised_copy():
    source = _frame(7)
    sample = ScreenSample(1, source)
    source[:] = 99
    assert np.all(sample.frame == 7)
    with pytest.raises(ValueError, match="non-negative"):
        ScreenSample(-1, _frame(0))


def test_lazy_build_retries_an_installed_sdk_on_toolchain_mismatch(
    monkeypatch, tmp_path
):
    source = tmp_path / "EventTap.swift"
    source.write_text("print(1)")
    sdk = tmp_path / "MacOSX15.sdk"
    sdk.mkdir()
    commands = []

    def runner(command, **kwargs):
        commands.append(command)
        if "-sdk" not in command:
            return subprocess.CompletedProcess(
                command, 1, "", "SDK is not supported by the compiler; SwiftShims"
            )
        output = command[command.index("-o") + 1]
        with open(output, "w", encoding="utf-8") as stream:
            stream.write("fake executable")
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr("fertig.macos_recording.sys.platform", "darwin")
    monkeypatch.setattr(
        "fertig.macos_recording._candidate_sdk_paths", lambda swiftc: (sdk,)
    )
    binary = build_event_tap(
        cache_dir=tmp_path / "cache",
        source=source,
        swiftc="/fake/swiftc",
        runner=runner,
    )
    assert binary.is_file()
    assert len(commands) == 2
    assert commands[1][commands[1].index("-sdk") + 1] == str(sdk)
    assert binary.stat().st_mode & 0o111


def test_lazy_build_reports_non_toolchain_compile_errors(monkeypatch, tmp_path):
    source = tmp_path / "EventTap.swift"
    source.write_text("broken")
    calls = []

    def runner(command, **kwargs):
        calls.append(command)
        return subprocess.CompletedProcess(command, 1, "", "syntax error")

    monkeypatch.setattr("fertig.macos_recording.sys.platform", "darwin")
    monkeypatch.setattr(
        "fertig.macos_recording._candidate_sdk_paths", lambda swiftc: ()
    )
    with pytest.raises(EventTapBuildError, match="syntax error"):
        build_event_tap(
            cache_dir=tmp_path / "cache",
            source=source,
            swiftc="/fake/swiftc",
            runner=runner,
        )
    assert len(calls) == 1


def test_permission_preflight_is_read_only_and_typed(monkeypatch, tmp_path):
    helper = tmp_path / "event-tap"
    helper.touch(mode=0o755)
    monkeypatch.setattr(
        "fertig.macos_recording.build_event_tap", lambda **_kwargs: helper
    )

    def checked(command, **kwargs):
        assert command == [str(helper), "--check"]
        return subprocess.CompletedProcess(
            command,
            0,
            json.dumps(
                {
                    "type": "status",
                    "timestamp_ns": 1,
                    "status": "permission_check",
                    "input_monitoring": True,
                    "accessibility": False,
                    "input_sent": False,
                }
            ),
            "",
        )

    monkeypatch.setattr(subprocess, "run", checked)
    status = check_macos_permissions(cache_dir=tmp_path)
    assert status.helper == helper
    assert status.input_monitoring is True
    assert status.accessibility is False
    assert status.input_sent is False
