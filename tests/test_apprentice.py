"""Functional tests for the direct teach -> learn -> do product loop."""

from __future__ import annotations

import numpy as np

from fertig.apprentice import (
    Apprentice,
    OnlineWorldModel,
    RESOLVED,
    RGBGridWorld,
    UNKNOWN,
    run_apprentice_experiment,
    visible_effect,
)


def _teach_directions(agent: Apprentice, world: RGBGridWorld) -> None:
    for name, effect in {
        "right": (3, 0),
        "left": (-3, 0),
        "down": (0, 3),
        "up": (0, -3),
    }.items():
        agent.teach(name, (world.demonstrate(effect),))


def test_world_model_learns_opaque_action_effects_from_rgb() -> None:
    world = RGBGridWorld(seed=1, codebook_variant=4, renderer_offset=(2, -2))
    model = OnlineWorldModel()
    for code in world.action_codes:
        world.reset()
        transition = world.step(code)
        assert np.allclose(visible_effect(transition), world.expected_effect(code))
        assert model.observe(transition)
        assert np.allclose(model.effect(code), world.expected_effect(code))
    assert all(model.predict(code).observations == 1 for code in world.action_codes)


def test_teaching_binds_visible_effect_and_composes_new_instruction() -> None:
    world = RGBGridWorld(seed=2)
    agent = Apprentice()
    _teach_directions(agent, world)
    meaning = agent.interpret("right up right")
    assert meaning.status == RESOLVED
    assert meaning.effect == (6.0, -3.0)
    assert agent.understand("right up right") == meaning
    unknown = agent.interpret("right teleport")
    assert unknown.status == UNKNOWN
    assert unknown.unknown_tokens == ("teleport",)


def test_explore_then_do_unseen_composition_closed_loop() -> None:
    world = RGBGridWorld(seed=3, renderer_offset=(-2, 2))
    agent = Apprentice()
    _teach_directions(agent, world)
    before = agent.plan("right right up")
    assert before.status == UNKNOWN
    agent.explore(world, steps=8)
    plan = agent.plan("right right up", action_codes=world.action_codes)
    assert plan.status == RESOLVED
    assert len(plan.actions) == 3
    result = agent.do(world, "right right up", max_depth=4)
    assert result.success
    assert result.actual_effect == (6.0, -3.0)


def test_meaning_transfers_to_fresh_opaque_codebook() -> None:
    source = RGBGridWorld(seed=4, codebook_variant=0)
    agent = Apprentice()
    _teach_directions(agent, source)
    agent.explore(source, steps=8)
    assert agent.execute(source, "left up", learn=False).success

    target = RGBGridWorld(seed=99, codebook_variant=7, renderer_offset=(2, 1))
    assert set(source.action_codes).isdisjoint(target.action_codes)
    # The words persist; only the new opaque motor alphabet must be explored.
    assert agent.interpret("left up").status == RESOLVED
    assert agent.plan("left up", action_codes=target.action_codes).status == UNKNOWN
    agent.explore(target, steps=8)
    assert agent.execute(target, "left up", learn=False).success


def test_memory_roundtrip_preserves_meanings_models_and_explanation(tmp_path) -> None:
    world = RGBGridWorld(seed=5)
    agent = Apprentice()
    _teach_directions(agent, world)
    agent.explore(world, steps=8)
    path = tmp_path / "apprentice.json"
    agent.save(path)
    loaded = Apprentice.load(path)
    assert loaded.vocabulary == agent.vocabulary
    assert loaded.plan("down right").actions == agent.plan("down right").actions
    explanation = loaded.explain("down right")
    assert "sichtbarer Ziel-Effekt" in explanation
    assert "Demonstration" in explanation
    assert "Plan:" in explanation
    assert loaded.explain("teleport").startswith("UNKNOWN")


def test_memory_rejects_nonfinite_operational_state(tmp_path) -> None:
    path = tmp_path / "poisoned.json"
    path.write_text(
        '{"version":1,"tolerance":0.75,"model":{"1":'
        '{"count":1,"mean":[NaN,0],"m2":[0,0]}},"meanings":{}}'
    )
    try:
        Apprentice.load(path)
    except ValueError as error:
        assert "action-effect" in str(error)
    else:  # pragma: no cover - regression guard
        raise AssertionError("non-finite memory was accepted")


def test_learning_curve_improves_and_shuffle_does_not() -> None:
    learned = run_apprentice_experiment(seed=6, steps=16, checkpoint_every=4)
    shuffled = run_apprentice_experiment(
        seed=6, steps=16, checkpoint_every=4, shuffled_control=True
    )
    assert learned.initial_accuracy == 0.0
    assert learned.final_accuracy == 1.0
    assert learned.composition_accuracy == 1.0
    assert learned.improvement == 1.0
    assert learned.unknown_abstained
    assert learned.curve[-1].model_accuracy == 1.0
    assert learned.curve[-1].mean_uncertainty < learned.curve[0].mean_uncertainty
    assert shuffled.final_accuracy < learned.final_accuracy
    assert shuffled.composition_accuracy < learned.composition_accuracy


def test_experiment_handles_zero_steps_honestly() -> None:
    report = run_apprentice_experiment(seed=7, steps=0)
    assert report.initial_accuracy == report.final_accuracy == 0.0
    assert report.improvement == 0.0
    assert len(report.curve) == 1
