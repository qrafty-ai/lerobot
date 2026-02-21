# Feature Research

**Domain:** Brownfield robotics ML runtime extension (online RL recipe integration)
**Researched:** 2026-02-21
**Confidence:** HIGH

## Feature Landscape

### Table Stakes (Users Expect These)

Features users assume exist. Missing these = PI-RL support is not practically usable.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| `pi_rl` policy/config registration | New RL method must be selectable like existing policies | MEDIUM | Requires `PreTrainedConfig` registration + factory wiring |
| Learner-side PI-RL optimization path | New method must train end-to-end in current actor/learner flow | HIGH | Current learner loop is SAC-centric |
| Actor inference compatibility | Actor process must keep receiving usable policy params | MEDIUM | Must preserve `.actor` parameter streaming contract |
| Replay-buffer-compatible data path | Must reuse current transition stream for MVP | MEDIUM | Avoid proto/schema redesign in first milestone |
| Test coverage for config/factory/runtime path | Regression safety against SAC and transport flow | MEDIUM | Add policy, learner branch, and transport/queue checks |

### Differentiators (Competitive Advantage)

Features that make this extension strategically strong beyond a basic port.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Flow-Noise + Flow-SDE recipe toggles | One implementation supports two PI-RL variants | HIGH | Requires carefully scoped config and loss plumbing |
| Hybrid online+offline fine-tuning mode | Reuse demos with online updates for data efficiency | HIGH | Built on existing optional `cfg.dataset` offline path |
| Benchmark-ready recipes for LeRobot workflows | Lowers barrier for adoption and reproducibility | MEDIUM | Config/doc heavy after core loop works |

### Anti-Features (Commonly Requested, Often Problematic)

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Full RLinf runtime import/fork | “Fast parity with reference repo” | High maintenance + architectural drift from LeRobot | Port only PI-RL recipe primitives into LeRobot architecture |
| Transport/proto redesign in MVP | “Support future flexibility now” | Large risk before algorithm value is proven | Keep gRPC contract fixed for phase 1 |
| Full benchmark replication in first phase | “Show SOTA immediately” | Compute-heavy and blocks integration progress | First validate functionality + invariants, then benchmark |

## Feature Dependencies

```
PI-RL training loop support
    └──requires──> pi_rl policy/config registration
                       └──requires──> factory + parser compatibility

Hybrid online+offline mode ──requires──> stable online-only PI-RL path

Benchmark recipes ──enhances──> validated PI-RL training/eval flow
```

### Dependency Notes

- **PI-RL training loop requires policy/config wiring:** learner cannot route updates without a recognized policy type.
- **Hybrid mode depends on online-first stability:** blending offline data is safer after online behavior is validated.
- **Benchmark recipes depend on validated core flow:** otherwise failures are hard to localize.

## MVP Definition

### Launch With (v1)

- [ ] `pi_rl` policy/config/factory integration — makes method selectable.
- [ ] Learner PI-RL branch with online replay loop compatibility — makes method trainable.
- [ ] Actor parameter sync + inference path preserved — keeps distributed runtime working.
- [ ] Unit/integration tests for new path — protects regressions.
- [ ] Basic docs/config recipe for running PI-RL path — enables team adoption.

### Add After Validation (v1.x)

- [ ] Hybrid online+offline sampling controls — add when online path is stable.
- [ ] Expanded diagnostics/metrics for PI-RL internals — add when tuning begins.

### Future Consideration (v2+)

- [ ] Multi-node/disaggregated scaling features for PI-RL workloads — defer until local/single-node success.
- [ ] Deep parity with RLinf orchestration abstractions — defer unless roadmap demands runtime convergence.

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Policy/config/factory wiring | HIGH | MEDIUM | P1 |
| Learner PI-RL optimization branch | HIGH | HIGH | P1 |
| Actor sync compatibility | HIGH | MEDIUM | P1 |
| Tests for new runtime path | HIGH | MEDIUM | P1 |
| Hybrid online+offline controls | MEDIUM | HIGH | P2 |
| Benchmark recipe expansion | MEDIUM | MEDIUM | P2 |

**Priority key:**
- P1: Must have for launch
- P2: Should have, add when possible
- P3: Nice to have, future consideration

## Competitor Feature Analysis

| Feature | RLinf | LeRobot (Current) | Our Approach |
|---------|-------|-------------------|--------------|
| PI-RL recipe support | Present | Absent | Add LeRobot-native PI-RL path |
| Online actor/learner runtime | Present | Present | Reuse LeRobot runtime with algorithm extension |
| Flow-based VLA RL fine-tuning | Present | Limited in RL runtime | Add policy/loss integration incrementally |

## Sources

- arXiv `2510.25889` (paper title/abstract and method framing)
- RLinf repo structure and module references
- Private PI-RL summary in `qrafty-ai/research`
- Local LeRobot RL and policy architecture inspection

---
*Feature research for: LeRobot PI-RL extension*
*Researched: 2026-02-21*
