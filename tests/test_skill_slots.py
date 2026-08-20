"""Tests for deterministic dynamic text in demonstrated desktop skills."""

from __future__ import annotations

import json

import pytest

from fertig.desktop import DesktopAction
from fertig.skill_slots import (
    DuplicateSlotError,
    InvocationSyntaxError,
    MissingSlotError,
    SkillTemplate,
    SlotValueError,
    TemplateApplicationError,
    TemplateNotFoundError,
    TemplateStore,
    TextSlot,
    UnknownSlotError,
    apply_actions,
)


def _template() -> SkillTemplate:
    return SkillTemplate(
        "Send Report",
        "open mail and send report",
        (
            TextSlot("recipient", 1, "ada@example.test"),
            TextSlot("subject", 3, "Monthly report", required=False),
        ),
    )


def _actions() -> tuple[DesktopAction, ...]:
    return (
        DesktopAction.click_at(10, 20),
        DesktopAction.enter_text("ada@example.test"),
        DesktopAction.press_key("tab"),
        DesktopAction.enter_text("Monthly report"),
        DesktopAction.press_key("return"),
    )


def test_bind_validates_and_maps_values_to_demonstrated_steps() -> None:
    template = _template()

    assert template.bind({"recipient": "grace@example.test"}) == {
        1: "grace@example.test",
        3: "Monthly report",
    }
    invocation = template.invoke(
        {"recipient": "grace@example.test", "subject": "Quarterly report"}
    )
    assert invocation.template_name == "send report"
    assert invocation.base_task == "open mail and send report"
    assert dict(invocation.values) == {
        "recipient": "grace@example.test",
        "subject": "Quarterly report",
    }


def test_missing_extra_and_duplicate_slots_have_typed_failures() -> None:
    template = _template()

    with pytest.raises(MissingSlotError) as missing:
        template.bind({})
    assert missing.value.slots == ("recipient",)

    with pytest.raises(UnknownSlotError) as unknown:
        template.bind({"recipient": "Ada", "body": "invented"})
    assert unknown.value.slots == ("body",)

    with pytest.raises(DuplicateSlotError) as duplicate:
        template.bind([("recipient", "Ada"), ("RECIPIENT", "Grace")])
    assert duplicate.value.slots == ("recipient",)


def test_values_reject_empty_oversize_and_control_characters() -> None:
    template = _template()

    for invalid in ("", "a" * 10_001, "hello\nworld", "hello\x00world"):
        with pytest.raises(SlotValueError):
            template.bind({"recipient": invalid})


def test_apply_actions_replaces_only_declared_text_steps_without_mutation() -> None:
    template = _template()
    original = _actions()

    resolved = template.apply_actions(
        original,
        {"recipient": "grace@example.test", "subject": "August results"},
    )

    assert resolved is not original
    assert original == _actions()
    assert resolved[1] == DesktopAction.enter_text("grace@example.test")
    assert resolved[3] == DesktopAction.enter_text("August results")
    assert resolved[0] is original[0]
    assert resolved[2] is original[2]
    assert resolved[4] is original[4]


def test_application_rejects_wrong_kind_or_wrong_demonstrated_literal() -> None:
    template = _template()
    actions = list(_actions())
    actions[1] = DesktopAction.press_key("tab")
    with pytest.raises(TemplateApplicationError, match="not a text action"):
        template.apply_actions(actions, {"recipient": "Grace"})

    actions[1] = DesktopAction.enter_text("different demonstrated value")
    with pytest.raises(TemplateApplicationError, match="expected demonstrated text"):
        template.apply_actions(actions, {"recipient": "Grace"})


def test_low_level_application_seam_copies_actions() -> None:
    original = _actions()
    resolved = apply_actions(original, {3: "A new subject"})

    assert original[3].text == "Monthly report"
    assert resolved[3].text == "A new subject"
    assert resolved[:3] == original[:3]


def test_natural_parser_supports_multiword_names_and_quoted_values() -> None:
    store = TemplateStore()
    store.put(_template())

    invocation = store.resolve(
        'send report recipient="Grace Hopper <grace@example.test>" '
        'subject="August = green"'
    )

    assert invocation.base_task == "open mail and send report"
    assert invocation.values["recipient"] == "Grace Hopper <grace@example.test>"
    assert invocation.values["subject"] == "August = green"
    assert invocation.step_text[3] == "August = green"


def test_natural_parser_rejects_unknown_template_bad_tail_and_bad_quotes() -> None:
    store = TemplateStore()
    store.put(_template())

    with pytest.raises(TemplateNotFoundError):
        store.resolve("not learned recipient=Ada")
    with pytest.raises(InvocationSyntaxError, match="slot=value"):
        store.resolve("send report recipient=Ada stray")
    with pytest.raises(InvocationSyntaxError, match="quoting"):
        store.resolve('send report recipient="Ada')
    with pytest.raises(DuplicateSlotError):
        store.resolve("send report recipient=Ada recipient=Grace")


def test_store_persists_atomically_and_reloads(tmp_path) -> None:
    path = tmp_path / "templates" / "skills.json"
    store = TemplateStore(path)
    store.put(_template())

    assert path.exists()
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["schema"] == "fertig.desktop.skill-templates"
    assert not tuple(path.parent.glob("*.tmp"))

    reloaded = TemplateStore(path)
    assert reloaded.list() == ("send report",)
    invocation = reloaded.resolve(
        '"send report" recipient="Katherine Johnson" subject=Trajectory'
    )
    assert invocation.step_text == {1: "Katherine Johnson", 3: "Trajectory"}


def test_single_action_execution_seam_changes_only_its_declared_index() -> None:
    invocation = _template().invoke({"recipient": "Grace"})
    actions = _actions()

    assert invocation.apply_action(0, actions[0]) is actions[0]
    assert invocation.apply_action(1, actions[1]).text == "Grace"
    assert invocation.apply_action(3, actions[3]).text == "Monthly report"
