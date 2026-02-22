---
phase: "01"
name: "PI-RL Recipe Foundation"
created: 2026-02-22
status: passed
---

# Phase 1 Verification - PI-RL Recipe Foundation

## Verification Scope

- Phase goal source: `.planning/ROADMAP.md` Phase 1 goal: "Make PI-RL selectable as a training recipe independent of policy type, validated first with XVLA."
- Requirement IDs verified: `RCP-01`, `RCP-02`, `RCP-03` (from `.planning/REQUIREMENTS.md`).
- Evidence sources required by task: code, tests, and git commit history in this repository.

## Overall Status

**passed**

Rationale: all three Phase 1 requirements are implemented in current code, mapped by explicit tests (including RCP-tagged matrix cases), and confirmed by focused local test execution (`29 passed`) plus phase commit history.

## Phase Goal Validation

Goal: **Make PI-RL selectable as a training recipe independent of policy type, validated first with XVLA.**

- PI-RL recipe is selectable via dedicated config fields (`recipe`, `pirl.variant`, variant knobs): `src/lerobot/configs/train.py`.
- Selection is recipe-level (not a new policy taxonomy): matrix assertion explicitly checks `cfg.policy.type != "pi_rl"`: `tests/configs/test_train_config.py`.
- XVLA-first runtime validation is enforced by preflight allowlist (`PI_RL_PHASE1_ALLOWED_POLICIES = ("xvla",)`): `src/lerobot/configs/train.py`.

Result: goal conditions are satisfied in current code + tests.

## Requirement-by-Requirement Verification

### RCP-01 - Enable PI-RL independently of policy type selection

**Status:** passed

Evidence:
- Recipe abstraction exists separately from policy types: `RecipeType.PI_RL = "pi-rl"` in `src/lerobot/configs/types.py`.
- Training config carries recipe and PI-RL knobs outside policy taxonomy (`recipe`, `pirl`): `src/lerobot/configs/train.py`.
- Acceptance matrix verifies policy taxonomy is unchanged (`cfg.policy.type == "xvla"` and `!= "pi_rl"`) under PI-RL recipe: `tests/configs/test_train_config.py`.
- Commit lineage:
  - `d4ab133a` added PI-RL recipe config surface (`src/lerobot/configs/train.py`, `src/lerobot/configs/types.py`).
  - `db222469`, `35987f04` added/tightened acceptance matrix assertions.

### RCP-02 - Run PI-RL recipe with flow-matching policies (XVLA first)

**Status:** passed

Evidence:
- Runtime preflight enforces XVLA-only eligibility in Phase 1 (`PI_RL_PHASE1_ALLOWED_POLICIES = ("xvla",)` + hard-fail on others): `src/lerobot/configs/train.py`.
- Train entrypoint routes PI-RL away from offline `lerobot-train` with explicit learner/actor guidance: `src/lerobot/scripts/lerobot_train.py`.
- RL tests cover allow/deny matrix for XVLA vs SAC under PI-RL (`RCP-02`): `tests/rl/test_actor_learner.py`.
- Routing behavior tests confirm PI-RL block + non-PI-RL default path preserved: `tests/scripts/test_lerobot_train_recipe_routing.py`.
- Commit lineage:
  - `efb2834f` centralized preflight eligibility checks.
  - `209b2b4d` added train routing guardrails.
  - `d33f3313` and `db222469` added startup/acceptance coverage.

### RCP-03 - Configure PI-RL variant behavior via structured fields

**Status:** passed

Evidence:
- Structured variant types and allowed values are defined (`flow-noise`, `flow-sde`): `src/lerobot/configs/types.py`.
- Structured PI-RL variant configs exist (`PIRLFlowNoiseConfig`, `PIRLFlowSDEConfig`) with validation for required knobs and bounds: `src/lerobot/configs/train.py`.
- Tests validate both valid variants and invalid/missing knobs with actionable errors: `tests/configs/test_train_config.py`, `tests/configs/test_train_recipe_validation.py`.
- Acceptance matrix includes explicit `RCP-03` case for `flow-sde`: `tests/configs/test_train_config.py`.
- Commit lineage:
  - `d4ab133a` introduced variant config surface.
  - `c024a6e8`, `b383cfeb` added validation and variant-focused tests.

## Test Execution Evidence (Current Repo State)

Command executed:

```bash
uv run --extra test --extra dev pytest -sv \
  tests/configs/test_train_config.py \
  tests/rl/test_actor_learner.py \
  tests/scripts/test_lerobot_train_recipe_routing.py \
  tests/rl/test_learner_service.py
```

Observed result:
- `29 passed in 3.84s`
- Includes Phase 1-critical checks: recipe parsing/validation, XVLA runtime guard, train routing, actor/learner config metadata sync.

## Git History Evidence

Verified phase commits touching implementation/tests for this goal:

- `d4ab133a` feat(01-01): add PI-RL recipe config surface
- `c024a6e8` test(01-01): enforce fail-fast PI-RL validation and coverage
- `efb2834f` feat(01-02): centralize PI-RL preflight eligibility checks
- `592c0c8c` feat(01-02): hard-fail actor learner config source mismatch
- `209b2b4d` feat(01-02): keep default train path while routing pi-rl mode
- `b383cfeb` test(01-03): add PI-RL config recipe validation coverage
- `d33f3313` test(01-03): cover RL PI-RL startup guard behavior
- `db222469` test(01-03): add Phase 1 acceptance matrix coverage
- `35987f04` test(01-03): tighten matrix assertions for typed policy access

## Gaps / Human Follow-up

None found for Phase 1 scope (`RCP-01`/`RCP-02`/`RCP-03`).
