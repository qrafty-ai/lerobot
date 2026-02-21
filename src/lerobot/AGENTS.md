# CODEBASE KNOWLEDGE

## OVERVIEW
`src/lerobot` is the implementation root: configs, policies, processors, datasets, hardware integrations, and CLIs.

## STRUCTURE
```text
src/lerobot/
├── scripts/       # user-facing CLI entrypoints
├── policies/      # policy configs/models/processors + factory wiring
├── processor/     # transition pipeline + step registry
├── datasets/      # LeRobotDataset + tools + migration helpers
├── rl/            # actor/learner distributed HIL-SERL runtime
├── robots/        # hardware adapters
├── teleoperators/ # operator input devices
└── envs/          # environment configs and adapters
```

## WHERE TO LOOK
| Task | Location | Notes |
|------|----------|-------|
| Add CLI command | `scripts/` + `pyproject.toml` | Register under `[project.scripts]` |
| Add policy | `policies/<name>/` + `policies/factory.py` | Config/model/processor triplet |
| Add processor step | `processor/*.py` | Register via `ProcessorStepRegistry` |
| Update RL loop | `rl/actor.py`, `rl/learner.py` | gRPC + queue-based flow |
| Update dataset behavior | `datasets/lerobot_dataset.py` | Meta/data/video paths are coupled |

## CONVENTIONS
- Use `@parser.wrap()` for script entrypoints and config parsing.
- Use `draccus` registries for polymorphic config types.
- Keep dynamic imports in factory files to avoid loading all backends.

## ANTI-PATTERNS
- Do not add new CLI scripts without registering entry points in `pyproject.toml`.
- Do not couple script-level orchestration logic into low-level library modules.
- Do not bypass package-level factories (`policies/factory.py`, env/robot factories) for new extension points.
