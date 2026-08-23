# FERTIG

**Research trial artifact for grounded cognition and deterministic validation.**

FERTIG studies executable concepts: facts remain explicit, skills remain
executable, plans remain inspectable, and released actions pass deterministic
checks. A constrained neural surface ranks grounded candidates while the
symbolic runtime retains authority over state, arithmetic, evidence, and
execution.

The repository accompanies the research line around `.causal`, deterministic
validation, grounded skill acquisition, and neuro-symbolic composition. It
contains selected trial code, tests, and public measurements. Private traces,
learned state, deployment material, and capability-transfer experiments remain
outside the release surface.

## Research contribution

- **Executable meaning:** a concept can become a named, typed, verified skill.
- **Explicit truth:** graph state, measurements, tools, and receipts remain
  first-class runtime objects.
- **Deterministic release:** language and actions are checked against their
  plans and observed effects.
- **Grounded abstention:** incomplete structures remain unresolved instead of
  becoming fabricated answers.
- **Causal knowledge:** the `.causal` substrate stores explicit relations and
  deterministic inference paths.
- **System composition:** [IMMER](https://github.com/DT-Foss/immer) connects
  FERTIG verification to local frontier inference and causalized weight
  addressing.

## Selected trial evidence

| Trial | Result | Scope |
|---|---:|---|
| Public regression suite | 726 passed, 4 skipped | tracked release tree |
| Desktop product acceptance | 3/3 actions verified | deterministic simulator, persistence and reload included |
| Absolute-coordinate placebo | 0/3 steps completed | same desktop trial |
| GSM8K binding audit | 1,064 correct, 3 wrong, 252 abstentions | full 1,319-item test set |

Detailed public contracts and measurement boundaries are recorded in
[docs/architecture.md](docs/architecture.md) and [CHANGELOG.md](CHANGELOG.md).

## Paper context

- David Tom Foss, **The `.causal` Format: Embedded Deterministic Inference for
  Domain-Agnostic Knowledge Graph Amplification**, IEEE IRI 2026. Conference
  record: [IEEE IRI session E2](https://davidtomfoss.com/service/iri2026-session-e2-nlp-sentiment-multimodal-reasoning/).
- David Tom Foss, **Deterministic Validation for Reliable LLM-Based Causal
  Knowledge Extraction**, ICECET 2026. Record:
  [davidtomfoss.com](https://davidtomfoss.com/talks/deterministic-validation-llm-causal-extraction/).

## Related repositories

- [DT-Foss/immer](https://github.com/DT-Foss/immer)
- [DT-Foss/o1-state](https://github.com/DT-Foss/o1-state)
- [DT-Foss/dotcausal](https://github.com/DT-Foss/dotcausal)

## Author

[David Tom Foss](https://davidtomfoss.com/) ·
[ORCID 0009-0004-0289-7154](https://orcid.org/0009-0004-0289-7154)

Copyright © 2026 David Tom Foss.
