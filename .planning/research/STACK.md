# Stack Research

**Domain:** Online RL extension for flow-based VLA training in existing robotics ML codebase
**Researched:** 2026-02-21
**Confidence:** HIGH

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Python | 3.10 | Runtime language for LeRobot training stack | Existing project baseline and ecosystem compatibility |
| PyTorch | 2.x (project-managed) | Policy/model training and differentiable objectives | Already used in LeRobot and required for PI-RL style loss integration |
| Draccus | project-managed | Structured config registry and CLI parsing | LeRobot uses registry-driven configs and `@parser.wrap()` |
| gRPC + Protobuf transport | project-managed | Actor/learner service communication | Existing stable message path in `src/lerobot/rl/learner_service.py` |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| NumPy | project-managed | Numeric preprocessing and transition shaping | Environment interaction and state/action transforms |
| Weights & Biases | project-managed | Metrics logging for online training | Enable in long PI-RL runs for policy/optimization diagnostics |
| OpenCV (optional) | project-managed | Camera/observation handling in RL runtime paths | Required only in camera-enabled rollouts |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| Ruff + pre-commit | Lint/format and policy checks | Aligns with repository standards and CI guardrails |
| Pytest | Unit and integration testing | Use `tests/rl` + policy tests for regression coverage |
| GitHub Actions (existing) | CI verification | Keep PI-RL additions compatible with existing workflows |

## Installation

```bash
# Core project deps
pip install -e .

# Optional extras often needed for advanced RL/vla flows
pip install -e ".[hilserl]"

# Development checks
pre-commit run --all-files
pytest -sv tests/rl
```

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| LeRobot-native incremental PI-RL integration | Full RLinf runtime adoption | Only if project decides to replace orchestration model entirely |
| Existing gRPC actor/learner transport | New custom RPC/event bus | Only if scaling requirements exceed current transport boundaries |
| Draccus config registration | Hydra-only migration | Only in a broader config-system refactor milestone |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| Hard-forking RLinf into LeRobot | High maintenance burden and architectural drift | Port only PI-RL recipe primitives needed by LeRobot |
| Transport/proto redesign in MVP phase | Adds risk without proving PI-RL value | Keep existing service contract and add algorithm-specific payload logic inside learner |
| Benchmark-chasing as first deliverable | Expensive and not necessary to validate integration | First validate functional training recipe and safety/regression coverage |

## Stack Patterns by Variant

**If targeting minimal PI-RL MVP:**
- Use existing actor/learner runtime with new policy/loss integration points.
- Because this isolates algorithm work from infra churn.

**If targeting broader PI-RL parity with RLinf:**
- Add configurable log-prob/advantage pipeline and variant-specific training toggles.
- Because Flow-Noise and Flow-SDE have distinct update semantics.

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|-----------------|-------|
| LeRobot Python 3.10 baseline | PyTorch 2.x + existing project deps | Respect project lock and CI constraints |
| Draccus config registry | `PreTrainedConfig.register_subclass` patterns | Required for parser and factory compatibility |

## Sources

- arXiv `2510.25889` + arXiv HTML — PI-RL method framing as online RL fine-tuning.
- RLinf repository (`RLinf/RLinf`) — reference implementation structure and algorithm modules.
- Private summary: `qrafty-ai/research/paper_codes/2510.25889_pi_rl_summary.md`.
- Local codebase inspection under `src/lerobot/rl`, `src/lerobot/policies`, and `src/lerobot/configs`.

---
*Stack research for: LeRobot PI-RL extension*
*Researched: 2026-02-21*
