"""Tests for state-conditioned visual teach-by-showing."""

from __future__ import annotations

import numpy as np

from fertig.screen_model import (
    RESOLVED,
    UNKNOWN,
    ActionPrimitive,
    ScreenTaskModel,
    ScreenTransition,
    TaskDemo,
)


BACKGROUND = (18, 21, 27)


def _screen(
    widgets: list[tuple[tuple[int, int, int, int], tuple[int, int, int], int]],
    *,
    shape: tuple[int, int] = (72, 100),
    noise_variant: int = 0,
) -> np.ndarray:
    """Draw solid widgets with a small appearance glyph in each one."""

    frame = np.empty((*shape, 3), dtype=np.uint8)
    frame[:] = BACKGROUND
    for (x0, y0, x1, y1), colour, glyph in widgets:
        frame[y0:y1, x0:x1] = colour
        # The connected glyph makes same-colour/same-shape controls
        # distinguishable through their normalised appearance patch.
        gx = min(x1 - 2, x0 + 2 + glyph)
        frame[y0 + 2 : y1 - 2, gx : gx + 2] = np.maximum(np.asarray(colour) - 60, 0)
    if noise_variant == 1:
        frame[3:9, 5:20] = (95, 55, 120)
    elif noise_variant == 2:
        frame[56:66, 72:94] = (70, 100, 75)
        frame[4:7, 35:41] = (180, 170, 60)
    elif noise_variant == 3:
        frame[48:54, 4:36] = (45, 85, 130)
    return frame


def _transition(
    before: np.ndarray,
    target: tuple[float, float],
    after: np.ndarray,
    *,
    kind: str = "click",
    payload: str | None = None,
    success: bool | None = True,
) -> ScreenTransition:
    return ScreenTransition(
        before,
        ActionPrimitive(kind, target, payload=payload),
        after,
        success,
    )


def _three_step_demo(dx: int, noise: int) -> TaskDemo:
    first_box = (8 + dx, 10, 30 + dx, 25)
    second_box = (55 - dx, 31, 82 - dx, 47)
    third_box = (30 + dx, 51, 54 + dx, 65)
    first = _screen([(first_box, (35, 165, 105), 3)], noise_variant=noise)
    second = _screen([(second_box, (190, 95, 45), 6)], noise_variant=noise)
    third = _screen([(third_box, (55, 115, 210), 2)], noise_variant=noise)
    done = _screen([((39, 25, 61, 43), (150, 70, 190), 4)])
    return TaskDemo(
        (
            _transition(first, (first_box[0] + 16, first_box[1] + 7), second),
            _transition(second, (second_box[0] + 13, second_box[1] + 8), third),
            _transition(third, (third_box[0] + 12, third_box[1] + 7), done),
        )
    )


def test_replans_three_state_task_across_layout_and_irrelevant_changes() -> None:
    model = ScreenTaskModel().fit((_three_step_demo(0, 1), _three_step_demo(7, 2)))

    first_box = (60, 7, 86, 25)
    second_box = (7, 35, 34, 51)
    third_box = (67, 52, 91, 66)
    state0 = _screen([(first_box, (35, 165, 105), 3)], noise_variant=3)
    state1 = _screen([(second_box, (190, 95, 45), 6)], noise_variant=3)
    state2 = _screen([(third_box, (55, 115, 210), 2)], noise_variant=3)
    done = _screen([((10, 9, 32, 27), (150, 70, 190), 4)], noise_variant=2)

    first = model.next_action(state0)
    assert first.status == RESOLVED
    assert first.step_index == 0
    assert first.action is not None
    assert first_box[0] <= first.action.target[0] < first_box[2]
    history = [ScreenTransition(state0, first.action, state1, True)]

    second = model.next_action(state1, history)
    assert second.status == RESOLVED
    assert second.step_index == 1
    assert second.action is not None
    assert second_box[0] <= second.action.target[0] < second_box[2]
    history.append(ScreenTransition(state1, second.action, state2, True))

    third = model.next_action(state2, history)
    assert third.status == RESOLVED
    assert third.step_index == 2
    assert third.action is not None
    assert third_box[0] <= third.action.target[0] < third_box[2]
    history.append(ScreenTransition(state2, third.action, done, True))
    complete = model.next_action(done, history)
    assert complete.status == RESOLVED
    assert complete.action is None
    assert complete.step_index == 3


def test_preserves_relative_click_offset_when_widget_moves_and_resizes() -> None:
    train_box = (10, 12, 30, 28)
    before = _screen([(train_box, (40, 175, 95), 1)])
    after = _screen([((45, 30, 70, 47), (180, 80, 55), 4)])
    model = ScreenTaskModel().fit([TaskDemo([_transition(before, (26, 16), after)])])
    test_box = (45, 35, 85, 59)
    test = _screen([(test_box, (40, 175, 95), 1)], noise_variant=1)
    decision = model.next_action(test)
    assert decision.status == RESOLVED
    assert decision.action is not None
    # Demonstration was near 84% horizontally and 27% vertically.
    assert abs(decision.action.target[0] - 77.8) < 1.5
    assert abs(decision.action.target[1] - 41.1) < 1.5


