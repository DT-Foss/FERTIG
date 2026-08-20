# FERTIG current architecture

FERTIG's current integration role is deliberately smaller than the historical
Moonshot framing in older notes. The stable, portable core is an abstaining
unified solver:

```text
bindings → semantic → math → miner → abstain
```

- `bindings` binds numbers to objects, units, and roles before computing;
- `semantic` resolves an entity/relation graph when the language structure is
  sufficient;
- `math` evaluates explicit operation templates with exact fractions;
- `miner` applies only supplied learned rules;
- no engine guesses when its evidence is incomplete.

The HSSLM, desktop, vision, stream, and experience surfaces remain optional
modules. They are not silently required by the exact solver and their model
checkpoints stay outside the repository. IMMER consumes this repository at the
solver boundary and records the order as a pinned contract.
