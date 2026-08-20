"""Offline tests for the desktop demonstration adapter."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess

import numpy as np
import pytest

from fertig.desktop import (
    ACTION_ALLOWLIST,
    KEY_ALLOWLIST,
    ArrayScreenshotBackend,
    DesktopAction,
    DesktopBackendError,
    DesktopDemonstration,
    DesktopEnvironment,
    DesktopPermissionError,
    DryRunInputBackend,
    MacOSInputBackend,
    MacOSScreenshotBackend,
    RecordingSession,
    SCHEMA,
    SCHEMA_VERSION,
)


def _frame(value: int, shape: tuple[int, int] = (4, 5)) -> np.ndarray:
    return np.full((*shape, 3), value, dtype=np.uint8)


def test_action_allowlist_and_roundtrip_are_strict():
    actions = [
        DesktopAction.click_at(-2, 17),
        DesktopAction.press_key("return"),
        DesktopAction.enter_text("hello; no shell interpolation"),
        DesktopAction.wait_for(0.25),
    ]
    assert ACTION_ALLOWLIST == {"click", "key", "text", "wait"}
    assert "return" in KEY_ALLOWLIST
    assert [DesktopAction.from_dict(action.to_dict()) for action in actions] == actions

    with pytest.raises(ValueError, match="kind"):
        DesktopAction("drag")
    with pytest.raises(ValueError, match="exactly"):
        DesktopAction("click", x=1, y=2, text="surplus")
    with pytest.raises(ValueError, match="key must"):
        DesktopAction.press_key("launch-everything")
    with pytest.raises(ValueError, match="unknown action fields"):
        DesktopAction.from_dict({"kind": "wait", "seconds": 0, "shell": True})
    with pytest.raises(ValueError, match="within"):
        DesktopAction.wait_for(61)


def test_environment_dispatches_only_validated_actions_and_normalises_rgb():
    float_frame = np.full((2, 3, 3), 0.5, dtype=np.float32)
    screenshots = ArrayScreenshotBackend([float_frame] * 5)
    inputs = DryRunInputBackend()
    environment = DesktopEnvironment(screenshots, inputs)

    observed = environment.observe()
    assert observed.dtype == np.uint8
    assert np.all(observed == 128)
    assert environment.execute(DesktopAction.click_at(10, 20)).shape == (2, 3, 3)
    environment.execute(DesktopAction.press_key("tab"), observe_after=False)
    environment.execute(DesktopAction.enter_text("task name"), observe_after=False)
    environment.execute(DesktopAction.wait_for(0.01), observe_after=False)
    assert inputs.actions == [
        DesktopAction.click_at(10, 20),
        DesktopAction.press_key("tab"),
        DesktopAction.enter_text("task name"),
        DesktopAction.wait_for(0.01),
    ]
    with pytest.raises(TypeError, match="DesktopAction"):
        environment.execute({"kind": "click", "x": 1, "y": 2})


def test_invalid_screenshot_fails_before_action():
    class InvalidScreenshot:
        def capture(self):
            return np.zeros((4, 4), dtype=np.uint8)

    inputs = DryRunInputBackend()
    environment = DesktopEnvironment(InvalidScreenshot(), inputs)
    with pytest.raises(DesktopBackendError, match="shape"):
        environment.execute(DesktopAction.click_at(1, 2))
    # execute sends input first, then validates its requested after-observation.
    assert inputs.actions == [DesktopAction.click_at(1, 2)]


def test_record_save_load_roundtrip(tmp_path):
    frames = [_frame(0), _frame(10), _frame(20), _frame(30)]
    inputs = DryRunInputBackend()
    session = RecordingSession(
        DesktopEnvironment(ArrayScreenshotBackend(frames), inputs),
        label="open notes and type title",
    )
    first = session.record(DesktopAction.click_at(12, 34))
    second = session.record(DesktopAction.enter_text("Moonshot"))
    assert np.array_equal(first.before, frames[0])
    assert np.array_equal(first.after, frames[1])
    assert np.array_equal(second.before, frames[2])
    assert np.array_equal(second.after, frames[3])

    paths = session.save(tmp_path / "demo")
    assert paths.metadata.name == "demo.json"
    assert paths.frames.name == "demo.npz"
    assert paths.metadata.exists() and paths.frames.exists()
    raw = json.loads(paths.metadata.read_text())
    assert raw["schema"] == SCHEMA
    assert raw["version"] == SCHEMA_VERSION
    assert raw["frames_file"] == "demo.npz"
    assert raw["steps"][0]["action"] == {"kind": "click", "x": 12, "y": 34}

    restored = RecordingSession.load(paths.metadata)
    assert isinstance(restored, DesktopDemonstration)
    assert restored.label == session.demonstration.label
    assert [step.action for step in restored.steps] == [
        DesktopAction.click_at(12, 34),
        DesktopAction.enter_text("Moonshot"),
    ]
    for expected, actual in zip(session.steps, restored.steps):
        assert np.array_equal(expected.before, actual.before)
        assert np.array_equal(expected.after, actual.after)


def test_roundtrip_supports_resolution_changes(tmp_path):
    # Individual NPZ arrays keep a recording valid across monitor changes.
    frames = [_frame(1, (2, 3)), _frame(2, (4, 5))]
    session = RecordingSession(
        DesktopEnvironment(ArrayScreenshotBackend(frames), DryRunInputBackend())
    )
    session.record(DesktopAction.wait_for(0))
    restored = DesktopDemonstration.load(session.save(tmp_path / "resize").frames)
    assert restored.steps[0].before.shape == (2, 3, 3)
    assert restored.steps[0].after.shape == (4, 5, 3)


def test_load_rejects_wrong_schema_and_path_traversal(tmp_path):
    metadata = tmp_path / "bad.json"
    metadata.write_text(
        json.dumps(
            {
                "schema": "someone.else",
                "version": SCHEMA_VERSION,
                "frames_file": "bad.npz",
                "steps": [],
            }
        )
    )
    with pytest.raises(DesktopBackendError, match="not a FERTIG"):
        DesktopDemonstration.load(metadata)

    metadata.write_text(
        json.dumps(
            {
                "schema": SCHEMA,
                "version": SCHEMA_VERSION,
                "frames_file": "../outside.npz",
                "steps": [],
            }
        )
    )
    with pytest.raises(DesktopBackendError, match="frames_file"):
        DesktopDemonstration.load(metadata)


def test_real_backends_have_no_constructor_side_effects(monkeypatch):
    calls = []
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: calls.append(args))
    MacOSScreenshotBackend()
    MacOSInputBackend()
    assert calls == []


def test_macos_input_uses_argument_array_and_reports_permissions(monkeypatch):
    calls = []

    def denied(command, **kwargs):
        calls.append((command, kwargs))
        return subprocess.CompletedProcess(command, 1, "", "not authorized")

    monkeypatch.setattr(subprocess, "run", denied)
    backend = MacOSInputBackend()
    with pytest.raises(
        DesktopPermissionError, match="Privacy & Security > Accessibility"
    ):
        backend.text('hello "quoted"; rm is data')
    command, kwargs = calls[0]
    assert isinstance(command, list)
    assert command[0] == "/usr/bin/osascript"
    assert command[-1] == 'hello "quoted"; rm is data'
    assert kwargs["check"] is False


def test_macos_screenshot_permission_error_is_actionable(monkeypatch):
    def denied(command, **kwargs):
        return subprocess.CompletedProcess(command, 1, "", "screen capture denied")

    monkeypatch.setattr(subprocess, "run", denied)
    with pytest.raises(DesktopPermissionError, match="Screen Recording"):
        MacOSScreenshotBackend().capture()


def test_macos_screenshot_normalises_retina_pixels_to_click_coordinates(monkeypatch):
    calls = []

    def successful(command, **kwargs):
        calls.append(command)
        if command[0].endswith("screencapture"):
            Path(command[-1]).touch()
            return subprocess.CompletedProcess(command, 0, "", "")
        if command[0].endswith("sips"):
            Path(command[-1]).touch()
            return subprocess.CompletedProcess(command, 0, "", "")
        return subprocess.CompletedProcess(
            command,
            0,
            '{"width": 5, "height": 4, "scale": 2}',
            "",
        )

    physical = np.arange(8 * 10 * 3, dtype=np.uint8).reshape(8, 10, 3)
    monkeypatch.setattr(subprocess, "run", successful)
    monkeypatch.setattr("fertig.desktop._read_bmp", lambda _path: physical)

    frame = MacOSScreenshotBackend().capture()

    assert frame.shape == (4, 5, 3)
    assert calls[0][1:4] == ["-x", "-D", "1"]
    assert calls[-1][1:3] == ["-l", "JavaScript"]