def test_missing_and_ambiguous_targets_abstain() -> None:
    target = ((12, 10, 34, 27), (55, 170, 105), 3)
    after = _screen([((45, 30, 68, 48), (170, 80, 60), 4)])
    model = ScreenTaskModel().fit(
        [TaskDemo([_transition(_screen([target]), (22, 18), after)])]
    )

    missing = _screen([((50, 10, 75, 29), (40, 80, 205), 8)])
    missing_decision = model.next_action(missing)
    assert missing_decision.status == UNKNOWN
    assert "missing" in missing_decision.reason

    duplicate = _screen(
        [
            ((8, 8, 30, 25), target[1], target[2]),
            ((60, 38, 82, 55), target[1], target[2]),
        ]
    )
    ambiguous = model.next_action(duplicate)
    assert ambiguous.status == UNKNOWN
    assert "ambiguous" in ambiguous.reason


def test_failed_result_does_not_advance_state_but_success_does() -> None:
    demo = _three_step_demo(0, 0)
    model = ScreenTaskModel().fit([demo])
    first_state = demo.steps[0].before.frame
    second_state = demo.steps[0].after.frame
    action = model.next_action(first_state).action
    assert action is not None
    failed = ScreenTransition(first_state, action, first_state, False)
    still_first = model.next_action(first_state, [failed])
    assert still_first.step_index == 0
    succeeded = ScreenTransition(first_state, action, second_state, True)
    now_second = model.next_action(second_state, [failed, succeeded])
    assert now_second.step_index == 1


def test_successful_human_correction_adds_new_visual_prototype() -> None:
    original_box = (10, 10, 34, 27)
    original = _screen([(original_box, (35, 175, 95), 2)])
    done = _screen([((50, 30, 72, 47), (185, 75, 55), 4)])
    model = ScreenTaskModel().fit([TaskDemo([_transition(original, (22, 18), done)])])

    variant_box = (58, 38, 86, 57)
    variant = _screen([(variant_box, (190, 45, 200), 8)], noise_variant=1)
    assert model.next_action(variant).status == UNKNOWN

    wrong = ScreenTransition(variant, ActionPrimitive("click", (7, 7)), variant, False)
    assert not model.observe_result(wrong, successful=False)
    correction = _transition(variant, (72, 47), done, success=True)
    assert model.observe_result(correction, successful=True)
    learned = model.next_action(variant)
    assert learned.status == RESOLVED
    assert learned.action is not None
    assert variant_box[0] <= learned.action.target[0] < variant_box[2]
    assert "failed result" in model.explain()


def test_action_kind_payload_explanation_and_json_roundtrip(tmp_path) -> None:
    box = (15, 12, 42, 31)
    before = _screen([(box, (55, 120, 215), 5)], noise_variant=1)
    after = _screen([((51, 37, 76, 55), (160, 75, 185), 1)])
    model = ScreenTaskModel().fit(
        [
            TaskDemo(
                [
                    _transition(
                        before,
                        (26, 21),
                        after,
                        kind="type",
                        payload="monthly report",
                    )
                ]
            )
        ]
    )
    path = tmp_path / "screen-task.json"
    model.save(path)
    loaded = ScreenTaskModel.load(path)
    moved_box = (55, 8, 87, 30)
    moved = _screen([(moved_box, (55, 120, 215), 5)], noise_variant=2)
    decision = loaded.next_action(moved)
    assert decision.status == RESOLVED
    assert decision.action is not None
    assert decision.action.kind == "type"
    assert decision.action.payload == "monthly report"
    assert loaded.step_count == 1
    explanation = loaded.explain()
    assert "relative offset" in explanation
    assert "monthly report" in explanation


def test_targetless_state_action_is_supported() -> None:
    before = _screen([((10, 10, 30, 25), (40, 155, 90), 2)])
    after = _screen([((45, 30, 70, 48), (180, 85, 55), 5)])
    transition = ScreenTransition(
        before,
        ActionPrimitive("key", payload="enter"),
        after,
        True,
    )
    model = ScreenTaskModel().fit([TaskDemo([transition])])
    decision = model.next_action(_screen([], noise_variant=3))
    assert decision.status == RESOLVED
    assert decision.action == ActionPrimitive("key", payload="enter")


def test_demonstrated_actions_expose_stable_contract_without_coordinates() -> None:
    demo = _three_step_demo(0, 0)
    model = ScreenTaskModel().fit([demo])

    actions = model.demonstrated_actions()

    assert len(actions) == 3
    assert all(action.kind == "click" for action in actions)
    assert all(action.target is None for action in actions)
    assert actions[0].target_offset != (0.5, 0.5)
