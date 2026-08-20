# FERTIG

**Grounded neuro-symbolic cognitive architecture with a weight-free deterministic core and a constrained neural surface.**

FERTIG combines explicit symbolic state, grounded perception, exact tools, learned executable skills, a small rank-only state-space language module, and replay-verified agent experience in one architecture.

> **A concept is an executable grounded skill. Showing is programming; a sentence is the call.**

The system is not an LLM and not a single-purpose solver. Facts, tools, skills, arithmetic and execution remain explicit and verifiable. Neural components are used where learned ranking or surface form is useful; they do not receive authority to invent facts or bypass verification.

## Architecture

```text
┌─────────────────────────────────────────────────────────────────────┐
│ Interface                    CLI · assistant · chat                  │
├─────────────────────────────────────────────────────────────────────┤
│ Agent-trace learning         replay · process distillation          │
│                              trace learning · experience             │
├─────────────────────────────────────────────────────────────────────┤
│ Language & evidence          worldbook · discourse · form arena     │
│                              lifted walks · verified surface         │
├─────────────────────────────────────────────────────────────────────┤
│ Constrained neural surface   HSSLM / HSSLM-C · rank-only scoring    │
├─────────────────────────────────────────────────────────────────────┤
│ Desktop apprentice           teach · compose · template · correct   │
│                              observe → act → verify                  │
├─────────────────────────────────────────────────────────────────────┤
│ Understanding & solving      intent · bindings · semantic · math    │
│                              miner · solver · tools · code           │
├─────────────────────────────────────────────────────────────────────┤
│ Grounding & perception       quantitative · visual · video · stream │
│                              web gaps · learned categories           │
├─────────────────────────────────────────────────────────────────────┤
│ Weight-free symbolic core    graph · inference · sampler · corpus   │
│                              utterance IR · primitives · grammar     │
└─────────────────────────────────────────────────────────────────────┘
```

The complete module map and system contracts are documented in [docs/architecture.md](docs/architecture.md).

## Design contract

FERTIG is built around a small set of hard rules:

- **Facts are explicit.** Graph edges, measurements, tools, replayable experience and exact arithmetic are the sources of factual state.
- **Abstention beats guessing.** Missing bindings or insufficient evidence produce `UNKNOWN`, `AMBIGUOUS` or no result instead of a fabricated answer.
- **Generation is verified.** Prose is parsed back against its plan; desktop actions are checked against the visible post-state; evidence can be replayed.
- **The neural model ranks; it does not rule.** HSSLM scores grounded candidates and surface forms instead of freely defining system state.
- **Learning closes the loop.** Gaps, demonstrations, streams and agent traces become new executable or replayable structure only after their acceptance checks pass.

## Current measured state

### GSM8K structure solver

The current full-test run reached:

| Metric | Result |
| --- | ---: |
| Correct | **1056 / 1319** |
| Coverage | **80.06%** |
| Incorrect answers | **0** |
| Binding regression tests | **731 passing** |

The run advanced from 715/1319 to 1056/1319 over rounds 315–399 while preserving zero incorrect answers in the full test. Unsolved items remain explicit abstentions. The solver path is only one organ of FERTIG:

```text
question
  → bindings
  → semantic relation graph
  → exact math / structural reductions
  → mined rules
  → answer or abstention
```

### Desktop apprentice

The product path learns named desktop skills by demonstration rather than by coordinate scripting:

```text
teach
  → passive event capture + screenshots
  → visual anchors + state transitions
  → persistent skill

run
  → observe
  → relocate target
  → execute one action
  → verify visible effect
  → continue or stop
```

Skills can be composed, parameterized and corrected at the atomic-step level.

### Grounding and evidence

FERTIG spans several grounding levels: word-to-word graph structure, quantitative anchors, perceptual binding and unsupervised visual categories. The gap loop can turn an unknown concept into sourced causal graph structure. The worldbook stores acted records with replayable provenance and digests.

### Constrained neural surface

The HSSLM family is a small state-space language component. Its production role is constrained scoring: deterministic organs generate and ground candidate meanings or forms; HSSLM ranks among those candidates. The final utterance is checked before release.

### Intelligence compilation

The agent-trace layer records decisions, tool outcomes and replayable file mutations, then reduces them to architecture-neutral process examples. Its long-range target is:

```text
Student = Compile(Recipe, Architecture, Budget)
```

The recipe is the durable object; a particular model checkpoint is one compiled realization of it.

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python3 -m fertig info
python3 -m fertig product-demo
python3 -m fertig assistant
python3 -m pytest tests/ -q
```

Useful entry points:

```bash
# Desktop apprentice
python3 -m fertig desktop-doctor
python3 -m fertig teach "example skill"
python3 -m fertig explain "example skill"
python3 -m fertig do "example skill"

# Symbolic / grounded system
python3 -m fertig graph
python3 -m fertig speech
python3 -m fertig intent -x "explain how smoking affects health"

# Benchmarks and verification
python3 -m fertig bench groundzero
python3 -m fertig bench causal-v2
```

## Repository map

```text
fertig/               core runtime and cognitive modules
erweiterung/          evidence, discourse and live-language extensions
grounding_kernel/     independent-agent grounding experiments
scripts/              training, mining and evaluation utilities
tests/                regression and architecture tests
data/                 small runtime data included by policy
docs/                 architecture and system documentation
```

Large checkpoints, private traces and historical experiment dumps are intentionally kept outside the source repository.

## Research position

FERTIG's core research object is the separation of **truth, skill, plan and form**:

```text
FACT   → explicit grounded state
SKILL  → executable grounded program
PLAN   → composition of facts and skills
FORM   → verified language or interface surface
```

The neural surface can change without redefining the facts. Skills can be learned without rewriting the host's entire model. Execution is checked against the world. Agent experience can be replayed and compiled into new students. The resulting system is a cognitive runtime rather than a monolithic predictor.

## Author

David Tom Foss · 2026
