# Phase 1: PI-RL Recipe Foundation - Research

**Researched:** 2026-02-21
**Domain:** LeRobot training config and RL entrypoint routing
**Confidence:** HIGH

## User Constraints

### Locked Decisions (from CONTEXT.md)
- PI-RL must be activated through an explicit top-level recipe field, following VERL-style explicit selection.
- Canonical user-facing recipe value is strict `pi-rl`.
- Actor and learner must use one shared config file path for recipe selection.
- If PI-RL recipe mode is not provided, default behavior remains existing non-PI-RL training path.
- Any actor/learner recipe mismatch is a hard failure.
- Phase 1 allows only XVLA for `pi-rl` recipe mode.
- Using a non-eligible policy with `pi-rl` must hard fail and print the allowed policy list.
- Eligibility validation happens as a preflight check before actor/learner startup.
- Post-phase expansion should be controlled by a policy capability flag.
- Phase 1 exposes both variants: `flow-noise` and `flow-sde`.
- Variant is required when `pi-rl` is selected (no implicit default).
- Tuning surface remains minimal in Phase 1 (must-have knobs only).
- Invalid or missing variant-specific knobs must hard fail with concrete fix hints.
- Invalid config errors must be actionable and include exact field + invalid value + fix guidance.
- Valid config should print a concise preflight summary (recipe, policy, variant, config path).
- Incorrect recipe spelling must fail and suggest canonical `pi-rl`.
- If actor/learner config paths differ, error must include both paths and stop execution.

### Claude's Discretion (from CONTEXT.md)
- Exact naming of minimal variant knobs in Phase 1.
- Preflight summary output format and ordering.
- Exact wording style for validation/error messages.

### Deferred Ideas (from CONTEXT.md)
- None.

## Summary

Phase 1 should be implemented as a recipe-layer extension on top of existing policy typing, not as a new policy class. The current codebase already separates CLI decoding (`parser.wrap`), training config validation (`TrainPipelineConfig`/`TrainRLServerPipelineConfig`), and runtime entrypoints (`lerobot_train.py`, `rl/actor.py`, `rl/learner.py`). This allows PI-RL selection to be introduced in config and validation gates without altering policy factory taxonomy.

The minimal-risk pattern is: add recipe config fields in training config, enforce preflight validation in one shared validator path, and centralize recipe dispatch decisions in RL startup code before algorithm-specific loops. Existing SAC-centric learner internals can remain unchanged in Phase 1; this phase only ensures the system can recognize PI-RL mode, enforce XVLA-only eligibility, and fail fast with actionable messages.

Tests should focus on config parse/validation and runtime selection guards. These are the highest-value checks for RCP-01/02/03 because they prevent ambiguous startup behavior and protect existing non-PI-RL flows.

**Primary recommendation:** Implement PI-RL as validated recipe metadata on `TrainRLServerPipelineConfig`, then gate actor/learner startup with shared preflight checks and targeted tests.

## Standard Stack

### Core
| Library | Purpose | Why Standard |
|---------|---------|--------------|
| `draccus` dataclass config | CLI/config decoding and typed config composition | Existing LeRobot config system already uses it uniformly (`parser.wrap`, config dataclasses) |
| `parser.wrap` | Shared CLI bootstrap for scripts/modules | Single integration point for config loading and plugin behavior |
| `pytest` | Unit/integration validation for config and runtime guards | Existing test harness under `tests/` with RL-focused coverage |

### Supporting
| Component | Purpose | When to Use |
|-----------|---------|-------------|
| `src/lerobot/configs/train.py` | Train config schema and validation hooks | Add recipe fields + preflight validation logic |
| `src/lerobot/rl/actor.py`, `src/lerobot/rl/learner.py` | Runtime startup gates for distributed RL | Enforce recipe compatibility before loop execution |
| `src/lerobot/scripts/lerobot_train.py` | Non-RL train path | Keep default behavior unchanged when recipe is unset |

## Architecture Patterns

### Pattern 1: Validate at config boundary, not deep in runtime loop
**What:** Put PI-RL eligibility and variant checks in config validation or preflight helpers used by both actor and learner.
**Why:** Prevents partial startup and inconsistent actor/learner behavior.

### Pattern 2: Recipe mode orthogonal to policy type
**What:** Keep `policy.type` taxonomy unchanged; route PI-RL through a separate recipe selector.
**Why:** Satisfies requirement to avoid introducing `pi_rl` policy type while enabling XVLA-compatible PI-RL mode.

### Pattern 3: Fail-fast actionable errors
**What:** Validation failures include exact field path, invalid value, and concrete fix.
**Why:** Matches context constraints and reduces misconfiguration loops.

## Don't Hand-Roll

- Do not introduce a new policy class just to represent PI-RL recipe mode.
- Do not split actor/learner recipe interpretation into separate ad-hoc logic paths.
- Do not defer eligibility or variant checks until after runtime threads/processes launch.

## Common Pitfalls

- Adding recipe knobs only to one config path (e.g., learner only) causes actor/learner divergence.
- Letting unknown recipe spellings silently fall back to default behavior makes failures non-obvious.
- Encoding XVLA eligibility as scattered string checks instead of a centralized allow-list increases drift.
- Writing tests only for happy path misses invalid variant and invalid policy guardrails required by this phase.

## Code Examples

### Config surface and validation target
- `src/lerobot/configs/train.py` currently owns train dataclasses and `validate()` hooks for both pipeline variants.

### Shared RL startup checkpoints
- `src/lerobot/rl/actor.py:103` (`actor_cli`) and `src/lerobot/rl/learner.py:106` (`train_cli`) both call wrapped config entrypoints and are suitable for common preflight behavior.

### Keep policy taxonomy untouched
- `src/lerobot/policies/factory.py` should remain responsible for policy type dispatch; recipe dispatch should live outside policy class registration.
