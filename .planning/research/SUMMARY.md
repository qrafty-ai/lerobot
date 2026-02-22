# Project Research Summary

**Project:** LeRobot PI-RL Extension
**Domain:** Online RL recipe integration for flow-based VLA policies
**Researched:** 2026-02-21
**Confidence:** HIGH

## Executive Summary

LeRobot already has a mature distributed actor/learner RL runtime with gRPC transport, replay buffering,
and a SAC-centric learner update loop. Research indicates PI-RL is best treated as an online RL fine-tuning
recipe (with optional hybridization when offline data mixing is enabled), so the most effective approach is
an incremental extension rather than a runtime replacement.

The recommended implementation path keeps transport and replay contracts stable while adding a PI-RL
recipe layer (not a new policy family) and a learner branch for PI-RL-specific optimization behavior. This minimizes architectural
risk, preserves SAC compatibility, and keeps rollout/inference/update responsibilities aligned with existing code patterns.

Main risks are actor/learner parameter-sync mismatches, premature transport redesign, and inference-time FPS regressions.
These risks can be contained through phased delivery, policy/branch-specific tests, and explicit runtime profiling.

## Key Findings

Canonical PI-RL core logic note: `.planning/research/PI_RL_CORE_ALGORITHM.md`

### Recommended Stack

Use LeRobot's existing Python + PyTorch + Draccus + gRPC runtime as the implementation foundation. Add PI-RL logic
inside recipe-level learner branching and flow-matching policy-compatible adapters, rather than introducing a second orchestration stack.

**Core technologies:**
- Python 3.10: project baseline and compatibility anchor.
- PyTorch: training and loss implementation surface.
- Draccus config registration: required for parser/factory integration.
- Existing gRPC actor/learner service: stable transport to preserve in MVP.

### Expected Features

**Must have (table stakes):**
- PI-RL recipe config/routing path independent from policy type.
- XVLA-based validation path for first supported flow-matching policy.
- Learner PI-RL optimization branch and actor compatibility.
- Replay-compatible online training flow and targeted tests.
- LIBERO-first validation protocol with single-suite + multi-suite commands and reportable per-suite metrics.

**Should have (competitive):**
- Flow-Noise/Flow-SDE variant toggles through config.
- Hybrid online+offline blending controls after online validation.

**Defer (v2+):**
- Broad runtime/orchestration redesign or full RLinf runtime parity.

### Architecture Approach

Keep scheduling/orchestration in `src/lerobot/rl/learner.py` and introduce PI-RL recipe routing there.
Maintain the current actor/learner service contract and transition schema while applying the recipe to flow-matching policies (XVLA first).

**Major components:**
1. Recipe layer: PI-RL mode selection, variant controls, and update scheduling.
2. Flow-matching policy target: XVLA first, with generalization path for additional policies.
3. Existing runtime infra: actor loop, transport, replay, and checkpoint path.

### Critical Pitfalls

1. **Actor/learner state mismatch** — enforce and test actor-streamed parameter contract.
2. **Premature transport redesign** — keep proto/schema unchanged in MVP.
3. **Branch regressions in learner** — add branch-specific and SAC-regression tests.
4. **Actor FPS degradation** — profile and cap inference complexity.

## Implications for Roadmap

Based on research, suggested phase structure:

### Phase 1: PI-RL Recipe Foundation
**Rationale:** Establishes the minimum architecture entry points without destabilizing runtime.
**Delivers:** recipe-level PI-RL selection + XVLA-compatible baseline wiring.
**Addresses:** Core wiring requirements.
**Avoids:** transport and schema churn.

### Phase 2: Learner Algorithm Integration
**Rationale:** Adds PI-RL optimization semantics where training logic already lives.
**Delivers:** learner PI-RL branch with online replay loop support.
**Uses:** existing replay/queue/transport infrastructure.
**Implements:** algorithm branch scheduling and optimizer paths.

### Phase 3: Runtime Validation and Stability
**Rationale:** Prevents regressions and ensures operational quality.
**Delivers:** unit/integration tests, SAC compatibility checks, actor sync verification, and LIBERO benchmark reports.
**Addresses:** branch/regression and sync risks.

### Phase 4: Docs, Recipes, and Hybrid Controls
**Rationale:** Makes PI-RL path usable and extensible after stable core integration.
**Delivers:** runnable configs/docs and optional online+offline blending controls.

### Phase Ordering Rationale

- Recipe routing before optimization avoids debugging hidden mode-selection failures during learner work.
- Algorithm integration before broad docs ensures documentation reflects real behavior.
- Stability gate before hybrid controls prevents compounded failures.

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 2:** exact PI-RL loss/update adaptations for flow-matching policy interfaces (XVLA first).
- **Phase 4:** benchmark-specific recipe defaults and expected metric baselines.

Phases with standard patterns (skip research-phase):
- **Phase 1:** recipe/config/parser wiring follows established LeRobot conventions.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Fully aligned with existing codebase architecture |
| Features | HIGH | Strong convergence across paper, RLinf, and local runtime constraints |
| Architecture | HIGH | Existing actor/learner layering provides clear insertion points |
| Pitfalls | HIGH | Risks are concrete and tied to known runtime contracts |

**Overall confidence:** HIGH

### Gaps to Address

- Exact PI-RL objective details needed for first concrete learner implementation tasks.
- Target metric thresholds for “good enough” PI-RL runtime validation in LeRobot.

## Sources

### Primary (HIGH confidence)
- arXiv `2510.25889` and associated method description.
- RLinf repository module mapping and runner/algorithm references.
- LeRobot local architecture files under `src/lerobot/rl`, `src/lerobot/policies`, and `src/lerobot/configs`.
- LeRobot LIBERO benchmark guidance in `docs/source/libero.mdx`.

### Secondary (MEDIUM confidence)
- Private PI-RL code summary in `qrafty-ai/research`.

### Tertiary (LOW confidence)
- None used for core architectural claims.

---
*Research completed: 2026-02-21*
*Ready for roadmap: yes*
