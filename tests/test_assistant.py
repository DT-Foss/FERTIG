"""Product-level tests for the natural-language FERTIG assistant."""

from __future__ import annotations

import numpy as np

from fertig.assistant import (
    AMBIGUOUS,
    NEEDS_INPUT,
    OK,
    UNKNOWN,
    AssistantReply,
    FertigAssistant,
)
from fertig.desktop import (
    DesktopAction,
    DesktopDemonstration,
    DesktopEnvironment,
    DryRunInputBackend,
    RecordedStep,
)


BACKGROUND = (17, 20, 25)


def _screen(
    widgets: list[tuple[tuple[int, int, int, int], tuple[int, int, int], int]],
    *,
    decoration: int = 0,
) -> np.ndarray:
    frame = np.empty((72, 100, 3), dtype=np.uint8)
    frame[:] = BACKGROUND
    for (x0, y0, x1, y1), colour, glyph in widgets:
        frame[y0:y1, x0:x1] = colour
        glyph_x = min(x1 - 2, x0 + 2 + glyph)
        frame[y0 + 2 : y1 - 2, glyph_x : glyph_x + 2] = np.maximum(
            np.asarray(colour) - 55, 0
        )
    if decoration == 1:
        frame[4:9, 42:61] = (95, 55, 130)
    elif decoration == 2:
        frame[57:65, 5:32] = (50, 80, 130)
        frame[3:7, 78:92] = (145, 130, 40)
    return frame


