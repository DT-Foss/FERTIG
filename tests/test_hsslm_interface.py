"""Tests for the constrained HSSLM product interface."""

from __future__ import annotations

from pathlib import Path

import pytest

from fertig.hsslm_interface import (
    AMBIGUOUS,
    RESOLVED,
    UNKNOWN,
    GroundedLanguageInterface,
    HSSLMRuntime,
    SkillDescriptor,
)


class FakeRuntime:
    def __init__(self, scores: dict[str, float] | None = None) -> None:
        self.scores = scores or {}

    def status(self):
        class Status:
            ready = True

        return Status()

    def text_coverage(self, text: str) -> float:
        return 1.0

    def score(self, text: str) -> float:
        return self.scores.get(text, -10.0)

    def choose(self, candidates):
        return max(candidates, key=lambda value: (self.score(value), value))


def test_real_checkpoint_status_counts_tied_weights_once() -> None:
    runtime = HSSLMRuntime()
    assert runtime._engine is None
    status = runtime.status()
    assert status.ready
    assert status.parameter_count == 2_214_368
    assert status.serialized_parameter_count == 2_316_768
    assert status.size_bytes > 8_000_000
    # Status inspection does not instantiate the neural network.
    assert runtime._engine is None


def test_real_candidate_scores_are_request_order_independent() -> None:
    runtime = HSSLMRuntime()
    first = "Smoking causes tar buildup."
    other = "Exercise improves health."
    before = runtime.score(first)
    runtime.score(other)
    after = runtime.score(first)
    assert after == pytest.approx(before, abs=1e-9)


def test_missing_checkpoint_is_a_clean_lazy_fallback(tmp_path: Path) -> None:
    runtime = HSSLMRuntime(tmp_path / "missing.pt", tmp_path / "missing.json")
    status = runtime.status()
    assert not status.ready
    assert "missing" in status.reason
    with pytest.raises(RuntimeError, match="missing"):
        runtime.score("A sufficiently long candidate sentence.")


def test_resolves_natural_german_and_english_requests_to_learned_skills() -> None:
    language = GroundedLanguageInterface()
    skills = (
        SkillDescriptor(
            "monatsbericht herunterladen",
            ("rechnung laden", "download monthly report"),
        ),
        SkillDescriptor("notizen öffnen", ("open notes",)),
    )
    german = language.resolve("Kannst du bitte die Rechnung laden?", skills)
    assert german.status == RESOLVED
    assert german.intent == "do"
    assert german.task == "monatsbericht herunterladen"

    english = language.resolve("please execute open notes", skills)
    assert english.status == RESOLVED
    assert english.task == "notizen öffnen"

    question = language.resolve("How fast can a cheetah run?", skills)
    assert question.intent == "unknown"
    assert question.status == UNKNOWN


def test_teach_can_name_a_new_skill_but_do_cannot_invent_one() -> None:
    language = GroundedLanguageInterface()
    taught = language.resolve("Lerne Rechnung archivieren", ())
    assert taught.status == RESOLVED
    assert taught.intent == "teach"
    assert taught.task == "rechnung archivieren"

    missing = language.resolve("Mach Rechnung archivieren", ())
    assert missing.status == UNKNOWN
    assert missing.skill is None


def test_ambiguous_skill_does_not_cross_action_boundary() -> None:
    language = GroundedLanguageInterface()
    result = language.resolve(
        "mach bericht",
        ("bericht öffnen", "bericht senden"),
    )
    assert result.status == AMBIGUOUS
    assert result.skill is None


def test_constrained_hsslm_can_break_only_a_real_lexical_tie() -> None:
    candidates = {
        "The requested learned task is bericht öffnen.": -4.0,
        "The requested learned task is bericht senden.": -2.0,
    }
    language = GroundedLanguageInterface(FakeRuntime(candidates))
    result = language.resolve("mach bericht", ("bericht öffnen", "bericht senden"))
    assert result.status == RESOLVED
    assert result.task == "bericht senden"
    assert "HSSLM" in result.reason


def test_render_selects_only_fact_preserving_candidates() -> None:
    runtime = FakeRuntime(
        {
            "completed: task: report, steps: 3.": -3.0,
            "Done — task: report, steps: 3.": -1.0,
            "Result — task: report, steps: 3.": -2.0,
        }
    )
    language = GroundedLanguageInterface(runtime)
    output = language.render("completed", {"task": "report", "steps": 3})
    assert output == "Done — task: report, steps: 3."
    assert "report" in output and "3" in output


def test_render_uses_hsslm_for_grounded_quant_and_graph_forms() -> None:
    quant = (
        "The measured answer is 104 km/h; the mechanism is running_at, "
        "with confidence 0.550."
    )
    graph = "From the causal graph: Smoking causes tar buildup."
    runtime = FakeRuntime({quant: -1.0, graph: -0.5})
    language = GroundedLanguageInterface(runtime)

    assert (
        language.render(
            "quantitative fact",
            {
                "message": "Measured answer: 104 km/h (running_at, confidence 0.550).",
                "answer": "104 km/h",
                "mechanism": "running_at",
                "confidence": "0.550",
            },
        )
        == quant
    )
    assert (
        language.render(
            "graph result",
            {
                "message": "Smoking causes tar buildup.",
                "result": "Smoking causes tar buildup.",
            },
        )
        == graph
    )


def test_oov_coverage_prevents_silent_unknown_character_ranking(tmp_path: Path) -> None:
    tokenizer = tmp_path / "bpe.json"
    tokenizer.write_text(
        '{"merges": [], "vocab": {"a": 1, "b": 2}, "itos": {"1": "a", "2": "b"}}'
    )
    runtime = HSSLMRuntime(tmp_path / "missing.pt", tokenizer)
    assert runtime.text_coverage("ab") == 1.0
    assert runtime.text_coverage("ab🙂") == pytest.approx(2 / 3)
