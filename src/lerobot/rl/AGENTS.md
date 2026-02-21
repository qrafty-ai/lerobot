# RL KNOWLEDGE

## OVERVIEW
`src/lerobot/rl` implements distributed online RL (HIL-SERL style): actor process, learner process, replay buffers, gRPC transport, and related utilities.

## WHERE TO LOOK
| Task | Location | Notes |
|------|----------|-------|
| Start learner | `learner.py:train_cli` | gRPC service + training loop entry |
| Start actor | `actor.py:actor_cli` | env interaction + transition streaming |
| gRPC server behavior | `learner_service.py` | `SendTransitions`, `SendInteractions`, `StreamParameters` |
| Buffering | `buffer.py` | ReplayBuffer + dataset conversion |
| Runtime env | `gym_manipulator.py` | HIL-specific env loop/processors |
| Message contract | `../transport/services.proto` | actor↔learner RPC schema |

## CONVENTIONS
- Both actor and learner use `@parser.wrap()` with `TrainRLServerPipelineConfig`.
- Concurrency can be threads or processes; guard behavior through `use_threads(cfg)`.
- Queue payloads are serialized bytes for cross-process/gRPC transfer.

## ANTI-PATTERNS
- Do not change proto message contracts without updating service/client handling.
- Do not assume single-process local execution; actor/learner are decoupled services.
- Do not introduce RL algorithm logic only in actor; training semantics belong in learner.

## NOTES
- Current online loop is SAC-centric in learner update logic; non-SAC methods need explicit adaptation.
- Integration tests live under `tests/rl/` and `tests/utils/test_replay_buffer.py`.

## COMMANDS
- Start learner: `python -m lerobot.rl.learner --config_path <path-to-train-config.json>`
- Start actor: `python -m lerobot.rl.actor --config_path <path-to-train-config.json>`
