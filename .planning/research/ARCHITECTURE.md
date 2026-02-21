# Architecture Research

**Domain:** Incremental algorithm extension in distributed RL runtime
**Researched:** 2026-02-21
**Confidence:** HIGH

## Standard Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                   CLI / Config Layer                        │
├─────────────────────────────────────────────────────────────┤
│  parser.wrap()  TrainRLServerPipelineConfig  policy config │
└───────────────┬─────────────────────────────────────────────┘
                │
┌───────────────┴─────────────────────────────────────────────┐
│                  Runtime Orchestration                      │
├─────────────────────────────────────────────────────────────┤
│  Actor process/thread        Learner process/thread         │
│  - env interaction           - optimization loop            │
│  - transition creation       - replay sampling              │
│  - param receive             - param push                   │
└───────────────┬─────────────────────────────┬───────────────┘
                │ gRPC transport              │
┌───────────────┴─────────────────────────────┴───────────────┐
│                     Data / Model Layer                       │
├─────────────────────────────────────────────────────────────┤
│  ReplayBuffer (online)  Optional offline buffer  Policy impl│
│  Transition schema       state/action/reward/done           │
└─────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|------------------------|
| Policy module | Algorithm math, losses, inference behavior | `modeling_*.py` + `forward(..., model=...)` |
| Learner runtime | Scheduling updates, batching, optimizer steps | `src/lerobot/rl/learner.py` |
| Actor runtime | Environment interaction and transition emission | `src/lerobot/rl/actor.py` |
| Transport service | Streams transitions/interactions/parameters | `src/lerobot/rl/learner_service.py` |
| Config/factory layer | Registration and instantiation of policy types | `PreTrainedConfig` + `policies/factory.py` |

## Recommended Project Structure

```
src/
└── lerobot/
    ├── policies/
    │   └── pi_rl/
    │       ├── configuration_pi_rl.py   # PI-RL config registration
    │       ├── modeling_pi_rl.py        # PI-RL policy/loss logic
    │       └── processor_pi_rl.py       # pre/post processor factory
    ├── rl/
    │   ├── learner.py                   # add pi_rl training branch
    │   └── actor.py                     # preserve actor sync contract
    └── configs/
        └── train.py                     # optional train-level knobs
```

### Structure Rationale

- **`policies/pi_rl/`** keeps algorithm-specific complexity isolated from runtime orchestration.
- **`rl/learner.py` branch-by-policy** minimizes risk by reusing current transport and replay path.
- **factory/config updates** keep PI-RL available through existing CLI and parser conventions.

## Architectural Patterns

### Pattern 1: Policy-Centric Algorithm Logic

**What:** Keep loss computation and model-specific math inside policy module.
**When to use:** New RL algorithm introduces distinct objectives.
**Trade-offs:** Cleaner layering; requires policy interface consistency.

### Pattern 2: Learner Orchestration Branching

**What:** Route training behavior by `cfg.policy.type` in learner.
**When to use:** Existing loop is SAC-specific and new method differs materially.
**Trade-offs:** Fast, safe integration; can accumulate branches if not refactored later.

### Pattern 3: Transport Contract Preservation

**What:** Reuse existing actor/learner messages and transition schema.
**When to use:** New method can consume standard transition tuples.
**Trade-offs:** Lower migration cost; limits feature design to current payload model.

## Data Flow

### Request Flow

```
Actor env step
    ↓
Transition creation → transitions_queue → gRPC SendTransitions
    ↓
Learner transition_queue → ReplayBuffer → batch sampling
    ↓
Policy forward/loss → optimizer step → actor params pushed back via StreamParameters
```

### State Management

```
Policy state (learner)
    ↓ serialize actor params
gRPC stream
    ↓
Policy actor state (actor process)
```

### Key Data Flows

1. **Online loop:** actor collects transitions continuously; learner updates policy from replay.
2. **Hybrid loop (optional):** learner mixes online buffer and offline dataset-derived buffer.

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| Local dev / small runs | Keep threads/processes as configured, prioritize correctness |
| Medium training workloads | Tune queue, replay, and push frequency; monitor actor FPS |
| Large distributed workloads | Consider orchestration upgrades only after PI-RL path is stable |

### Scaling Priorities

1. **First bottleneck:** actor inference latency under PI-RL sampling complexity.
2. **Second bottleneck:** learner update throughput and replay sampling pressure.

## Anti-Patterns

### Anti-Pattern 1: Embedding PI-RL logic into actor loop

**What people do:** place training semantics in actor runtime.
**Why it's wrong:** breaks current architecture separation and maintainability.
**Do this instead:** keep actor focused on inference/collection; train in learner.

### Anti-Pattern 2: Proto/schema redesign before MVP

**What people do:** redesign transport to “future-proof.”
**Why it's wrong:** introduces high risk before proving algorithm fit.
**Do this instead:** validate with existing transition schema first.

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| Weights & Biases | Existing learner logging utility | Add PI-RL metrics incrementally |
| Hugging Face Hub (optional) | Existing model/config workflows | Keep compatibility with current save/load paths |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| `rl/actor.py` ↔ `rl/learner_service.py` | gRPC streaming | Keep message semantics stable |
| `rl/learner.py` ↔ `policies/pi_rl` | direct policy calls | Branch by `cfg.policy.type` |
| `policies/factory.py` ↔ `configs/policies.py` | registry/factory | Required for CLI instantiation |

## Sources

- LeRobot RL runtime and policy architecture files
- RLinf module map and runner/algorithm structure
- PI-RL paper and summary documents

---
*Architecture research for: LeRobot PI-RL extension*
*Researched: 2026-02-21*
