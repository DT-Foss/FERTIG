# FERTIG Architecture

FERTIG is a grounded neuro-symbolic cognitive architecture built around a deterministic symbolic core, explicit provenance, executable skills, constrained neural ranking and closed-loop verification.

Its central idea is operational rather than metaphorical:

> **A concept is an executable grounded skill. Showing is programming; a sentence is the call.**

## 1. System layers

### Layer 1 — Weight-free symbolic core

The bottom layer stores and manipulates explicit structure without learned embeddings as the source of truth.

Primary modules include:

- `.causal` graph I/O and graph state;
- deterministic inference and chained relation traversal;
- contraction-controlled sampling and corpus statistics;
- explicit primitives and semantic relations;
- utterance IR with plan → prose → plan verification;
- grammar rules and structural guards.

The core can be seeded for deterministic form generation while factual graph operations and arithmetic remain exact.

### Layer 2 — Grounding and perception

Symbols are connected to non-symbolic evidence through multiple grounding paths:

- quantitative values and units;
- text/image binding;
- unsupervised visual signatures and categories;
- video motion and scene features;
- O(1) stream learning with prototype updates;
- gap-driven web acquisition and causal triple extraction.

New graph structure enters the world model only through measured or sourced evidence.

### Layer 3 — Understanding and solving

Natural-language tasks are transformed into executable semantic structure.

```text
input
  → intent / parse
  → bindings
  → semantic entity-relation graph
  → exact math / structural templates
  → mined reductions
  → result or abstention
```

The binding system attaches numbers to objects, units and roles before computation. Fractions are kept exact where arithmetic requires it. No engine is allowed to guess when its bindings are incomplete.

The current GSM8K full-test result is **1056/1319 = 80.06% correct with 0 incorrect answers**. The corresponding binding regression suite contains **731 passing tests**. Remaining items are explicit abstentions rather than forced answers.

### Layer 4 — Desktop apprentice

The desktop product path learns executable skills by observation.

```text
teach
  → passive event stream + screenshots
  → visual anchor model
  → persistent named skill

execute
  → observe
  → relocate
  → perform one action
  → observe post-state
  → verify effect
  → continue or stop
```

Skills support composition, parameterized text slots and atomic correction. The system reasons over visual state transitions rather than replaying absolute coordinates.

### Layer 5 — Constrained neural surface

HSSLM is a small hierarchical state-space language component. It is deliberately subordinate to grounded state.

Its production role is constrained scoring:

1. deterministic organs produce grounded candidate skills, answers or phrasings;
2. HSSLM scores only those candidates;
3. the selected form is verified against the plan before release.

The neural model therefore improves surface selection without becoming the authority for facts or actions.

### Layer 6 — Language and evidence

The extension layer turns grounded state into coherent discourse while keeping provenance available.

It contains:

- replayable worldbook evidence;
- discourse composition;
- form ranking and information-density measurements;
- lifted graph walks;
- verified surface generation;
- independent-agent grounding experiments.

Claims can be coupled to receipts and digests, and generated prose can be rejected if it no longer matches the underlying plan.

### Layer 7 — Agent-trace learning

Observed agent work is converted into replay-grounded process data.

The trace stack records:

- event streams;
- tool lifecycle joins;
- deterministic file mutation replay;
- process-distillation examples;
- architecture-neutral decision fingerprints;
- append-only experience storage.

The target abstraction is:

```text
Student = Compile(Recipe, Architecture, Budget)
```

The durable object is the learned recipe. HSSLM, a small Transformer, an SSM or a hybrid runtime can be treated as different compiled realizations.

### Layer 8 — Interface

The CLI, assistant and chat surfaces expose the underlying system without changing its authority structure. Natural language is an invocation surface over grounded state and skills, not a replacement for them.

## 2. Core contracts

### Truth

Facts must originate from explicit graph state, measurements, sourced evidence, replayable experience or exact tools.

### Abstention

Insufficient structure produces an explicit failure state rather than a guessed result.

### Verification

- prose is parsed back against its plan;
- desktop actions are checked against the visible post-state;
- replayable evidence can be re-executed;
- benchmark changes are recorded as measurable ledger entries.

### Neural authority

Learned neural components may rank or compress grounded candidates. They do not silently redefine factual state or bypass execution checks.

### Closed loops

The architecture repeatedly closes observation and learning loops:

```text
observe → act → verify → replan
measure → find gap → acquire evidence → integrate → remeasure
trace → replay → distill → compile → evaluate
```

## 3. Major end-to-end paths

### Grounded language

```text
causal graph
  → graph walk / plan
  → candidate forms
  → constrained neural ranking
  → utterance verification
  → released text
```

### Desktop skill

```text
demonstration
  → visual transition model
  → named skill
  → natural-language invocation
  → observe / act / verify loop
```

### Mathematical reasoning

```text
question
  → binding graph
  → semantic relation graph
  → exact operations
  → structural reduction
  → answer or abstention
```

### Gap learning

```text
unknown concept
  → source queries
  → causal extraction
  → confidence aggregation
  → world graph merge
  → newly grounded capability
```

### Process learning

```text
agent trace
  → replayable experience
  → decision / outcome representation
  → process recipe
  → compiled student
```

## 4. Determinism model

Determinism is a property of individual paths rather than a claim that every physical interaction is identical.

- graph lookup, arithmetic, bindings and solver routing are deterministic;
- corpus and sampling paths are seedable;
- neural training is stochastic, while inference can be seeded and constrained;
- desktop execution interacts with a real changing environment, so each action is re-observed and verified;
- benchmark protocols use fixed arguments and recorded fixtures.

## 5. System boundary

FERTIG is not defined by any single benchmark, model or user interface. The solver, HSSLM, desktop apprentice, grounding layers and trace compiler are organs inside one cognitive runtime.

The stable separation is:

```text
FACT   explicit grounded state
SKILL  executable grounded program
PLAN   composition of facts and skills
FORM   verified language / interface realization
```

This separation is what allows the system to add learned language, demonstrations and model students without handing factual or execution authority to a single end-to-end neural predictor.
