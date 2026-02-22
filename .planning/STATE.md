# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-02-21)

**Core value:** Enable reliable online RL fine-tuning of flow-based VLA policies in LeRobot while preserving existing RL stability and operability.
**Current focus:** Phase 2 - Learner PI-RL Training Path

## Current Position

Phase: 2 of 4 (Learner PI-RL Training Path)
Plan: 0 of 3
Status: Context gathered, ready for planning
Last activity: 2026-02-22 - Captured 02-CONTEXT decisions for smoke-first run profile and learner/actor launch path

Progress: [████░░░░░░] 32%

## Performance Metrics

**Velocity:**
- Total plans completed: 3
- Average duration: 3 min
- Total execution time: 0.15 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 1 | 3/3 | 9 min | 3 min |
| 2 | 0/3 | - | - |
| 3 | 0/3 | - | - |
| 4 | 0/2 | - | - |

**Recent Trend:**
- Last 5 plans: 01-01 (2 min), 01-02 (2 min), 01-03 (5 min)
- Trend: Stable
| Phase 01 P01 | 2 min | 2 tasks | 4 files |
| Phase 01 P02 | 2 min | 3 tasks | 7 files |
| Phase 01 P03 | 5 min | 3 tasks | 4 files |

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- [Init]: Treat PI-RL as online RL extension path.
- [Init]: Integrate incrementally in LeRobot runtime instead of full RLinf runtime replacement.
- [Update]: Use LIBERO benchmark as default simulation-first validation path for PI-RL milestones.
- [Phase 01-01]: Use strict canonical pi-rl recipe at parser preflight. — Prevents ambiguous spellings and gives deterministic correction hints before runtime startup.
- [Phase 01-01]: Require PI-RL variant and variant-specific knobs only when recipe=pi-rl. — Preserves default behavior when recipe is unset while enforcing strict PI-RL safety gates.
- [Phase 01-02]: Centralized PI-RL runtime preflight context for actor/learner/train — Keeps recipe eligibility and startup summary deterministic from one validation source.
- [Phase 01-02]: Actor validates learner config path/hash from streamed metadata before loading params — Hard-fails mismatched recipe sources without protobuf changes.
- [Phase 01-03]: Represent RCP-01/02/03 with explicit matrix tests in config and RL modules — Keeps roadmap acceptance gates executable and directly traceable to requirement IDs.
- [Phase 01-03]: Verify PI-RL startup preflight via hardware-independent unit tests — Covers actor/learner guard behavior deterministically in CI without robot runtime dependencies.
- [Phase 02 Context]: Default to smoke-first `libero_10` training with explicit two-terminal learner/actor launch and hard-fail checkpoint metadata mismatch handling.

### Pending Todos

None yet.

### Blockers/Concerns

- Need explicit acceptance thresholds for LIBERO per-suite/average metrics for Phase 3 sign-off.

## Session Continuity

Last session: 2026-02-22 03:24 UTC
Stopped at: Phase 2 context gathered
Resume file: .planning/phases/02-learner-pi-rl-training-path/02-CONTEXT.md
