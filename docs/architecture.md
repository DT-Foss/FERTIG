# FERTIG Architecture

FERTIG is a grounded cognitive runtime. It represents facts as explicit state,
concepts as executable skills, plans as inspectable compositions and language
as a verified surface.

> **A concept is an executable grounded skill. Showing is programming; a
> sentence is the call.**

## 1. Authority model

Every output follows a fixed authority order:

```text
measurement / source / graph / replay / exact tool
  -> factual state
  -> executable plan
  -> candidate action or form
  -> postcondition or round-trip verification
  -> released result
```

The runtime keeps four objects distinct:

| Object | Representation | Authority |
| --- | --- | --- |
| Fact | graph edge, measurement, receipt, replay or tool result | Defines world state |
| Skill | named executable program with inputs and checks | Defines available action |
| Plan | ordered composition of facts and skills | Defines intended execution |
| Form | prose or interface realization | Communicates the verified plan |

The neural surface ranks candidates inside this structure. Facts, arithmetic,
desktop authority and release verdicts stay in their dedicated engines.

## 2. System map

```text
┌─────────────────────────────────────────────────────────────────────┐
│ Interface            CLI · assistant · chat                         │
├─────────────────────────────────────────────────────────────────────┤
│ Experience           event joins · replay · distillation · ledger   │
├─────────────────────────────────────────────────────────────────────┤
│ Language             utterance IR · candidate forms · HSSLM ranking │
├─────────────────────────────────────────────────────────────────────┤
│ Action               teach · compose · template · correct · execute │
├─────────────────────────────────────────────────────────────────────┤
│ Solving              intent · bindings · semantic graph · exact math│
├─────────────────────────────────────────────────────────────────────┤
│ Grounding            quantities · images · video · streams · gaps   │
├─────────────────────────────────────────────────────────────────────┤
│ Causal substrate     .causal I/O · inference · walks · provenance   │
└─────────────────────────────────────────────────────────────────────┘
```

### Causal substrate

Public modules:

- `fertig/_vendor/dotcausal/io.py`
- `fertig/_vendor/dotcausal/core.py`
- `fertig/_vendor/dotcausal/inference.py`
- `fertig/pipeline.py`
- `fertig/inference.py`
- `fertig/sampler.py`
- `fertig/state_init.py`
- `fertig/bphm.py`

This plane loads and writes `.causal` graphs, verifies their checksum, resolves
entity identifiers, computes deterministic inference chains and exposes exact
graph edges to the rest of FERTIG. Sampling controls graph-walk form; the edge
set remains the factual source.

### Grounding

Public modules:

- `fertig/grounding.py`
- `fertig/quant.py`
- `fertig/vision.py`
- `fertig/video.py`
- `fertig/stream.py`
- `fertig/gaps.py`
- `fertig/sources.py`
- `fertig/scrape.py`

This plane binds symbols to quantities, perceptual signatures, motion, stream
prototypes and sourced graph additions. The gap loop turns an unresolved target
into source queries, extracted causal structure and a merged world graph.

### Understanding and solving

Public modules:

- `fertig/intent.py`
- `fertig/bindings.py`
- `fertig/semantic.py`
- `fertig/math.py`
- `fertig/relations.py`
- `fertig/solver.py`
- `fertig/tools.py`
- `fertig/miner.py`
- `fertig/mined.py`

The binding engine assigns numbers to objects, units and roles. The semantic
engine turns relations into an executable graph. Arithmetic uses
`fractions.Fraction` for exact intermediate values. Structural solvers and
mined reductions extend the route while preserving the same answer contract.

```text
question
  -> intent
  -> quantity/object/role bindings
  -> entity-relation graph
  -> exact operation chain
  -> answer | abstention
```

### Desktop apprentice

Public modules:

- `fertig/assistant.py`
- `fertig/chat.py`
- `fertig/desktop.py`
- `fertig/desktop_agent.py`
- `fertig/screen_model.py`
- `fertig/skill_slots.py`
- `fertig/macos_recording.py`
- `fertig/product_demo.py`

Teach-by-showing records state transitions and action primitives. A skill store
persists named atomic tasks; composition builds workflows; templates turn text
steps into typed runtime slots; correction replaces a selected atomic step.

```text
teach
  -> capture pre-state
  -> record action
  -> capture post-state
  -> learn visual transition
  -> persist named skill

execute
  -> resolve one named skill
  -> observe current state
  -> relocate visual target
  -> perform one action
  -> observe post-state
  -> verify effect
  -> continue or stop
```

OS input becomes reachable after successful intent resolution and stored-skill
resolution. Ambiguous targets terminate before the action adapter receives an
input command.

### Language surface

Public modules:

- `fertig/utterance.py`
- `fertig/form_engine.py`
- `fertig/hsslm_interface.py`
- `fertig/hsslm/`
- `fertig/grammar.py`
- `fertig/corpus.py`
- `fertig/pattern_bank.py`

Utterance IR carries subject, relation, object, confidence, source, prose and a
verification verdict. The plan produces candidate forms; each candidate is
parsed back and checked against the graph-backed plan.

```text
grounded edges
  -> utterance plan
  -> candidate forms
  -> optional HSSLM ranking
  -> semantic round-trip
  -> released prose
```

The repository tracks the HSSLM architecture and BPE tokenizer. Installed
checkpoints are explicit runtime inputs, and `fertig hsslm-status` reports
their readiness, serialized size and parameter count.

### Experience and compilation

