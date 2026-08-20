"""Tests for the unified grounded FERTIG chat router."""

from __future__ import annotations

from dataclasses import dataclass

from fertig.assistant import AssistantReply, FertigAssistant, IntentResolution
from fertig.chat import FertigChat


class FakeAgent:
    def __init__(self, tasks=("report 2024",)) -> None:
        self.tasks = tuple(tasks)

    def list(self):
        return self.tasks


class FakeAssistant:
    def __init__(self, tasks=("report 2024",), language=None) -> None:
        self.agent = FakeAgent(tasks)
        self.language = language
        self.calls: list[str] = []

    def resolve(self, text: str):
        low = text.casefold()
        if low.startswith(("teach ", "lerne ")):
            return IntentResolution("teach", text.split(maxsplit=1)[1])
        if low.startswith(("do ", "mach ")):
            return IntentResolution("do", text.split(maxsplit=1)[1])
        if low.startswith(("explain ", "erkläre ")):
            return IntentResolution("explain", text.split(maxsplit=1)[1])
        if "list" in low or "was kannst du" in low:
            return IntentResolution("list")
        if "help" in low or "hilfe" in low:
            return IntentResolution("help")
        return IntentResolution("unknown", None, 0.0)

    def handle(self, text, desktop=None, recorder=None):
        self.calls.append(text)
        resolution = self.resolve(text)
        task = resolution.task
        known = task in self.agent.tasks
        if resolution.intent == "teach":
            return AssistantReply("needs_input", "teach", task, "recorder needed")
        if resolution.intent == "do":
            return AssistantReply(
                "ok" if known else "unknown",
                "do",
                task if known else None,
                f"done {task}" if known else "unknown task",
            )
        if resolution.intent == "explain":
            return AssistantReply(
                "ok" if known else "unknown",
                "explain",
                task if known else None,
                f"steps for {task}" if known else "unknown task",
            )
        return AssistantReply("unknown", "unknown", None, "unknown")


def test_explicit_desktop_route_beats_math_and_followup_uses_last_task() -> None:
    assistant = FakeAssistant()
    chat = FertigChat(assistant)

    done = chat.handle("do report 2024", desktop=object())
    assert done.route == "desktop" and done.status == "ok"
    assert done.task == "report 2024"
    explained = chat.handle("explain it")
    assert explained.route == "desktop" and explained.task == "report 2024"
    assert assistant.calls == ["do report 2024", "explain report 2024"]
    assert chat.last_task == "report 2024"
    assert len(chat.history) == 2
    assert chat.history[-1].user == "explain it"


def test_known_desktop_explain_wins_but_unknown_explain_falls_to_graph() -> None:
    assistant = FakeAssistant(("smoking report",))
    chat = FertigChat(assistant)

    desktop = chat.handle("explain smoking report")
    assert desktop.route == "desktop"
    graph = chat.handle("explain how smoking affects health")
    assert graph.route == "graph" and graph.status == "ok"
    assert graph.data["target"] == "smoking"
    assert "tar buildup" in graph.text.lower()
    assert assistant.calls == ["explain smoking report"]


def test_real_arithmetic_and_quantitative_fallbacks() -> None:
    chat = FertigChat(FakeAssistant(()))
    math = chat.handle(
        "A bakery sold 12 cakes on Monday and 15 cakes on Tuesday. "
        "How many cakes did they sell in total?"
    )
    assert math.route == "math" and math.data["answer"] == "27"

    measured = chat.handle("How fast can a cheetah run?")
    assert measured.route == "quant"
    assert measured.data["answer"] == "104 km/h"
    assert measured.data["mechanism"] == "running_at"


def test_real_assistant_does_not_turn_run_question_into_desktop_input(tmp_path) -> None:
    chat = FertigChat(FertigAssistant(tmp_path / "tasks.json"))

    measured = chat.handle("How fast can a cheetah run?")

    assert measured.route == "quant"
    assert measured.status == "ok"
    assert measured.data["answer"] == "104 km/h"


def test_why_is_mapped_to_grounded_graph_explanation() -> None:
    chat = FertigChat(FakeAssistant(()))
    result = chat.handle("Why does smoking affect health?")
    assert result.route == "graph" and result.status == "ok"
    assert result.data["tool"] == "speech"
    assert result.data["target"] == "smoking"


