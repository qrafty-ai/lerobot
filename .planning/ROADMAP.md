# Roadmap: LeRobot PI-RL Extension

## Overview

This roadmap delivers PI-RL support through a low-risk sequence: first wire recipe-level configuration
and XVLA baseline compatibility, then add learner recipe behavior, then validate distributed runtime
compatibility and regressions using LIBERO benchmark suites, and finally package runnable docs/config recipes for adoption.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: PI-RL Recipe Foundation** - Add recipe-level config/routing and XVLA-first integration baseline.
- [ ] **Phase 2: Learner PI-RL Training Path** - Add PI-RL learner branch and training-step integration using existing replay flow.
- [ ] **Phase 3: Runtime Compatibility and Verification** - Prove actor/learner compatibility and protect SAC with tests.
- [ ] **Phase 4: Recipes and Operational Docs** - Publish runnable PI-RL recipes and usage guidance.

## Phase Details

### Phase 1: PI-RL Recipe Foundation
**Goal**: Make PI-RL selectable as a training recipe independent of policy type, validated first with XVLA.
**Depends on**: Nothing (first phase)
**Requirements**: [RCP-01, RCP-02, RCP-03]
**Success Criteria** (what must be TRUE):
  1. User can enable PI-RL recipe mode while keeping policy type as a flow-matching policy (XVLA baseline).
  2. Recipe routing does not require introducing `pi_rl` as a new policy type.
  3. Baseline config/runtime selection tests pass for XVLA + PI-RL recipe setup.
**Plans**: 3 plans

Plans:
- [x] 01-01: Define recipe-level PI-RL config knobs and selection path in training config.
- [x] 01-02: Wire recipe dispatch logic so it applies to flow-matching policies without changing policy taxonomy.
- [x] 01-03: Add focused tests for recipe selection and XVLA compatibility.

### Phase 2: Learner PI-RL Training Path
**Goal**: Enable learner-side PI-RL optimization while reusing existing transport/replay runtime.
**Depends on**: Phase 1
**Requirements**: [LRN-01, LRN-02, LRN-03, LRN-04]
**Success Criteria** (what must be TRUE):
  1. Learner can enter a PI-RL-specific update branch based on recipe mode, not policy type.
  2. PI-RL branch consumes replay-buffer transitions from current actor stream.
  3. PI-RL recipe checkpoints can be saved and resumed through existing conventions.
  4. LIBERO training smoke run completes with documented PI-RL orchestration (XVLA target).
**Plans**: 3 plans

Plans:
- [ ] 02-01: Implement PI-RL learner branch and update scheduling hooks.
- [ ] 02-02: Integrate PI-RL loss/optimizer calls through flow-matching policy-forward contracts (XVLA first).
- [ ] 02-03: Validate checkpoint/resume and run LIBERO training smoke flow for PI-RL path.

Training commands (Phase 2 gate):

```bash
pip install -e ".[libero]"
export MUJOCO_GL=egl

# Optional supervised warm-start in LIBERO environment
lerobot-train \
  --policy.type=xvla \
  --dataset.repo_id=HuggingFaceVLA/libero \
  --env.type=libero \
  --env.task=libero_10 \
  --output_dir=./outputs/pirl_libero_warmstart \
  --steps=10000 \
  --batch_size=4

# PI-RL online recipe orchestration (HILSERL_SIM style: actor + learner)
# Terminal A
python -m lerobot.rl.learner --config_path path/to/pirl_libero_train.json

# Terminal B
python -m lerobot.rl.actor --config_path path/to/pirl_libero_train.json
```

### Phase 3: Runtime Compatibility and Verification
**Goal**: Validate distributed runtime correctness and prevent regressions on SAC and transport behavior with LIBERO-first simulation testing.
**Depends on**: Phase 2
**Requirements**: [ACT-01, ACT-02, ACT-03, VAL-01, VAL-02, VAL-03, VAL-04, VAL-05]
**Success Criteria** (what must be TRUE):
  1. Actor receives and applies learner-updated parameters correctly in XVLA + PI-RL mode.
  2. Existing gRPC/queue transition flow remains unchanged and functional.
  3. LIBERO single-suite smoke eval passes for XVLA + PI-RL outputs (at least `libero_object`).
  4. LIBERO multi-suite eval runs for `libero_spatial,libero_object,libero_goal,libero_10` with recorded per-suite metrics.
  5. Self-contained LIBERO setup is codified (`.[libero]` install + `MUJOCO_GL=egl`).
  6. SAC tests and PI-RL regression checks pass together.
**Plans**: 3 plans

Plans:
- [ ] 03-01: Add actor/learner integration tests for PI-RL parameter and transition streaming.
- [ ] 03-02: Add learner-branch and policy-level regression tests.
- [ ] 03-03: Run LIBERO validation matrix (single-suite + multi-suite) plus SAC cross-path checks and harden runtime edge cases.

Validation matrix commands (Phase 3 gate):

```bash
pip install -e ".[libero]"
export MUJOCO_GL=egl

# smoke suite
lerobot-eval \
  --policy.path="<pi-rl-output-policy>" \
  --env.type=libero \
  --env.task=libero_object \
  --eval.batch_size=1 \
  --eval.n_episodes=3

# multi-suite benchmark
lerobot-eval \
  --policy.path="<pi-rl-output-policy>" \
  --env.type=libero \
  --env.task=libero_spatial,libero_object,libero_goal,libero_10 \
  --eval.batch_size=1 \
  --eval.n_episodes=10 \
  --env.max_parallel_tasks=1
```

Phase 3 deliverable artifact:
- Per-suite success rates (Spatial/Object/Goal/Long) + average in a reproducible report.

### Phase 4: Recipes and Operational Docs
**Goal**: Ship runnable PI-RL usage docs and configs for practical team adoption.
**Depends on**: Phase 3
**Requirements**: [DOC-01]
**Success Criteria** (what must be TRUE):
  1. Users can follow documented commands/configs to launch PI-RL LIBERO training (learner+actor) and evaluation flow.
  2. Docs include self-contained LIBERO test commands (install/setup/rendering/single-suite/multi-suite).
  3. Docs clearly explain what changed, what stayed stable, and known limits.
  4. Example recipe artifacts align with tested runtime behavior and recorded LIBERO metrics.
**Plans**: 2 plans

Plans:
- [ ] 04-01: Create PI-RL training recipe docs and configuration examples.
- [ ] 04-02: Add troubleshooting and operational notes (FPS, sync, resume, metrics).

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. PI-RL Recipe Foundation | 3/3 | Complete | 2026-02-22 |
| 2. Learner PI-RL Training Path | 0/3 | Not started | - |
| 3. Runtime Compatibility and Verification | 0/3 | Not started | - |
| 4. Recipes and Operational Docs | 0/2 | Not started | - |
