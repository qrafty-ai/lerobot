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

The recommended implementation path keeps transport and replay contracts stable while adding a new `pi_rl`
policy/config family and a learner branch for PI-RL-specific optimization behavior. This minimizes architectural
risk, preserves SAC compatibility, and keeps rollout/inference/update responsibilities aligned with existing code patterns.

Main risks are actor/learner parameter-sync mismatches, premature transport redesign, and inference-time FPS regressions.
These risks can be contained through phased delivery, policy/branch-specific tests, and explicit runtime profiling.

## Key Findings

### Recommended Stack

Use LeRobot's existing Python + PyTorch + Draccus + gRPC runtime as the implementation foundation. Add PI-RL logic
inside new policy modules and learner branching, rather than introducing a second orchestration stack.

**Core technologies:**
- Python 3.10: project baseline and compatibility anchor.
- PyTorch: training and loss implementation surface.
- Draccus config registration: required for parser/factory integration.
- Existing gRPC actor/learner service: stable transport to preserve in MVP.

### Expected Features

**Must have (table stakes):**
- `pi_rl` config/policy/factory registration path.
- Learner PI-RL optimization branch and actor compatibility.
- Replay-compatible online training flow and targeted tests.

**Should have (competitive):**
- Flow-Noise/Flow-SDE variant toggles through config.
- Hybrid online+offline blending controls after online validation.

**Defer (v2+):**
- Broad runtime/orchestration redesign or full RLinf runtime parity.

### Architecture Approach

Keep algorithm semantics in `policies/pi_rl/modeling_pi_rl.py` and keep scheduling/orchestration in `src/lerobot/rl/learner.py`.
Maintain the current actor/learner service contract and transition schema while introducing policy-type routing in learner.

**Major components:**
1. Policy family (`pi_rl`): model + losses + inference semantics.
2. Learner branch: PI-RL update schedule and optimizer control.
3. Existing runtime infra: actor loop, transport, replay, and checkpoint path.

### Critical Pitfalls

1. **Actor/learner state mismatch** — enforce and test actor-streamed parameter contract.
2. **Premature transport redesign** — keep proto/schema unchanged in MVP.
3. **Branch regressions in learner** — add branch-specific and SAC-regression tests.
4. **Actor FPS degradation** — profile and cap inference complexity.

## Implications for Roadmap

Based on research, suggested phase structure:

### Phase 1: PI-RL Foundation Wiring
**Rationale:** Establishes the minimum architecture entry points without destabilizing runtime.
**Delivers:** `pi_rl` config/policy/factory + parser-compatible instantiation.
**Addresses:** Core wiring requirements.
**Avoids:** transport and schema churn.

### Phase 2: Learner Algorithm Integration
**Rationale:** Adds PI-RL optimization semantics where training logic already lives.
**Delivers:** learner PI-RL branch with online replay loop support.
**Uses:** existing replay/queue/transport infrastructure.
**Implements:** algorithm branch scheduling and optimizer paths.

### Phase 3: Runtime Validation and Stability
**Rationale:** Prevents regressions and ensures operational quality.
**Delivers:** unit/integration tests, SAC compatibility checks, actor sync verification.
**Addresses:** branch/regression and sync risks.

### Phase 4: Docs, Recipes, and Hybrid Controls
**Rationale:** Makes PI-RL path usable and extensible after stable core integration.
**Delivers:** runnable configs/docs and optional online+offline blending controls.

### Phase Ordering Rationale

- Wiring before optimization avoids debugging hidden instantiation failures during learner work.
- Algorithm integration before broad docs ensures documentation reflects real behavior.
- Stability gate before hybrid controls prevents compounded failures.

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 2:** exact PI-RL loss/update adaptations for LeRobot policy interfaces.
- **Phase 4:** benchmark-specific recipe defaults and expected metric baselines.

Phases with standard patterns (skip research-phase):
- **Phase 1:** config/factory/parser wiring follows established LeRobot conventions.

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

### Secondary (MEDIUM confidence)
- Private PI-RL code summary in `qrafty-ai/research`.

### Tertiary (LOW confidence)
- None used for core architectural claims.

---
*Research completed: 2026-02-21*
*Ready for roadmap: yes*
