# LeRobot PI-RL Extension

## What This Is

This project extends LeRobot's distributed RL runtime to support a PI-RL training recipe for flow-based
vision-language-action policies. It focuses on integrating Flow-Noise and Flow-SDE style online fine-tuning
into the existing actor/learner architecture without regressing the current SAC/HIL-SERL path.

## Core Value

Enable reliable online RL fine-tuning of flow-based VLA policies in LeRobot while preserving existing RL
stability and operability.

## Requirements

### Validated

- ✓ Distributed online RL runtime exists with actor/learner + gRPC transport + queue streaming — existing
- ✓ Replay buffer and online optimization loop are productionized for SAC — existing
- ✓ Policy registration and config plumbing support extensible policy types — existing

### Active

- [ ] Add PI-RL-capable policy/config path for flow-based VLA fine-tuning in LeRobot.
- [ ] Extend learner optimization flow for PI-RL objectives and log-prob-aware updates.
- [ ] Preserve compatibility with current transport/process architecture and SAC training route.
- [ ] Add verification coverage (unit/integration) for PI-RL data flow and training contracts.
- [ ] Provide runnable training/eval recipe docs and configs for PI-RL workflow in LeRobot.

### Out of Scope

- Full RLinf framework migration into LeRobot — too broad and unnecessary for initial PI-RL support.
- Reproducing every benchmark number from the PI-RL paper in this milestone — requires separate compute campaign.
- Immediate multi-node/disaggregated training orchestration redesign — defer until single-node recipe is stable.

## Context

- Target method: PI-RL (`arXiv:2510.25889`) and RLinf reference implementation.
- PI-RL is an online RL fine-tuning approach for flow-based VLA models with Flow-Noise and Flow-SDE variants.
- LeRobot already has a distributed RL actor/learner runtime under `src/lerobot/rl/`, currently SAC-centric.
- User goal: plan and execute an extension path for PI-RL support in `src/lerobot/rl/` and adjacent policy/config wiring.

## Constraints

- **Architecture**: Preserve existing actor/learner split, gRPC service contracts, and queue serialization model.
- **Compatibility**: Do not break SAC/HIL-SERL usage and existing RL entrypoints.
- **Quality**: Add tests for new algorithm/control flow and maintain CI viability.
- **Scope**: Deliver an implementable staged roadmap, not a full-stack RLinf fork.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| PI-RL treated as online RL extension path | Paper and RLinf training loop are online rollout/update-driven | — Pending |
| Keep LeRobot-native runtime and integrate recipe incrementally | Lowest integration risk, preserves existing operational model | — Pending |
| Phase PI-RL support behind explicit config/policy wiring | Allows coexistence with SAC and safer rollout | — Pending |

---
*Last updated: 2026-02-21 after initialization*
