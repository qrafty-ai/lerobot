# Pitfalls Research

**Domain:** Adding PI-RL algorithm path to existing distributed RL runtime
**Researched:** 2026-02-21
**Confidence:** HIGH

## Critical Pitfalls

### Pitfall 1: Breaking actor/learner parameter contract

**What goes wrong:**
Actor cannot load learner-updated parameters or silently loads incomplete state.

**Why it happens:**
Recipe-level PI-RL integration changes what must be streamed to actor, but transport payload handling is left unchanged.

**How to avoid:**
Define and test PI-RL actor-side required state explicitly; keep `policy.actor` stream contract stable for MVP.

**Warning signs:**
Actor runs but performance stalls, parameter load warnings, mismatched state dict keys.

**Phase to address:**
Phase 1

---

### Pitfall 2: Forcing transport/schema redesign too early

**What goes wrong:**
Project spends cycles rewriting gRPC/proto and queue contracts before proving PI-RL learning behavior.

**Why it happens:**
Premature optimization and overfitting to reference implementation internals.

**How to avoid:**
Validate PI-RL against existing transition schema first; only expand payload after evidence-backed need.

**Warning signs:**
Large infra diffs with no end-to-end trainability milestone.

**Phase to address:**
Phase 1

---

### Pitfall 3: Learner branch complexity without tests

**What goes wrong:**
SAC path regresses or PI-RL path remains unstable due to branching logic side effects.

**Why it happens:**
Algorithm branch added in learner without dedicated unit/integration guardrails.

**How to avoid:**
Add focused tests for branch selection, update steps, replay usage, and actor sync behavior.

**Warning signs:**
Intermittent CI failures, hidden runtime drift, flaky online loop behavior.

**Phase to address:**
Phase 2

---

### Pitfall 4: Actor FPS collapse under PI-RL inference cost

**What goes wrong:**
Environment interaction loop slows below required FPS, reducing data quality and training stability.

**Why it happens:**
Flow-style sampling can be heavier than SAC inference and is run per interaction step.

**How to avoid:**
Constrain inference-time complexity, profile with existing actor timing metrics, and expose tuning knobs.

**Warning signs:**
Frequent low-FPS warnings, unstable episodic interaction cadence.

**Phase to address:**
Phase 3

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Hardcode PI-RL tuning constants in learner | Faster initial coding | Opaque behavior and poor reproducibility | Never (use config fields) |
| Couple PI-RL recipe routing to policy-type checks | Fewer files changed | Wrong abstraction and poor extensibility | Never (route by recipe mode) |
| Skip tests for runtime branching | Faster merge | High regression risk on SAC path | Never |

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| Recipe wiring | Add PI-RL knobs but no learner dispatch | Wire train config recipe mode to learner branch explicitly |
| CLI parsing | Recipe mode not represented in train config | Add recipe fields in train config and validate parser path |
| Actor sync | Stream wrong state components | Keep actor-required state explicit and tested |

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Heavy inference per step | Policy FPS warnings, rollout lag | Bound sampling steps and profile actor loop | Medium to high task FPS settings |
| Overly frequent parameter pushes | Queue/network pressure | Tune push frequency by config and profile | Long-running online jobs |
| Replay imbalance in hybrid mode | Unstable updates | Explicit online/offline ratio control | After enabling dataset mixing |

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| Exposing learner endpoint without environment guardrails | Unauthorized interaction with learner service | Keep host/port defaults conservative and deployment-scoped |
| Blind loading of external configs/checkpoints | Integrity and reproducibility issues | Validate sources and lock checkpoint provenance |

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| PI-RL config names unclear to users | Misconfiguration and failed runs | Add explicit docs/examples with sane defaults |
| Missing migration guidance from SAC flow | Slow adoption and confusion | Provide “what changes / what stays same” guidance |

## "Looks Done But Isn't" Checklist

- [ ] **PI-RL recipe wired:** verify train config can enable recipe mode while keeping policy type (XVLA baseline).
- [ ] **Learner branch works:** verify optimization steps execute and checkpoints save.
- [ ] **Actor sync works:** verify actor receives and loads updated params continuously.
- [ ] **SAC unaffected:** verify SAC path still passes targeted RL tests.

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Actor sync mismatch | MEDIUM | Re-align streamed state dict keys, add compatibility tests |
| Learner branch regressions | MEDIUM | Isolate branch logic, add fixtures, re-run RL integration tests |
| FPS collapse | HIGH | Reduce inference complexity, tune config, profile and optimize hotspots |

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Actor/learner sync contract breakage | Phase 1 | Actor receives/loads params in integration test |
| Premature transport redesign | Phase 1 | No proto changes in MVP PR unless justified |
| Learner branch regressions | Phase 2 | RL test suite for both SAC and PI-RL paths |
| Actor FPS collapse | Phase 3 | Policy frequency metrics within acceptable bounds |

## Sources

- LeRobot runtime architecture inspection (`actor.py`, `learner.py`, `learner_service.py`, `buffer.py`)
- Oracle architecture review for PI-RL integration approach
- RLinf runtime and algorithm mapping
- PI-RL paper and private summary

---
*Pitfalls research for: LeRobot PI-RL extension*
*Researched: 2026-02-21*