def _centre(box: tuple[int, int, int, int]) -> tuple[int, int]:
    return ((box[0] + box[2]) // 2, (box[1] + box[3]) // 2)


def _demo() -> DesktopDemonstration:
    first_box = (8, 9, 31, 25)
    second_box = (57, 31, 83, 48)
    third_box = (28, 52, 54, 66)
    first = _screen([(first_box, (35, 170, 105), 2)], decoration=1)
    second = _screen([(second_box, (190, 95, 45), 6)], decoration=1)
    third = _screen([(third_box, (50, 115, 215), 3)], decoration=1)
    done = _screen([((39, 25, 62, 43), (155, 65, 190), 5)])
    return DesktopDemonstration(
        [
            RecordedStep(
                DesktopAction.click_at(*_centre(first_box)), first, second, 0.1
            ),
            RecordedStep(
                DesktopAction.click_at(*_centre(second_box)), second, third, 0.1
            ),
            RecordedStep(DesktopAction.click_at(*_centre(third_box)), third, done, 0.1),
        ],
        label="original",
    )


class FakeRecorder:
    def __init__(self, demo: DesktopDemonstration) -> None:
        self.demo = demo
        self.labels: list[str | None] = []

    def record(self, *, label: str | None = None) -> DesktopDemonstration:
        self.labels.append(label)
        return self.demo


class CountingScreenshots:
    def __init__(self, frames: list[np.ndarray]) -> None:
        self.frames = frames
        self.calls = 0

    def capture(self) -> np.ndarray:
        frame = self.frames[min(self.calls, len(self.frames) - 1)]
        self.calls += 1
        return frame


def _moved_environment() -> tuple[DesktopEnvironment, DryRunInputBackend, tuple]:
    first_box = (61, 8, 88, 27)
    second_box = (7, 34, 35, 52)
    third_box = (65, 52, 93, 67)
    frames = [
        _screen([(first_box, (35, 170, 105), 2)], decoration=2),
        _screen([(second_box, (190, 95, 45), 6)], decoration=2),
        _screen([(third_box, (50, 115, 215), 3)], decoration=2),
        _screen([((9, 11, 34, 30), (155, 65, 190), 5)]),
    ]
    inputs = DryRunInputBackend()
    return (
        DesktopEnvironment(CountingScreenshots(frames), inputs),
        inputs,
        (first_box, second_box, third_box),
    )


def _text_demo(
    example: str = "Ada",
) -> tuple[DesktopDemonstration, np.ndarray, np.ndarray]:
    before = _screen([((8, 18, 92, 48), (58, 62, 70), 1)])
    after = before.copy()
    after[27:35, 18:42] = (225, 225, 225)
    return (
        DesktopDemonstration(
            [RecordedStep(DesktopAction.enter_text(example), before, after, 0.1)],
            label="fill name",
        ),
        before,
        after,
    )


def test_german_teach_persist_reload_and_do_on_moved_layout(tmp_path) -> None:
    store_path = tmp_path / "tasks.json"
    recordings = tmp_path / "recordings"
    recorder = FakeRecorder(_demo())
    assistant = FertigAssistant(store_path, recordings_dir=recordings)

    learned = assistant.handle("Lerne bitte den Monatsbericht", recorder=recorder)
    assert learned.status == OK
    assert learned.intent == "teach"
    assert learned.task == "monatsbericht"
    assert learned.data["steps"] == 3
    assert recorder.labels == ["monatsbericht"]
    assert store_path.exists()
    assert len(list(recordings.rglob("*.json"))) == 1
    assert len(list(recordings.rglob("*.npz"))) == 1

    reloaded = FertigAssistant(store_path)
    listed = reloaded.handle("Was kannst du?")
    assert listed.status == OK
    assert listed.intent == "list"
    assert listed.data["tasks"] == ("monatsbericht",)

    desktop, inputs, boxes = _moved_environment()
    result = reloaded.handle("Führe den Monatsbericht aus", desktop=desktop)
    assert result.status == OK
    assert result.intent == "do"
    assert result.task == "monatsbericht"
    assert result.data["success"] is True
    assert len(inputs.actions) == 3
    for action, box in zip(inputs.actions, boxes):
        assert action.kind == "click"
        assert box[0] <= action.x < box[2]
        assert box[1] <= action.y < box[3]


def test_explain_and_list_are_read_only(tmp_path) -> None:
    assistant = FertigAssistant(tmp_path / "tasks.json")
    assistant.handle("teach report export", recorder=FakeRecorder(_demo()))
    desktop, inputs, _ = _moved_environment()

    explained = assistant.handle("Erkläre bitte den report export", desktop=desktop)
    assert explained.status == OK
    assert explained.intent == "explain"
    assert explained.task == "report export"
    assert "3." in explained.data["explanation"]
    assert inputs.actions == []
    assert desktop.screenshot.calls == 0


def test_shared_token_is_ambiguous_and_causes_no_desktop_side_effect(tmp_path) -> None:
    assistant = FertigAssistant(tmp_path / "tasks.json")
    assistant.handle("lerne monats bericht", recorder=FakeRecorder(_demo()))
    assistant.handle("lerne wochen bericht", recorder=FakeRecorder(_demo()))
    desktop, inputs, _ = _moved_environment()

    reply = assistant.handle("Mach den Bericht", desktop=desktop)
    assert reply.status == AMBIGUOUS
    assert reply.intent == "do"
    assert reply.task is None
    assert reply.data["alternatives"] == ("monats bericht", "wochen bericht")
    assert inputs.actions == []
    assert desktop.screenshot.calls == 0


def test_unknown_task_and_unknown_intent_never_observe_or_act(tmp_path) -> None:
    assistant = FertigAssistant(tmp_path / "tasks.json")
    desktop, inputs, _ = _moved_environment()

    unknown_task = assistant.handle("do completely unknown workflow", desktop=desktop)
    assert unknown_task.status == UNKNOWN
    assert unknown_task.intent == "do"
    unknown_intent = assistant.handle("beautiful weather today", desktop=desktop)
    assert unknown_intent.status == UNKNOWN
    assert unknown_intent.intent == "unknown"
    assert inputs.actions == []
    assert desktop.screenshot.calls == 0


def test_question_containing_run_is_not_a_desktop_command(tmp_path) -> None:
    assistant = FertigAssistant(tmp_path / "tasks.json")

    resolution = assistant.resolve("How fast can a cheetah run?")

    assert resolution.intent == "unknown"


def test_missing_runtime_adapter_is_typed_and_side_effect_free(tmp_path) -> None:
    assistant = FertigAssistant(tmp_path / "tasks.json")
    no_recorder = assistant.handle("Lerne Rechnung senden")
    assert no_recorder.status == NEEDS_INPUT
    assert no_recorder.intent == "teach"
    assert no_recorder.task == "rechnung senden"
    assert assistant.agent.list() == ()

    assistant.handle("Lerne Rechnung senden", recorder=FakeRecorder(_demo()))
    no_desktop = assistant.handle("Mach Rechnung senden")
    assert no_desktop.status == NEEDS_INPUT
    assert no_desktop.intent == "do"
    assert no_desktop.task == "rechnung senden"


def test_alias_fuzzy_match_and_structural_language_adapter(tmp_path) -> None:
    class Language:
        def resolve(self, text, tasks):
            if text == "✨":
                return {"intent": "list", "confidence": 0.99}
            return None

        def render(self, reply: AssistantReply) -> str:
            return f"HLSSM[{reply.intent}:{reply.status}] {reply.text}"

    assistant = FertigAssistant(
        tmp_path / "tasks.json",
        aliases={"abrechnung": "rechnung senden"},
        language=Language(),
    )
    assistant.handle("teach rechnung senden", recorder=FakeRecorder(_demo()))

    explained = assistant.handle("explain abrechnung")
    assert explained.status == OK
    assert explained.task == "rechnung senden"
    assert explained.text.startswith("HLSSM[explain:ok]")
    assert assistant.handle("✨").intent == "list"

    typo = assistant.handle("explain rechnug senden")
    assert typo.status == OK
    assert typo.task == "rechnung senden"


def test_grounded_hsslm_status_is_honoured_before_any_desktop_action(tmp_path) -> None:
    from fertig.hsslm_interface import GroundedLanguageInterface

    assistant = FertigAssistant(
        tmp_path / "tasks.json", language=GroundedLanguageInterface()
    )
    assistant.handle("lerne monats bericht", recorder=FakeRecorder(_demo()))
    assistant.handle("lerne wochen bericht", recorder=FakeRecorder(_demo()))
    desktop, inputs, _ = _moved_environment()

    ambiguous = assistant.handle("mach bericht", desktop=desktop)
    assert ambiguous.status == AMBIGUOUS
    assert ambiguous.intent == "do"
    assert ambiguous.data["reason"] == "multiple learned skills match"
    unknown = assistant.handle("mach wetter vorhersage", desktop=desktop)
    assert unknown.status == UNKNOWN
    assert unknown.intent == "do"
    assert unknown.data["reason"] == "no learned skill matches"
    assert inputs.actions == []
    assert desktop.screenshot.calls == 0


def test_compose_and_parameterised_skill_are_reachable_from_language(tmp_path) -> None:
    tasks = tmp_path / "tasks.json"
    templates = tmp_path / "templates.json"
    assistant = FertigAssistant(tasks, template_store=templates)
    assistant.handle("teach open report", recorder=FakeRecorder(_demo()))
    assistant.handle("teach export report", recorder=FakeRecorder(_demo()))

    composed = assistant.handle(
        'compose "publish report" = "open report" + "export report"'
    )
    assert composed.status == OK
    assert composed.intent == "compose"
    assert composed.data["children"] == ("open report", "export report")
    assert "publish report" in assistant.agent.list()

    text_demo, before, demonstrated_after = _text_demo()
    assistant.handle("teach fill name", recorder=FakeRecorder(text_demo))
    defined = assistant.handle('template "fill person" from "fill name" person=0')
    assert defined.status == OK
    assert defined.intent == "template"
    assert defined.data["slots"][0]["example"] == "Ada"

    runtime_after = before.copy()
    runtime_after[25:40, 18:85] = (225, 225, 225)
    inputs = DryRunInputBackend()
    result = assistant.handle(
        'do "fill person" person="Grace Hopper"',
        desktop=DesktopEnvironment(
            CountingScreenshots([before, runtime_after]), inputs
        ),
    )
    assert result.status == OK
    assert result.task == "fill person"
    assert result.data["base_task"] == "fill name"
    assert result.data["values"] == {"person": "Grace Hopper"}
    assert inputs.actions == [DesktopAction.enter_text("Grace Hopper")]

    reloaded = FertigAssistant(tasks, template_store=templates)
    listing = reloaded.handle("list tasks")
    assert "publish report" in listing.data["tasks"]
    assert listing.data["templates"] == ("fill person",)
    explanation = reloaded.handle("explain fill person")
    assert explanation.status == OK
    assert "global step 0" in explanation.data["explanation"]
    assert demonstrated_after.shape == runtime_after.shape


def test_missing_template_value_and_unknown_correction_are_zero_input(tmp_path) -> None:
    assistant = FertigAssistant(
        tmp_path / "tasks.json", template_store=tmp_path / "templates.json"
    )
    text_demo, before, after = _text_demo()
    assistant.handle("teach fill name", recorder=FakeRecorder(text_demo))
    assistant.handle('template "fill person" from "fill name" person=0')
    screenshots = CountingScreenshots([before, after])
    inputs = DryRunInputBackend()
    desktop = DesktopEnvironment(screenshots, inputs)

    missing = assistant.handle('do "fill person"', desktop=desktop)
    assert missing.status == UNKNOWN
    assert screenshots.calls == 0
    assert inputs.actions == []

    recorder = FakeRecorder(text_demo)
    unknown = assistant.handle("correct never learned", recorder=recorder)
    assert unknown.status == UNKNOWN
    assert recorder.labels == []


def test_correct_records_exactly_one_atomic_step_and_updates_model(tmp_path) -> None:
    assistant = FertigAssistant(
        tmp_path / "tasks.json", recordings_dir=tmp_path / "recordings"
    )
    assistant.handle("teach report", recorder=FakeRecorder(_demo()))
    correction = DesktopDemonstration([_demo().steps[0]], label="correction")
    recorder = FakeRecorder(correction)

    reply = assistant.handle("correct report step=0", recorder=recorder)

    assert reply.status == OK
    assert reply.intent == "correct"
    assert reply.data["accepted"] is True
    assert recorder.labels == ["correction:report:step:0"]
    assert len(list((tmp_path / "recordings").rglob("*.json"))) == 2
