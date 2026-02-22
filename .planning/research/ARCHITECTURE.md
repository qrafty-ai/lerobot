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
| Recipe/config layer | Recipe mode selection and routing independent of policy type | `TrainRLServerPipelineConfig` + learner recipe dispatch |

## Recommended Project Structure

```
src/
└── lerobot/
    ├── policies/
    │   └── xvla/                        # first validated flow-matching target for PI-RL recipe
    ├── rl/
    │   ├── learner.py                   # add recipe-mode PI-RL training branch
    │   └── actor.py                     # preserve actor sync contract
    └── configs/
        └── train.py                     # recipe-level knobs and selection
```

### Structure Rationale

- **recipe layer in `rl/learner.py` + `configs/train.py`** keeps PI-RL orchestration explicit and policy-agnostic.
- **XVLA-first validation on LIBERO** provides a concrete simulation-first integration target before broad rollout.
- **minimal policy-factory changes** avoid misclassifying PI-RL as a standalone policy type.

## Architectural Patterns

### Pattern 1: Recipe-Centric Orchestration

**What:** Keep PI-RL mode selection and update scheduling in recipe-level learner logic.
**When to use:** Algorithm is a training recipe applicable across multiple policy families.
**Trade-offs:** Better reuse across policies; requires a clear policy capability contract.

### Pattern 2: Learner Orchestration Branching

**What:** Route training behavior by recipe mode in learner.
**When to use:** Existing loop is SAC-specific and PI-RL should not be encoded as a policy identity.
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
3. **Simulation validation loop:** run LIBERO single-suite smoke then multi-suite matrix and log per-suite success rates.

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
| LIBERO benchmark env | `lerobot-eval --env.type=libero` | Primary validation surface before real-robot testing |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| `rl/actor.py` ↔ `rl/learner_service.py` | gRPC streaming | Keep message semantics stable |
| `rl/learner.py` ↔ flow-matching policies (`policies/xvla` first) | direct policy calls | Branch by recipe mode, not policy type |
| `configs/train.py` ↔ `rl/learner.py` | config-driven dispatch | Required for recipe selection and variant controls |

## Sources

- LeRobot RL runtime and policy architecture files
- RLinf module map and runner/algorithm structure
- PI-RL paper and summary documents
- LIBERO guidance in `docs/source/libero.mdx`

---
*Architecture research for: LeRobot PI-RL extension*
*Researched: 2026-02-21*
