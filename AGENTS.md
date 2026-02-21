# PROJECT KNOWLEDGE BASE

**Generated:** 2026-02-21 16:00 America/New_York  
**Commit:** `fedf5b4c`  
**Branch:** `feat/rl-on-lerobot`

## OVERVIEW
LeRobot is a Python robotics ML codebase: hardware control + dataset tooling + policy training/eval (IL, RL, VLA) with a `src/lerobot` package layout.

## STRUCTURE
```text
.
├── src/lerobot/        # core library code
├── tests/              # mirrored test layout + fixtures/mocks/artifacts
├── docs/               # docs source + build files
├── examples/           # runnable usage/tutorial scripts
├── .github/workflows/  # CI, nightly, release, quality
├── pyproject.toml      # packaging, deps, script entry points, lint/type config
└── Makefile            # docker + e2e test shortcuts
```

## WHERE TO LOOK
| Task | Location | Notes |
|------|----------|-------|
| Train policy | `src/lerobot/scripts/lerobot_train.py` | Main training orchestrator |
| Evaluate policy | `src/lerobot/scripts/lerobot_eval.py` | Unified eval entry point |
| Add/modify policy | `src/lerobot/policies/` + `src/lerobot/policies/factory.py` | Factory + registry pattern |
| Add/modify processors | `src/lerobot/processor/pipeline.py` + `src/lerobot/processor/*.py` | Step registry + pipeline serialization |
| RL actor/learner flow | `src/lerobot/rl/actor.py`, `src/lerobot/rl/learner.py` | Distributed HIL-SERL path |
| Dataset internals | `src/lerobot/datasets/lerobot_dataset.py` | Core dataset API |
| CLI/config parsing | `src/lerobot/configs/parser.py` | `@parser.wrap()` + plugin discovery |
| Test guardrails | `tests/conftest.py`, `tests/utils.py` | Skip decorators + shared fixtures |

## CODE MAP
| Symbol | Type | Location | Role |
|--------|------|----------|------|
| `wrap` | function | `src/lerobot/configs/parser.py` | CLI-to-config bootstrap |
| `PreTrainedConfig` | class | `src/lerobot/configs/policies.py` | Policy config registry base |
| `get_policy_class` | function | `src/lerobot/policies/factory.py` | Dynamic policy class lookup |
| `make_policy` | function | `src/lerobot/policies/factory.py` | Policy construction from config |
| `ProcessorStepRegistry` | class | `src/lerobot/processor/pipeline.py` | Registry for processor steps |
| `DataProcessorPipeline` | class | `src/lerobot/processor/pipeline.py` | Transition processing framework |
| `train` | function | `src/lerobot/scripts/lerobot_train.py` | Main train loop entry |
| `actor_cli` | function | `src/lerobot/rl/actor.py` | RL actor process entry |
| `train_cli` | function | `src/lerobot/rl/learner.py` | RL learner process entry |

## CONVENTIONS
- Python 3.10 baseline (`pyproject.toml`, pre-commit default).
- Package layout is `src/`-based (`[tool.setuptools.packages.find] where = ["src"]`).
- Config polymorphism uses `draccus` registries (`@PreTrainedConfig.register_subclass`, `@EnvConfig.register_subclass`).
- CLI entrypoints use `@parser.wrap()` for config loading and plugin injection.
- Processor extensions should use `@ProcessorStepRegistry.register(...)` for portability.
- Lint/format: Ruff with line length 110, double quotes, Google docstring style.
- Pre-commit is first-class (`pre-commit install`, `pre-commit run --all-files`).

## ANTI-PATTERNS (THIS PROJECT)
- Do not edit generated transport files (`src/lerobot/transport/services_pb2.py`, `src/lerobot/transport/services_pb2_grpc.py`).
- Do not add policy types without wiring factory/registry paths (`src/lerobot/policies/factory.py`, config registration).
- Do not mutate processor inputs in place when implementing custom steps; copy transitions first (see processor docs and patterns).
- Do not run hardware-dependent tests without skip guards (`tests/utils.py` decorators).

## UNIQUE STYLES
- Heavy optional dependency matrix via extras (`lerobot[hilserl]`, `lerobot[groot]`, etc.).
- Scripts are exported as console commands in `pyproject.toml` (`[project.scripts]`).
- Tests include large artifact fixtures under `tests/artifacts` (git-lfs aware).

## COMMANDS
```bash
pre-commit run --all-files
pytest -sv ./tests
make test-end-to-end
lerobot-train --help
lerobot-eval --help
```

## NOTES
- Pull LFS assets before full test runs: `git lfs install && git lfs pull`.
- CI has separate fast/full/nightly workflows in `.github/workflows/`.
- Very large model files exist under some policy backends; prefer surgical changes.
