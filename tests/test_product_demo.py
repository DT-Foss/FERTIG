"""Acceptance tests for the deterministic FERTIG product demonstration."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from fertig import cli
from fertig.product_demo import ProductDemoReport, run_product_demo


def test_product_demo_runs_full_persisted_shifted_workflow(tmp_path: Path) -> None:
    runtime_value = "Katherine Johnson, Flight Research Division"

    report = run_product_demo(tmp_path, runtime_value=runtime_value)

    assert isinstance(report, ProductDemoReport)
    assert report.success
    assert report.reloaded_before_execution
    assert report.counts.atomic_tasks == 3
    assert report.counts.composed_workflows == 1
    assert report.counts.templates == 1
    assert report.counts.taught_steps == 3
    assert report.counts.executed_steps == 3
    assert report.counts.verified_steps == 3
    assert report.counts.persisted_stores == 2
    assert Path(report.task_store).is_file()
    assert Path(report.template_store).is_file()

    assert [action.kind for action in report.actions] == ["click", "text", "click"]
    assert all(action.verified for action in report.actions)
    assert report.actions[1].text == runtime_value
    assert report.actions[0].x is not None and 74 <= report.actions[0].x < 100
    assert report.actions[0].y is not None and 8 <= report.actions[0].y < 26
    assert report.actions[2].x is not None and 8 <= report.actions[2].x < 36
    assert report.actions[2].y is not None and 52 <= report.actions[2].y < 69

    assert not report.baseline.success
    assert report.baseline.completed_steps == 0
    assert report.baseline.attempted_actions == 3
    assert report.baseline.wrong_clicks == 2
    assert "background" in report.baseline.reason

    assert [reply.stage for reply in report.replies] == [
        "teach:open composer",
        "teach:fill recipient",
        "teach:send message",
        "compose",
        "template",
        "execute",
    ]
    assert all(reply.status == "ok" for reply in report.replies)
    assert report.replies[-1].surface == "chat"
    assert report.replies[-1].intent_or_route == "desktop"
    assert report.replies[-1].data["values"] == {"recipient": runtime_value}


def test_product_demo_report_round_trips_as_plain_json(tmp_path: Path) -> None:
    report = run_product_demo(tmp_path)

    encoded = report.to_json(indent=None)
    decoded = json.loads(encoded)

    assert decoded == report.to_dict()
    assert decoded["success"] is True
    assert decoded["actions"][1]["text"] == "Dr. Katherine Johnson"
    assert decoded["replies"][-1]["surface"] == "chat"
    assert json.dumps(report.to_dict(), allow_nan=False)


def test_product_demo_never_overwrites_existing_store(tmp_path: Path) -> None:
    first = run_product_demo(tmp_path)
    original = Path(first.task_store).read_bytes()

    with pytest.raises(FileExistsError, match="refuses to replace"):
        run_product_demo(tmp_path)

    assert Path(first.task_store).read_bytes() == original


@pytest.mark.parametrize("runtime_value", ["", None])
def test_product_demo_rejects_empty_runtime_value(
    tmp_path: Path, runtime_value: object
) -> None:
    with pytest.raises(ValueError, match="non-empty"):
        run_product_demo(tmp_path, runtime_value=runtime_value)  # type: ignore[arg-type]


def test_product_demo_is_public_cli_with_human_and_json_reports(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    human_dir = tmp_path / "human"
    assert cli.main(["product-demo", "--output", str(human_dir)]) == 0
    human = capsys.readouterr().out
    assert "FERTIG Produktbeweis" in human
    assert "3/3 Schritte sichtbar verifiziert" in human
    assert "Koordinaten-Replay: gescheitert" in human
    assert "Ergebnis: PASS" in human

    json_dir = tmp_path / "json"
    assert (
        cli.main(
            [
                "product-demo",
                "--output",
                str(json_dir),
                "--runtime-value",
                "Grace Hopper",
                "--json",
            ]
        )
        == 0
    )
    payload = json.loads(capsys.readouterr().out)
    assert payload["success"] is True
    assert payload["runtime_value"] == "Grace Hopper"
    assert payload["counts"]["verified_steps"] == 3
    assert payload["baseline"]["success"] is False
    assert payload["actions"][1]["text"] == "Grace Hopper"
