# Requirements: LeRobot PI-RL Extension

**Defined:** 2026-02-21
**Core Value:** Enable reliable online RL fine-tuning of flow-based VLA policies in LeRobot while preserving existing RL stability and operability.

## v1 Requirements

Requirements for initial release. Each maps to roadmap phases.

### Recipe and Configuration

- [x] **RCP-01**: User can enable PI-RL as a training recipe independently of policy type selection.
- [ ] **RCP-02**: User can run PI-RL recipe with flow-matching policies, with XVLA as the first validated target.
- [x] **RCP-03**: User can configure PI-RL variant behavior (Flow-Noise vs Flow-SDE style options) through structured recipe config fields.

### Learner Training Flow

- [ ] **LRN-01**: User can run learner in PI-RL recipe mode and execute a PI-RL-specific optimization branch.
- [ ] **LRN-02**: User can train PI-RL online using existing replay-buffer transition schema and queue/gRPC flow.
- [ ] **LRN-03**: User can checkpoint and resume PI-RL recipe training using existing checkpoint conventions.
- [ ] **LRN-04**: User can execute a self-contained LIBERO training smoke run for PI-RL (XVLA target) using documented orchestration.

### Actor and Runtime Compatibility

- [ ] **ACT-01**: User can run actor process with XVLA under PI-RL recipe mode and receive learner-updated parameters through existing stream path.
- [ ] **ACT-02**: User can complete rollout interactions without transport/proto contract changes in MVP scope.
- [ ] **ACT-03**: User can keep SAC runtime flow operational after PI-RL integration.

### Verification and Documentation

- [ ] **VAL-01**: User can rely on automated tests covering PI-RL recipe selection, learner branch behavior, and XVLA integration.
- [ ] **VAL-02**: User can rely on integration checks for actor↔learner parameter/transition flow in XVLA + PI-RL mode.
- [ ] **VAL-03**: User can run a LIBERO benchmark smoke evaluation (`libero_object`) for XVLA + PI-RL outputs via `lerobot-eval`.
- [ ] **VAL-04**: User can run a LIBERO multi-suite evaluation (`libero_spatial,libero_object,libero_goal,libero_10`) and collect per-suite success metrics.
- [ ] **VAL-05**: User can execute a self-contained LIBERO eval setup (`pip install -e ".[libero]"`, `MUJOCO_GL=egl`) and produce a reproducible metrics report.
- [ ] **DOC-01**: User can follow a documented PI-RL training recipe (configs + command flow) and understand how to extend it to other flow-matching policies.

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Hybrid and Scale

- **HYB-01**: User can configure explicit online/offline sampling ratios for PI-RL hybrid fine-tuning.
- **HYB-02**: User can run expanded benchmark recipes with standardized evaluation reports.
- **SCL-01**: User can scale PI-RL workflows beyond current local/single-node defaults with validated orchestration guidance.

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Full RLinf runtime replacement inside LeRobot | Too disruptive for initial milestone; not required to deliver PI-RL support |
| End-to-end reproduction of all paper benchmark tables | Compute-heavy and not required for first functional integration |
| Transport/protobuf redesign | Not needed for MVP if PI-RL can run on existing transition contracts |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| RCP-01 | Phase 1 | Complete |
| RCP-02 | Phase 1 | Pending |
| RCP-03 | Phase 1 | Complete |
| LRN-01 | Phase 2 | Pending |
| LRN-02 | Phase 2 | Pending |
| LRN-03 | Phase 2 | Pending |
| LRN-04 | Phase 2 | Pending |
| ACT-01 | Phase 3 | Pending |
| ACT-02 | Phase 3 | Pending |
| ACT-03 | Phase 3 | Pending |
| VAL-01 | Phase 3 | Pending |
| VAL-02 | Phase 3 | Pending |
| VAL-03 | Phase 3 | Pending |
| VAL-04 | Phase 3 | Pending |
| VAL-05 | Phase 3 | Pending |
| DOC-01 | Phase 4 | Pending |

**Coverage:**
- v1 requirements: 16 total
- Mapped to phases: 16
- Unmapped: 0

---
*Requirements defined: 2026-02-21*
*Last updated: 2026-02-21 after initial definition*
