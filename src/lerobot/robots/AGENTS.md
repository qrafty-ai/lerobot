# ROBOTS KNOWLEDGE

## OVERVIEW
`src/lerobot/robots` contains hardware robot adapters that implement the `Robot` interface and expose normalized observation/action contracts.

## WHERE TO LOOK
| Task | Location | Notes |
|------|----------|-------|
| Base interface | `robot.py` | Required methods (`connect`, `get_observation`, `send_action`, `disconnect`) |
| Config registry | `config.py` | `RobotConfig` + `@register_subclass` patterns |
| Factory path | `utils.py:make_robot_from_config` | New robots must be discoverable from config |
| Motor-based patterns | `so_follower/`, `koch_follower/` | Calibration + motors bus conventions |
| SDK-based patterns | `reachy2/`, `unitree_g1/` | Optional dependency guards |

## CONVENTIONS
- Register robot config classes in draccus registry with stable names.
- Keep observation keys/features aligned with shared constants (`obs.*`, motor key conventions).
- Use connection-state decorators and safe action helpers from utility modules.

## ANTI-PATTERNS
- Do not bypass calibration or safety-bound checks for motor-driven robots.
- Do not hardcode host-specific serial paths in reusable configs.
- Do not change observation/action key names without updating downstream processors/tests.

## NOTES
- Hardware code should remain testable with mocks; avoid direct side effects at import time.
- See `tests/robots/`, `tests/mocks/`, and `tests/utils.py` for guard conventions.

## COMMANDS
- Robot-focused tests: `pytest -sv tests/robots`
- Motor-focused tests: `pytest -sv tests/motors`
