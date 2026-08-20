"""CLI surface for the tangible Apprentice learning curve."""

from __future__ import annotations

import json

from fertig import cli


def test_apprentice_cli_prints_learning_and_control(capsys) -> None:
    assert (
        cli.main(
            [
                "apprentice",
                "--seed",
                "3",
                "--steps",
                "8",
                "--compare-shuffled",
            ]
        )
        == 0
    )
    output = capsys.readouterr().out
    assert "0.0% -> 100.0%" in output
    assert "Ungesehene Kompositionen: 100.0%" in output
    assert "Shuffle-Kontrolle" in output
    assert "0.0%" in output
    assert "Screen + Maus/Tastatur" in output


def test_apprentice_cli_json_is_machine_readable(capsys) -> None:
    assert cli.main(["apprentice", "--steps", "8", "--json"]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["initial_accuracy"] == 0.0
    assert report["final_accuracy"] == 1.0
    assert report["composition_accuracy"] == 1.0
    assert report["unknown_abstained"] is True
