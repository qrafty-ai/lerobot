---
phase: 01-pi-rl-recipe-foundation
plan: 01
subsystem: config
tags: [pi-rl, config, parser, validation, draccus, pytest]
requires:
  - phase: 00-project-initialization
    provides: base LeRobot planning scaffold and phase-1 scope
provides:
  - PI-RL recipe and variant config surface in train config
  - fail-fast parser and config validation errors with fix hints
  - focused positive/negative tests for recipe parse and validation behavior
affects: [phase-1-plan-02, phase-1-plan-03, rl-entrypoints]
tech-stack:
  added: []
  patterns: [recipe-level activation orthogonal to policy type, actionable preflight validation]
key-files:
  created: [tests/configs/test_train_recipe_validation.py]
  modified: [src/lerobot/configs/types.py, src/lerobot/configs/train.py, src/lerobot/configs/parser.py]
key-decisions:
  - "Use strict canonical recipe string `pi-rl` with parser preflight rejection for non-canonical spellings."
  - "Require PI-RL variant and variant-specific knobs only when `recipe=pi-rl`; leave default behavior unchanged when recipe is unset."
patterns-established:
  - "Validation errors include field path, invalid value, and concrete fix guidance."
  - "Recipe selection remains independent from policy taxonomy (no new policy type added)."
requirements-completed: [RCP-01, RCP-03]
duration: 2 min
completed: 2026-02-22
---

# Phase 1 Plan 01: PI-RL recipe config and validation Summary

**PI-RL is now selectable via explicit recipe metadata with strict variant validation and deterministic actionable errors, while preserving default non-PI-RL behavior when recipe is unset.**

## Performance

- **Duration:** 2 min
- **Started:** 2026-02-22T02:28:25Z
- **Completed:** 2026-02-22T02:29:48Z
- **Tasks:** 2
- **Files modified:** 4

## Accomplishments
- Added recipe-level PI-RL fields and typed variant enums in training config surface.
- Implemented fail-fast validation for canonical recipe spelling, required variant, and required variant-specific knobs.
- Added focused tests covering default parse behavior, both PI-RL variants, and negative validation/preflight cases.

## Task Commits

Each task was committed atomically:

1. **Task 1: Add explicit PI-RL recipe and variant fields to train config** - `d4ab133a` (feat)
2. **Task 2: Implement fail-fast recipe preflight validation with actionable errors** - `c024a6e8` (test)
3. **Verification fix: clear changed-file LSP error gate** - `0ce81030` (fix)

**Plan metadata:** recorded in the plan-completion docs commit.

## Files Created/Modified
- `src/lerobot/configs/types.py` - Adds canonical recipe/variant enums and PI-RL allowed-variant constants.
- `src/lerobot/configs/train.py` - Adds `recipe`/`pirl` config fields plus strict PI-RL validation helpers.
- `src/lerobot/configs/parser.py` - Adds parser preflight guard for non-canonical recipe values.
- `tests/configs/test_train_recipe_validation.py` - Adds parse and negative validation coverage for PI-RL recipe behavior.

## Decisions Made
- Enforced canonical `pi-rl` spelling at parser preflight with explicit correction hints.
- Made PI-RL variant and knobs mandatory only under `recipe=pi-rl`, leaving all non-PI-RL defaults untouched.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Local test execution dependencies were unavailable in the default environment**
- **Found during:** Task 2 (verification)
- **Issue:** `pytest` path and runtime packages were missing for this workspace.
- **Fix:** Ran tests through `uv run --python 3.10 python -m pytest ...` and installed `pytest` into `.venv`.
- **Files modified:** none
- **Verification:** `uv run --python 3.10 python -m pytest -sv tests/configs/test_train_recipe_validation.py`
- **Committed in:** n/a (environment only)

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** No scope creep; deviation only affected local verification execution path.

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Ready for `01-02-PLAN.md` recipe dispatch wiring.
- Phase 1 now has recipe-level PI-RL validation baseline in place.

---
*Phase: 01-pi-rl-recipe-foundation*
*Completed: 2026-02-22*
