# TELEOPERATORS KNOWLEDGE

## OVERVIEW
`src/lerobot/teleoperators` implements human input devices (leader arms, gamepad, keyboard, phone, glove) via a common `Teleoperator` interface.

## WHERE TO LOOK
| Task | Location | Notes |
|------|----------|-------|
| Base interface | `teleoperator.py` | `get_action`, `send_feedback`, feature contracts |
| Config registry | `config.py` | `TeleoperatorConfig` subclass registration |
| Factory path | `utils.py:make_teleoperator_from_config` | Entry point from runtime configs |
| Event contract | `utils.py:TeleopEvents` | Intervention/success/failure flags used by RL + recording |
| Device implementations | `gamepad/`, `keyboard/`, `so_leader/`, `phone/` | Device-specific action semantics |

## CONVENTIONS
- Keep action output schema consistent with robot-side processors.
- Gate optional dependencies using import utilities for device-specific backends.
- Keep teleop actions explicit and deterministic (no hidden state changes).

## ANTI-PATTERNS
- Do not emit incompatible action keys without corresponding processor updates.
- Do not assume feedback channels exist for all devices.
- Do not introduce blocking IO in hot polling loops without timeout control.

## NOTES
- RL/recording workflows consume teleop events; check compatibility with `gym_manipulator` and actor loop paths.

## COMMANDS
- Teleoperator tests: `pytest -sv tests/teleoperators`
- Smoke list supported teleops: `python -c "from lerobot import available_teleoperators; print(available_teleoperators)"`
