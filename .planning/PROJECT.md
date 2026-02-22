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
- ✓ Flow-matching policy implementations already exist (including XVLA) — existing

### Active

- [ ] Add PI-RL recipe configuration and routing that is independent from policy type selection.
- [ ] Ensure PI-RL recipe can run on flow-matching policies, with XVLA as first validated target.
- [ ] Extend learner optimization flow for PI-RL objectives and log-prob-aware updates.
- [ ] Preserve compatibility with current transport/process architecture and SAC training route.
- [ ] Add verification coverage (unit/integration) for PI-RL data flow and training contracts.
- [ ] Make LIBERO benchmark the default simulation-first validation harness for PI-RL milestones.
- [ ] Provide runnable training/eval recipe docs and configs for PI-RL workflow in LeRobot.

### Out of Scope

- Full RLinf framework migration into LeRobot — too broad and unnecessary for initial PI-RL support.
- Reproducing every benchmark number from the PI-RL paper in this milestone — requires separate compute campaign.
- Immediate multi-node/disaggregated training orchestration redesign — defer until single-node recipe is stable.

## Context

- Target method: PI-RL (`arXiv:2510.25889`) and RLinf reference implementation.
- PI-RL is an online RL fine-tuning approach for flow-based VLA models with Flow-Noise and Flow-SDE variants.
- LeRobot already has a distributed RL actor/learner runtime under `src/lerobot/rl/`, currently SAC-centric.
- User goal: plan and execute an extension path for PI-RL recipe support in `src/lerobot/rl/`, applicable to flow-matching policies (XVLA first).
- Real-robot testing is currently constrained; validation should run through LeRobot's LIBERO simulation benchmark path.
- LIBERO evaluation path and command patterns are documented in `docs/source/libero.mdx` and should be copied into phase gates.

## Constraints

- **Architecture**: Preserve existing actor/learner split, gRPC service contracts, and queue serialization model.
- **Compatibility**: Do not break SAC/HIL-SERL usage and existing RL entrypoints.
- **Quality**: Add tests for new algorithm/control flow and maintain CI viability.
- **Validation**: Use LIBERO suites as primary test/eval surface before any real-robot verification.
- **Scope**: Deliver an implementable staged roadmap, not a full-stack RLinf fork.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| PI-RL treated as online RL extension path | Paper and RLinf training loop are online rollout/update-driven | — Pending |
| Keep LeRobot-native runtime and integrate recipe incrementally | Lowest integration risk, preserves existing operational model | — Pending |
| Model PI-RL as a recipe layer, not a policy type | PI-RL should apply to any flow-matching policy and avoid forking policy taxonomy | — Pending |
| Standardize on LIBERO-first simulation validation | Real-robot loop is expensive/hard to iterate; LIBERO gives repeatable benchmark coverage | — Pending |

---
*Last updated: 2026-02-21 after initialization*