Public modules:

- `fertig/pi_trace.py`
- `fertig/pi_experience.py`
- `fertig/pi_artifact_replay.py`
- `fertig/agent_experience.py`
- `fertig/trace_learning.py`
- `fertig/process_distillation.py`

This plane joins agent events with tool outcomes, records file effects,
replays accepted mutations and reduces the trace into provider-neutral process
examples. Append-only experience records preserve the evidence needed to audit
each learned recipe.

```text
agent event stream
  -> tool lifecycle join
  -> effect receipt
  -> deterministic replay
  -> process example
  -> reusable recipe
```

### Evidence and discourse extensions

The tracked `erweiterung/` package adds:

- worldbook evidence with replayable receipts;
- discourse composition over grounded state;
- form-arena scoring;
- lifted graph walks;
- live-language training experiments;
- a pinned external-world snapshot for deterministic replay.

These modules consume the same graph, plan and verification contracts as the
main package.

## 3. The FERTIG `.causal` contract

A FERTIG `.causal` file contains:

1. a deduplicated entity dictionary;
2. explicit trigger -> mechanism -> outcome triplets;
3. confidence and provenance fields;
4. inference rules;
5. semantic clusters;
6. knowledge gaps;
7. section offsets and an integrity checksum.

`CausalReader.get_all_triplets(include_inferred=False)` returns the stored
facts. `include_inferred=True` adds deterministic rule-derived chains and
caches that inference result for the reader lifetime. Graph search runs over
resolved entity text and exposes whether each result is explicit or inferred.

The format serves semantic knowledge inside FERTIG. Its graph connects concepts,
evidence and outcomes.

## 4. FERTIG and IMMER

[IMMER](https://github.com/DT-Foss/immer) integrates FERTIG into a local,
streamed-model runtime and applies the same causal-file principle to model
access:

```text
FERTIG
  semantic destinations -> graph edges -> grounded plans -> exact certificates

IMMER
  tensor destinations -> exact byte ranges -> causal rails -> local cache
  official expert route -> Markov transition evidence -> next-range prefetch
```

IMMER's causalized local bundle keeps safetensor payloads immutable and implants
their structural wiring into the bundle. The reader reaches named tensor ranges
through that wiring. Its Markov router learns empirical transitions between
official expert selections and orders prefetch; the checkpoint router remains
the source of the executed expert set.

FERTIG enters this architecture as the grounding, skill and certification
organ. The two repositories share the causal design pattern and keep their file
semantics precise:

| Repository | Causal object | Addressed destination |
| --- | --- | --- |
| FERTIG | knowledge graph | entity, mechanism, outcome, evidence |
| IMMER | causalized model bundle | shard, tensor, byte range, route transition |

## 5. Determinism and replay

Deterministic paths:

- `.causal` integrity checks, graph loading and rule inference;
- graph lookup and seeded walks;
- intent parsing and stored-skill resolution;
- binding, relation execution and fractional arithmetic;
- plan-to-prose round-trip checks;
- zero-OS product simulation;
- canonical experience serialization and artifact replay.

Environment-bound paths re-observe their state:

- desktop execution checks every visible transition;
- source acquisition stores provenance with accepted graph additions;
- neural ranking consumes a named checkpoint and tokenizer;
- benchmark downloads resolve into a local dataset cache.

This split makes every release verdict reproducible at the layer where the
decision is made.

## 6. Verified release state

The clean tracked tree was measured on 2026-08-23:

| Gate | Evidence |
| --- | ---: |
| Public pytest suite | 726 passed, 4 skipped in 89.37 s |
| Product demo | 3 atomic skills, 1 composition, 1 template |
| Product execution | 3/3 relocated actions verified after reload |
| Absolute-coordinate control | 0/3 steps completed |
| GSM8K binding pass | 1,064 correct, 3 wrong, 252 abstentions, 0 crashes |
| GSM8K answered precision | 99.72% |

The product demo runs through public assistant and chat surfaces, persists both
stores, reloads them and executes against a shifted interface. The coordinate
control replays original coordinates against the same shift.

The GSM8K audit processes all 1,319 official test questions through
`fertig.bindings.solve`, extracts each reference terminal answer with
`fertig.math.gold_answer` and counts every emitted mismatch as wrong.

## 7. Public entry points

```bash
python -m fertig --help
python -m fertig info
python -m fertig graph smoking -n 5
python -m fertig product-demo --json
python -m fertig assistant
python -m fertig desktop-doctor --json
python -m pytest tests -q
```

The CLI parser in `fertig/cli.py` is the canonical command inventory.

## 8. Research links

- [FERTIG](https://github.com/DT-Foss/FERTIG)
- [IMMER](https://github.com/DT-Foss/immer)
- [o1-state](https://github.com/DT-Foss/o1-state)
- [dotcausal](https://github.com/DT-Foss/dotcausal)
- [The `.causal` Format](https://doi.org/10.5281/zenodo.18326222)
- [Universal GOE-Ginibre phase transition](https://doi.org/10.13140/RG.2.2.19450.45765)
- [Switch Transformers](https://jmlr.org/papers/v23/21-0998.html)
- [GLaM](https://proceedings.mlr.press/v162/du22c.html)
- [Next generation reservoir computing](https://doi.org/10.1038/s41467-021-25801-2)
- [David Tom Foss](https://davidtomfoss.com/)
- [ORCID 0009-0004-0289-7154](https://orcid.org/0009-0004-0289-7154)
