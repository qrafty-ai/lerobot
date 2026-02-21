# Roadmap: LeRobot PI-RL Extension

## Overview

This roadmap delivers PI-RL support through a low-risk sequence: first wire policy/config integration,
then add learner algorithm behavior, then validate distributed runtime compatibility and regressions,
and finally package runnable docs/config recipes for adoption.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: PI-RL Foundation Wiring** - Add policy/config/factory registration and base PI-RL module skeleton.
- [ ] **Phase 2: Learner PI-RL Training Path** - Add PI-RL learner branch and training-step integration using existing replay flow.
- [ ] **Phase 3: Runtime Compatibility and Verification** - Prove actor/learner compatibility and protect SAC with tests.
- [ ] **Phase 4: Recipes and Operational Docs** - Publish runnable PI-RL recipes and usage guidance.

## Phase Details

### Phase 1: PI-RL Foundation Wiring
**Goal**: Make PI-RL selectable and instantiable through LeRobot's existing config and factory pathways.
**Depends on**: Nothing (first phase)
**Requirements**: [POL-01, POL-02, POL-03]
**Success Criteria** (what must be TRUE):
  1. User can set `--policy.type=pi_rl` and configuration parses without manual patches.
  2. Policy factory returns PI-RL policy class and processor path correctly.
  3. Baseline policy instantiation tests pass with PI-RL configuration.
**Plans**: 3 plans

Plans:
- [ ] 01-01: Create `policies/pi_rl` config/model/processor modules following LeRobot conventions.
- [ ] 01-02: Wire `pi_rl` into policy factory and related exported policy lists.
- [ ] 01-03: Add focused tests for config parsing and factory instantiation.

### Phase 2: Learner PI-RL Training Path
**Goal**: Enable learner-side PI-RL optimization while reusing existing transport/replay runtime.
**Depends on**: Phase 1
**Requirements**: [LRN-01, LRN-02, LRN-03]
**Success Criteria** (what must be TRUE):
  1. Learner can enter a PI-RL-specific update branch based on policy type.
  2. PI-RL branch consumes replay-buffer transitions from current actor stream.
  3. PI-RL checkpoints can be saved and resumed through existing conventions.
**Plans**: 3 plans

Plans:
- [ ] 02-01: Implement PI-RL learner branch and update scheduling hooks.
- [ ] 02-02: Integrate PI-RL loss/optimizer calls through policy-forward contracts.
- [ ] 02-03: Validate checkpoint/resume flow for PI-RL path.

### Phase 3: Runtime Compatibility and Verification
**Goal**: Validate distributed runtime correctness and prevent regressions on SAC and transport behavior.
**Depends on**: Phase 2
**Requirements**: [ACT-01, ACT-02, ACT-03, VAL-01, VAL-02]
**Success Criteria** (what must be TRUE):
  1. Actor receives and applies learner-updated PI-RL parameters correctly.
  2. Existing gRPC/queue transition flow remains unchanged and functional.
  3. SAC tests and PI-RL regression checks pass together.
**Plans**: 3 plans

Plans:
- [ ] 03-01: Add actor/learner integration tests for PI-RL parameter and transition streaming.
- [ ] 03-02: Add learner-branch and policy-level regression tests.
- [ ] 03-03: Run cross-path validation (PI-RL and SAC) and harden runtime edge cases.

### Phase 4: Recipes and Operational Docs
**Goal**: Ship runnable PI-RL usage docs and configs for practical team adoption.
**Depends on**: Phase 3
**Requirements**: [DOC-01]
**Success Criteria** (what must be TRUE):
  1. Users can follow documented commands/configs to launch PI-RL learner+actor flow.
  2. Docs clearly explain what changed, what stayed stable, and known limits.
  3. Example recipe artifacts align with tested runtime behavior.
**Plans**: 2 plans

Plans:
- [ ] 04-01: Create PI-RL training recipe docs and configuration examples.
- [ ] 04-02: Add troubleshooting and operational notes (FPS, sync, resume, metrics).

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. PI-RL Foundation Wiring | 0/3 | Not started | - |
| 2. Learner PI-RL Training Path | 0/3 | Not started | - |
| 3. Runtime Compatibility and Verification | 0/3 | Not started | - |
| 4. Recipes and Operational Docs | 0/2 | Not started | - |
