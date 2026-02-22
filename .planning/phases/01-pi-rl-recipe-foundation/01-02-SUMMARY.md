---
phase: 01-pi-rl-recipe-foundation
plan: 02
subsystem: rl
tags: [pi-rl, xvla, preflight, actor-learner, config-sync]
requires:
  - phase: 01-pi-rl-recipe-foundation
    provides: PI-RL canonical recipe parsing and variant validation foundation
provides:
  - Centralized PI-RL runtime preflight with XVLA-only eligibility enforcement
  - Actor/learner config-path and config-hash consistency hard-fail guard
  - Train entrypoint PI-RL routing guard preserving default non-PI-RL behavior
affects: [01-03, phase-2-learner-branch, phase-3-runtime-validation]
tech-stack:
  added: [none]
  patterns: [shared-recipe-preflight-context, tensor-metadata-config-sync, fail-fast-runtime-gating]
key-files:
  created:
    - tests/rl/test_recipe_config_sync.py
    - tests/scripts/test_lerobot_train_recipe_routing.py
  modified:
    - src/lerobot/configs/train.py
    - src/lerobot/rl/actor.py
    - src/lerobot/rl/learner.py
    - src/lerobot/scripts/lerobot_train.py
    - tests/configs/test_train_recipe_validation.py
key-decisions:
  - "PI-RL eligibility and startup summary are enforced through shared train-config preflight helpers used by actor, learner, and train entrypoints."
  - "Actor/learner consistency uses existing parameter stream payloads with reserved uint8 metadata tensors for config path/hash, avoiding protobuf changes."
patterns-established:
  - "Recipe preflight context as single source of truth for runtime gating and concise startup logs."
  - "Distributed config consistency should fail before actor accepts learner parameter updates."
requirements-completed: [RCP-01, RCP-02]
duration: 2 min
completed: 2026-02-22
---

# Phase 01 Plan 02: Runtime Recipe Dispatch and Config Sync Summary

**PI-RL runtime dispatch is now centralized and XVLA-gated, with actor/learner config-source mismatch hard-failing before parameter updates are accepted.**

## Performance

- **Duration:** 2 min
- **Started:** 2026-02-21T21:42:13-05:00
- **Completed:** 2026-02-22T02:44:45Z
- **Tasks:** 3
- **Files modified:** 7

## Accomplishments
- Added centralized runtime preflight helpers in train config layer to enforce `recipe=pi-rl` eligibility as XVLA-only and emit deterministic startup summaries.
- Enforced actor/learner config consistency via encoded `(config_path, config_hash)` metadata in streamed parameter payloads and explicit hard-fail errors containing both sides.
- Kept non-PI-RL `lerobot-train` behavior intact while adding clean PI-RL routing guardrails that direct users to RL learner/actor entrypoints.

## Task Commits

Each task was committed atomically:

1. **Task 1: Add centralized PI-RL eligibility and startup summary preflight** - `efb2834f` (feat)
2. **Task 2: Enforce actor/learner config path consistency and hard-fail mismatch** - `592c0c8c` (feat)
3. **Task 3: Preserve non-PI-RL train script behavior and PI-RL routing** - `209b2b4d` (feat)

**Additional auto-fix:** `d81029d2` (fix) for strict typing compatibility in new RL config-sync tests.

## Files Created/Modified
- `src/lerobot/configs/train.py` - Added shared runtime preflight context, XVLA PI-RL eligibility gate, deterministic preflight logging helpers.
- `src/lerobot/rl/learner.py` - Applied preflight summary and encoded learner config metadata into parameter payloads.
- `src/lerobot/rl/actor.py` - Decoded learner config metadata and hard-failed on path/hash mismatch before policy load.
- `src/lerobot/scripts/lerobot_train.py` - Preserved default path and blocked `recipe=pi-rl` in offline train with explicit RL runtime guidance.
- `tests/configs/test_train_recipe_validation.py` - Added runtime preflight acceptance/rejection tests for XVLA-only eligibility.
- `tests/rl/test_recipe_config_sync.py` - Added metadata propagation and mismatch hard-failure tests.
- `tests/scripts/test_lerobot_train_recipe_routing.py` - Added train routing tests for PI-RL block and default non-PI-RL pass-through.

## Decisions Made
- Use train-config preflight helpers as runtime source of truth for recipe + policy eligibility across entrypoints.
- Use reserved transport metadata tensor keys in existing state-dict bytes stream to avoid any protobuf contract change.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Strict typing failures in new RL sync tests**
- **Found during:** Task 2 verification
- **Issue:** New sync tests failed strict basedpyright diagnostics due incompatible helper typing.
- **Fix:** Added precise cast boundaries for metadata payload and dummy policy test adapter.
- **Files modified:** tests/rl/test_recipe_config_sync.py
- **Verification:** `uv run pytest -sv tests/rl/test_recipe_config_sync.py tests/scripts/test_lerobot_train_recipe_routing.py`
- **Committed in:** d81029d2

---

**Total deviations:** 1 auto-fixed (1 bug)
**Impact on plan:** No scope creep; fix was required to keep added validation tests clean and stable.

## Issues Encountered
- Basedpyright reports a large existing error baseline in `src/lerobot/rl/actor.py`, `src/lerobot/rl/learner.py`, and `src/lerobot/scripts/lerobot_train.py` unrelated to this plan's functional behavior; plan-specific tests and new/updated test files passed cleanly.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- Phase 01-03 can build directly on centralized preflight and config-sync guards to expand focused compatibility tests.
- No blocker introduced by this plan; runtime route and fail-fast surfaces are in place.

---
*Phase: 01-pi-rl-recipe-foundation*
*Completed: 2026-02-22*