def test_list_and_help_combine_tasks_with_non_desktop_capabilities() -> None:
    chat = FertigChat(FakeAssistant(("report 2024", "send invoice")))
    listed = chat.handle("list tasks")
    assert listed.route == "list"
    assert listed.data["tasks"] == ("report 2024", "send invoice")
    assert "solve grounded arithmetic questions" in listed.data["capabilities"]
    assert "report 2024" in listed.text

    helped = chat.handle("help")
    assert helped.route == "help"
    assert helped.data["tasks"] == listed.data["tasks"]


@dataclass(frozen=True)
class FakeStatus:
    checkpoint: str = "/models/form.pt"
    tokenizer: str = "/models/bpe.json"
    ready: bool = True
    parameter_count: int = 2_214_368
    serialized_parameter_count: int = 2_316_768
    size_bytes: int = 8_912_345
    device: str = "cpu"
    reason: str = ""


class FakeRuntime:
    def status(self):
        return FakeStatus()


class FactLanguage:
    def __init__(self, *, preserve: bool = True) -> None:
        self.runtime = FakeRuntime()
        self.preserve = preserve

    def render(self, event, facts):
        if not self.preserve:
            return "I used a brand-new desktop tool."
        return (
            event + ": " + "; ".join(f"{key}={value}" for key, value in facts.items())
        )


def test_hsslm_status_is_exact_and_language_must_preserve_facts() -> None:
    language = FactLanguage()
    chat = FertigChat(FakeAssistant((), language=language))
    result = chat.handle("HLSSM parameter status?")
    assert result.route == "status" and result.status == "ok"
    assert result.data["parameter_count"] == 2_214_368
    assert result.data["serialized_parameter_count"] == 2_316_768
    assert "2214368" in result.text.replace("_", "")
    assert "/models/form.pt" in result.text

    untrusted = FertigChat(FakeAssistant((), language=FactLanguage(preserve=False)))
    measured = untrusted.handle("How fast can a cheetah run?")
    assert measured.route == "quant"
    assert "brand-new desktop tool" not in measured.text
    assert "104 km/h" in measured.text


def test_grounded_renderer_receives_natural_fallback_not_field_dump(tmp_path) -> None:
    from fertig.assistant import FertigAssistant
    from fertig.hsslm_interface import GroundedLanguageInterface

    chat = FertigChat(
        FertigAssistant(tmp_path / "tasks.json", language=GroundedLanguageInterface())
    )

    measured = chat.handle("How fast can a cheetah run?")

    assert measured.text.startswith("Measured answer: 104 km/h")


def test_unknown_and_missing_followup_are_typed_and_recorded() -> None:
    chat = FertigChat(FakeAssistant(()))
    followup = chat.handle("erkläre das")
    assert followup.status == "unknown" and followup.route == "unknown"
    unknown = chat.handle("beautiful weather today")
    assert unknown.status == "unknown" and unknown.route == "unknown"
    assert len(chat.history) == 2


def test_management_and_parameterized_commands_reach_assistant_verbatim() -> None:
    class ManagementAssistant(FakeAssistant):
        def resolve(self, text: str):
            low = text.casefold()
            if low.startswith("compose "):
                return IntentResolution("compose", "publish report")
            if low.startswith("template "):
                return IntentResolution("template", "send report")
            if low.startswith("correct "):
                return IntentResolution("correct", "report")
            if low.startswith("do ") and "=" in text:
                return IntentResolution("do", "send report")
            return super().resolve(text)

        def handle(self, text, desktop=None, recorder=None):
            self.calls.append(text)
            resolved = self.resolve(text)
            return AssistantReply("ok", resolved.intent, resolved.task, "managed")

    assistant = ManagementAssistant(("open report", "export report"))
    chat = FertigChat(assistant)
    commands = (
        'compose "publish report" = "open report" + "export report"',
        'template "send report" from "fill report" recipient=1',
        "correct report step=0",
        'do "send report" recipient="Grace Hopper"',
    )

    for command in commands:
        reply = chat.handle(command, desktop=object(), recorder=object())
        assert reply.route == "desktop"
        assert reply.status == "ok"

    assert assistant.calls == list(commands)
