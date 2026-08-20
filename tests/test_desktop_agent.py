"""End-to-end tests for the persistent desktop task agent."""

from __future__ import annotations

import json

import numpy as np
import pytest

from fertig.desktop import (
    ArrayScreenshotBackend,
    DesktopAction,
    DesktopDemonstration,
    DesktopEnvironment,
    DryRunInputBackend,
    RecordedStep,
)
from fertig.desktop_agent import (
    DesktopAgent,
    TaskStore,
    action_to_primitive,
    demonstration_to_task,
    primitive_to_action,
)
from fertig.screen_model import RESOLVED, UNKNOWN, ScreenTaskModel
from fertig.skill_slots import (
    MissingSlotError,
    SkillTemplate,
    TemplateApplicationError,
    TemplateStore,
    TextSlot,
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
    elif decoration == 3:
        frame[4:12, 4:22] = (80, 115, 65)
    return frame


def _centre(box: tuple[int, int, int, int]) -> tuple[int, int]:
    return ((box[0] + box[2]) // 2, (box[1] + box[3]) // 2)


def _demo(offset: int, decoration: int) -> DesktopDemonstration:
    first_box = (8 + offset, 9, 31 + offset, 25)
    second_box = (57 - offset, 31, 83 - offset, 48)
    third_box = (28 + offset, 52, 54 + offset, 66)
    first = _screen([(first_box, (35, 170, 105), 2)], decoration=decoration)
    second = _screen([(second_box, (190, 95, 45), 6)], decoration=decoration)
    third = _screen([(third_box, (50, 115, 215), 3)], decoration=decoration)
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
        label="finish report flow",
    )


def _one_step_demo(
    before: np.ndarray,
    target_box: tuple[int, int, int, int],
    after: np.ndarray,
    *,
    label: str,
) -> DesktopDemonstration:
    return DesktopDemonstration(
        [
            RecordedStep(
                DesktopAction.click_at(*_centre(target_box)), before, after, 0.1
            )
        ],
        label=label,
    )


def _composable_frames(
    *, offset: int = 0
) -> tuple[
    tuple[np.ndarray, tuple[int, int, int, int]],
    tuple[np.ndarray, tuple[int, int, int, int]],
    tuple[np.ndarray, tuple[int, int, int, int]],
    np.ndarray,
]:
    first_box = (7 + offset, 8, 28 + offset, 25)
    second_box = (55 - offset, 29, 80 - offset, 47)
    third_box = (26 + offset, 51, 51 + offset, 67)
    first = _screen([(first_box, (35, 170, 105), 2)], decoration=1)
    second = _screen([(second_box, (190, 95, 45), 6)], decoration=2)
    third = _screen([(third_box, (50, 115, 215), 3)], decoration=3)
    done = _screen([((39, 24, 63, 43), (155, 65, 190), 5)])
    return (first, first_box), (second, second_box), (third, third_box), done


def _teach_composable(agent: DesktopAgent) -> None:
    first, second, third, done = _composable_frames()
    agent.teach_from_demo(
        "open report",
        _one_step_demo(first[0], first[1], second[0], label="open report"),
    )
    agent.teach_from_demo(
        "export report",
        _one_step_demo(second[0], second[1], third[0], label="export report"),
    )
    agent.teach_from_demo(
        "close report",
        _one_step_demo(third[0], third[1], done, label="close report"),
    )


def _parameterised_demo(
    example: str = "Ada Lovelace",
) -> tuple[DesktopDemonstration, tuple[np.ndarray, np.ndarray, np.ndarray]]:
    button = (8, 9, 31, 25)
    start = _screen([(button, (35, 170, 105), 2)], decoration=1)
    editor = _screen([((53, 29, 84, 49), (190, 95, 45), 6)], decoration=2)
    done = _screen([((28, 51, 55, 67), (50, 115, 215), 3)], decoration=3)
    demo = DesktopDemonstration(
        [
            RecordedStep(DesktopAction.click_at(*_centre(button)), start, editor, 0.1),
            RecordedStep(DesktopAction.enter_text(example), editor, done, 0.1),
        ],
        label="address report",
    )
    return demo, (start, editor, done)


def test_action_mapping_uses_existing_desktop_types() -> None:
    actions = (
        DesktopAction.click_at(12, 34),
        DesktopAction.press_key("return"),
        DesktopAction.enter_text("monthly report"),
        DesktopAction.wait_for(0.25),
    )
    assert [primitive_to_action(action_to_primitive(item)) for item in actions] == list(
        actions
    )


def test_teach_and_do_three_steps_on_moved_layout_closed_loop() -> None:
    agent = DesktopAgent()
    agent.teach_from_demo("Finish Report", (_demo(0, 1), _demo(7, 2)))
    assert agent.list() == ("finish report",)

    first_box = (61, 8, 88, 27)
    second_box = (7, 34, 35, 52)
    third_box = (65, 52, 93, 67)
    first = _screen([(first_box, (35, 170, 105), 2)], decoration=3)
    second = _screen([(second_box, (190, 95, 45), 6)], decoration=3)
    third = _screen([(third_box, (50, 115, 215), 3)], decoration=3)
    done = _screen([((9, 11, 34, 30), (155, 65, 190), 5)], decoration=2)
    inputs = DryRunInputBackend()
    environment = DesktopEnvironment(
        ArrayScreenshotBackend([first, second, third, done]), inputs
    )

    result = agent.do("finish report", environment)
    assert result.status == RESOLVED
    assert result.success
    assert len(result.steps) == 3
    assert all(step.verified for step in result.steps)
    assert len(inputs.actions) == 3
    for action, box in zip(inputs.actions, (first_box, second_box, third_box)):
        assert action.kind == "click"
        assert box[0] <= action.x < box[2]
        assert box[1] <= action.y < box[3]


def test_task_store_persists_and_reload_executes(tmp_path) -> None:
    path = tmp_path / "desktop-tasks.json"
    original = DesktopAgent(TaskStore(path))
    original.teach_from_demo("report", (_demo(0, 1), _demo(6, 2)))
    assert path.exists()

    reloaded = DesktopAgent(TaskStore(path))
    assert reloaded.list() == ("report",)
    assert "3." in reloaded.explain("report")
    first_box = (55, 8, 80, 26)
    second_box = (8, 33, 34, 50)
    third_box = (62, 52, 88, 66)
    frames = [
        _screen([(first_box, (35, 170, 105), 2)], decoration=3),
        _screen([(second_box, (190, 95, 45), 6)], decoration=3),
        _screen([(third_box, (50, 115, 215), 3)], decoration=3),
        _screen([((11, 12, 34, 30), (155, 65, 190), 5)]),
    ]
    result = reloaded.do(
        "report",
        DesktopEnvironment(ArrayScreenshotBackend(frames), DryRunInputBackend()),
    )
    assert result.success


def test_repeated_teach_accumulates_examples_instead_of_replacing(tmp_path) -> None:
    path = tmp_path / "desktop-tasks.json"
    agent = DesktopAgent(TaskStore(path))

    agent.teach_from_demo("report", _demo(0, 1))
    agent.teach_from_demo("report", _demo(7, 2))

    explanation = DesktopAgent(TaskStore(path)).explain("report")
    assert "learned from 2 successful example(s)" in explanation


def test_unknown_or_ambiguous_target_stops_before_input() -> None:
    agent = DesktopAgent()
    agent.teach_from_demo("report", _demo(0, 0))
    unrelated = _screen([((55, 12, 82, 31), (180, 35, 205), 8)])
    inputs = DryRunInputBackend()
    result = agent.do(
        "report",
        DesktopEnvironment(
            ArrayScreenshotBackend([unrelated], repeat_last=True), inputs
        ),
    )
    assert result.status == UNKNOWN
    assert not result.success
    assert inputs.actions == []

    unknown_task = agent.do(
        "never taught",
        DesktopEnvironment(
            ArrayScreenshotBackend([unrelated], repeat_last=True), inputs
        ),
    )
    assert unknown_task.status == UNKNOWN
    assert inputs.actions == []


def test_visible_verification_failure_stops_after_exactly_one_action() -> None:
    agent = DesktopAgent()
    demo = _demo(0, 0)
    agent.teach_from_demo("report", demo)
    before = demo.steps[0].before
    # The click changes no visible state, so the demonstrated next state is
    # not verified and no second action may cross the environment boundary.
    inputs = DryRunInputBackend()
    result = agent.do(
        "report",
        DesktopEnvironment(ArrayScreenshotBackend([before, before]), inputs),
    )
    assert result.status == UNKNOWN
    assert not result.success
    assert len(result.steps) == 1
    assert not result.steps[0].verified
    assert len(inputs.actions) == 1


def test_correction_learns_new_visual_variant_and_is_persisted(tmp_path) -> None:
    path = tmp_path / "tasks.json"
    agent = DesktopAgent(TaskStore(path))
    demo = _demo(0, 0)
    agent.teach_from_demo("report", demo)

    variant_box = (58, 37, 88, 58)
    variant = _screen([(variant_box, (190, 40, 205), 8)], decoration=1)
    corrected_after = demo.steps[0].after
    before_inputs = DryRunInputBackend()
    before_result = agent.do(
        "report",
        DesktopEnvironment(
            ArrayScreenshotBackend([variant], repeat_last=True), before_inputs
        ),
    )
    assert before_result.status == UNKNOWN
    assert before_inputs.actions == []

    correction = RecordedStep(
        DesktopAction.click_at(*_centre(variant_box)), variant, corrected_after, 0.2
    )
    assert agent.correct("report", correction, step_index=0)

    reloaded = DesktopAgent(TaskStore(path))
    inputs = DryRunInputBackend()
    # Run just the corrected first state: it must now act on the variant.  The
    # max-step stop after that is expected because the full task has 3 steps.
    result = reloaded.do(
        "report",
        DesktopEnvironment(ArrayScreenshotBackend([variant, corrected_after]), inputs),
        max_steps=1,
    )
    assert result.status == UNKNOWN
    assert len(inputs.actions) == 1
    assert variant_box[0] <= inputs.actions[0].x < variant_box[2]
    assert result.steps[0].verified


def test_composition_executes_unseen_a_then_b_in_one_environment() -> None:
    agent = DesktopAgent()
    _teach_composable(agent)
    assert agent.compose("publish report", ("open report", "export report")) == (
        "open report",
        "export report",
    )
    assert agent.list() == (
        "close report",
        "export report",
        "open report",
        "publish report",
    )

    first, second, third, _ = _composable_frames(offset=6)
    inputs = DryRunInputBackend()
    result = agent.do(
        "publish report",
        DesktopEnvironment(
            ArrayScreenshotBackend([first[0], second[0], third[0]]), inputs
        ),
    )

    assert result.status == RESOLVED
    assert result.success
    assert [step.index for step in result.steps] == [0, 1]
    assert len(inputs.actions) == 2
    for action, box in zip(inputs.actions, (first[1], second[1])):
        assert box[0] <= action.x < box[2]
        assert box[1] <= action.y < box[3]


def test_composition_persists_reloads_and_explains_leaf_steps(tmp_path) -> None:
    path = tmp_path / "tasks.json"
    agent = DesktopAgent(TaskStore(path))
    _teach_composable(agent)
    agent.compose("publish report", ("open report", "export report"))

    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["version"] == 2
    assert payload["compositions"]["publish report"] == [
        "open report",
        "export report",
    ]
    reloaded = DesktopAgent(TaskStore(path))
    explanation = reloaded.explain("publish report")
    assert "Composed desktop task 'publish report'" in explanation
    assert "atomic 'open report': Screen task:" in explanation
    assert "atomic 'export report': Screen task:" in explanation

    first, second, third, _ = _composable_frames(offset=5)
    inputs = DryRunInputBackend()
    result = reloaded.do(
        "publish report",
        DesktopEnvironment(
            ArrayScreenshotBackend([first[0], second[0], third[0]]), inputs
        ),
    )
    assert result.success
    assert len(inputs.actions) == 2


def test_nested_composition_flattens_leaves_in_order() -> None:
    agent = DesktopAgent()
    _teach_composable(agent)
    agent.compose("publish report", ("open report", "export report"))
    agent.compose("publish and close", ("publish report", "close report"))

    first, second, third, done = _composable_frames(offset=4)
    inputs = DryRunInputBackend()
    result = agent.do(
        "publish and close",
        DesktopEnvironment(
            ArrayScreenshotBackend([first[0], second[0], third[0], done]), inputs
        ),
    )

    assert result.success
    assert [step.index for step in result.steps] == [0, 1, 2]
    assert len(inputs.actions) == 3
    explanation = agent.explain("publish and close")
    assert "composed 'publish report'" in explanation
    assert explanation.count("Screen task:") == 3


def test_composition_rejects_unknown_duplicates_empty_names_and_cycles() -> None:
    agent = DesktopAgent()
    _teach_composable(agent)

    with pytest.raises(KeyError, match="unknown desktop task"):
        agent.compose("broken", ("open report", "never learned"))
    with pytest.raises(ValueError, match="duplicate"):
        agent.compose("broken", ("open report", "open report"))
    with pytest.raises(ValueError, match="must not be empty"):
        agent.compose("broken", ("open report", "   "))
    with pytest.raises(ValueError, match="cycle"):
        agent.compose("loop", ("open report", "loop"))

    agent.compose("publish report", ("open report", "export report"))
    with pytest.raises(ValueError, match="cycle"):
        agent.compose("open report", ("publish report", "close report"))


def test_failure_in_first_leaf_prevents_all_later_actions() -> None:
    agent = DesktopAgent()
    _teach_composable(agent)
    agent.compose("publish report", ("open report", "export report"))
    first, _, _, _ = _composable_frames(offset=3)
    inputs = DryRunInputBackend()

    result = agent.do(
        "publish report",
        DesktopEnvironment(ArrayScreenshotBackend([first[0], first[0]]), inputs),
    )

    assert result.status == UNKNOWN
    assert not result.success
    assert "leaf task 'open report' failed" in result.reason
    assert len(result.steps) == 1
    assert len(inputs.actions) == 1


def test_version_one_store_fixture_remains_loadable(tmp_path) -> None:
    path = tmp_path / "v1-tasks.json"
    original = DesktopAgent(TaskStore(path))
    original.teach_from_demo("report", _demo(0, 1))
    fixture = json.loads(path.read_text(encoding="utf-8"))
    fixture["version"] = 1
    fixture.pop("compositions")
    path.write_text(json.dumps(fixture), encoding="utf-8")

    reloaded = DesktopAgent(TaskStore(path))

    assert reloaded.list() == ("report",)
    assert "Screen task:" in reloaded.explain("report")


def test_parameterised_atomic_skill_replans_moved_layout_and_verifies() -> None:
    agent = DesktopAgent()
    demo, (_, editor, done) = _parameterised_demo()
    agent.teach_from_demo("address report", demo)
    template = agent.define_template(
        "send named report",
        "address report",
        (TextSlot("recipient", 1, "Ada Lovelace"),),
    )
    assert template.name == "send named report"
    assert agent.list() == ("address report",)
    assert agent.list_templates() == ("send named report",)
    assert "global step 1" in agent.explain_template("send named report")

    moved_button = (62, 8, 91, 28)
    moved_start = _screen([(moved_button, (35, 170, 105), 2)], decoration=3)
    inputs = DryRunInputBackend()
    result = agent.do_template(
        "send named report",
        {"recipient": "Grace Hopper"},
        DesktopEnvironment(ArrayScreenshotBackend([moved_start, editor, done]), inputs),
    )

    assert result.status == RESOLVED
    assert result.success
    assert result.task == "send named report"
    assert [step.index for step in result.steps] == [0, 1]
    assert all(step.verified for step in result.steps)
    assert inputs.actions[0].kind == "click"
    assert moved_button[0] <= inputs.actions[0].x < moved_button[2]
    assert inputs.actions[1] == DesktopAction.enter_text("Grace Hopper")


def test_template_over_composition_uses_global_flattened_step_index() -> None:
    agent = DesktopAgent()
    demo, (start, editor, done) = _parameterised_demo()
    agent.teach_from_demo(
        "open editor",
        DesktopDemonstration((demo.steps[0],), label="open editor"),
    )
    agent.teach_from_demo(
        "fill recipient",
        DesktopDemonstration((demo.steps[1],), label="fill recipient"),
    )
    agent.compose("address report", ("open editor", "fill recipient"))
    agent.define_template(
        "send named report",
        "address report",
        (TextSlot("recipient", 1, "Ada Lovelace"),),
    )
    inputs = DryRunInputBackend()

    invocation = agent.resolve_template(
        'send named report recipient="Katherine Johnson"'
    )
    result = agent.invoke_template(
        invocation,
        DesktopEnvironment(ArrayScreenshotBackend([start, editor, done]), inputs),
    )

    assert result.success
    assert [step.index for step in result.steps] == [0, 1]
    assert inputs.actions[1] == DesktopAction.enter_text("Katherine Johnson")
    explanation = agent.explain_template("send named report")
    assert "composed base task 'address report'" in explanation


def test_missing_template_slot_fails_before_first_input() -> None:
    agent = DesktopAgent()
    demo, frames = _parameterised_demo()
    agent.teach_from_demo("address report", demo)
    agent.define_template(
        "send named report",
        "address report",
        (TextSlot("recipient", 1, "Ada Lovelace"),),
    )
    with pytest.raises(MissingSlotError, match="recipient"):
        agent.prepare_template("send named report", {})

    inputs = DryRunInputBackend()
    result = agent.do_template(
        "send named report",
        {},
        DesktopEnvironment(ArrayScreenshotBackend(frames), inputs),
    )

    assert result.status == UNKNOWN
    assert not result.success
    assert result.steps == ()
    assert "missing required slot" in result.reason
    assert inputs.actions == []


def test_task_and_template_stores_persist_and_reload_together(tmp_path) -> None:
    task_path = tmp_path / "tasks.json"
    template_path = tmp_path / "templates.json"
    original = DesktopAgent(TaskStore(task_path), TemplateStore(template_path))
    demo, (start, editor, done) = _parameterised_demo()
    original.teach_from_demo("address report", demo)
    original.define_template(
        "send named report",
        "address report",
        (TextSlot("recipient", 1, "Ada Lovelace"),),
    )

    reloaded = DesktopAgent(TaskStore(task_path), TemplateStore(template_path))
    assert reloaded.list() == ("address report",)
    assert reloaded.list_templates() == ("send named report",)
    assert "base contract valid" in reloaded.explain_template("send named report")
    inputs = DryRunInputBackend()
    result = reloaded.do_template_utterance(
        'send named report recipient="Dorothy Vaughan"',
        DesktopEnvironment(ArrayScreenshotBackend([start, editor, done]), inputs),
    )

    assert result.success
    assert inputs.actions[-1] == DesktopAction.enter_text("Dorothy Vaughan")


def test_stale_template_base_mismatch_fails_before_first_input() -> None:
    agent = DesktopAgent()
    demo, frames = _parameterised_demo()
    agent.teach_from_demo("address report", demo)
    agent.define_template(
        "send named report",
        "address report",
        (TextSlot("recipient", 1, "Ada Lovelace"),),
    )

    changed_demo, _ = _parameterised_demo("A different demonstrated value")
    changed_model = ScreenTaskModel().fit([demonstration_to_task(changed_demo)])
    agent.store.put("address report", changed_model)
    inputs = DryRunInputBackend()
    result = agent.do_template(
        "send named report",
        {"recipient": "Grace Hopper"},
        DesktopEnvironment(ArrayScreenshotBackend(frames), inputs),
    )

    assert result.status == UNKNOWN
    assert not result.success
    assert result.steps == ()
    assert "expected demonstrated text 'Ada Lovelace'" in result.reason
    assert inputs.actions == []


def test_template_definition_rejects_non_text_slot_or_unknown_base() -> None:
    agent = DesktopAgent()
    demo, _ = _parameterised_demo()
    agent.teach_from_demo("address report", demo)

    with pytest.raises(TemplateApplicationError, match="not a text action"):
        agent.define_template(
            "bad slot",
            "address report",
            (TextSlot("recipient", 0, "Ada Lovelace"),),
        )
    with pytest.raises(KeyError, match="unknown desktop task"):
        agent.define_template(
            "unknown base",
            "never taught",
            (TextSlot("recipient", 0, "Ada Lovelace"),),
        )
    assert agent.list_templates() == ()


def test_parameterised_text_verification_accepts_different_length_and_pixels() -> None:
    before = _screen([((10, 20, 90, 50), (65, 65, 70), 1)])
    demonstrated_after = before.copy()
    demonstrated_after[29:34, 18:31] = (225, 225, 225)
    runtime_after = before.copy()
    runtime_after[28:39, 18:84] = (225, 225, 225)
    agent = DesktopAgent()
    agent.teach_from_demo(
        "fill name",
        DesktopDemonstration(
            (
                RecordedStep(
                    DesktopAction.enter_text("Ada"),
                    before,
                    demonstrated_after,
                    0.1,
                ),
            ),
            label="fill name",
        ),
    )
    agent.define_template(
        "fill arbitrary name",
        "fill name",
        (TextSlot("name", 0, "Ada"),),
    )
    inputs = DryRunInputBackend()
    replacement = "Professor Katherine Coleman Goble Johnson"

    result = agent.do_template(
        "fill arbitrary name",
        {"name": replacement},
        DesktopEnvironment(ArrayScreenshotBackend([before, runtime_after]), inputs),
    )

    assert result.success
    assert result.steps[0].verified
    assert inputs.actions == [DesktopAction.enter_text(replacement)]


def test_task_and_template_names_cannot_collide() -> None:
    agent = DesktopAgent()
    demo, _ = _parameterised_demo()
    agent.teach_from_demo("address report", demo)
    with pytest.raises(ValueError, match="already a desktop task"):
        agent.define_template(
            "address report",
            "address report",
            (TextSlot("recipient", 1, "Ada Lovelace"),),
        )

    agent.define_template(
        "send named report",
        "address report",
        (TextSlot("recipient", 1, "Ada Lovelace"),),
    )
    with pytest.raises(ValueError, match="already a skill template"):
        agent.teach_from_demo("send named report", demo)

    click_demo = DesktopDemonstration((demo.steps[0],), label="click only")
    agent.teach_from_demo("click one", click_demo)
    agent.teach_from_demo("click two", click_demo)
    with pytest.raises(ValueError, match="already a skill template"):
        agent.compose("send named report", ("click one", "click two"))


def test_preexisting_store_name_collision_is_rejected_on_agent_start(tmp_path) -> None:
    task_store = TaskStore(tmp_path / "tasks.json")
    template_store = TemplateStore(tmp_path / "templates.json")
    demo, _ = _parameterised_demo()
    task_store.teach("same name", (demo,))
    template_store.put(
        SkillTemplate(
            "same name",
            "same name",
            (TextSlot("recipient", 1, "Ada Lovelace"),),
        )
    )

    with pytest.raises(ValueError, match="names collide"):
        DesktopAgent(task_store, template_store)
