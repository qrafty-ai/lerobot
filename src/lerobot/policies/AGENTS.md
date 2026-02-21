# POLICIES KNOWLEDGE

## OVERVIEW
`src/lerobot/policies` contains policy families (IL, RL, VLA) implemented as config + model + processor modules, wired through a central factory.

## WHERE TO LOOK
| Task | Location | Notes |
|------|----------|-------|
| Add new policy type | `configuration_<name>.py` | Must use `@PreTrainedConfig.register_subclass("<name>")` |
| Implement model | `modeling_<name>.py` | Policy class is resolved by naming convention in factory |
| Implement IO transforms | `processor_<name>.py` | Must expose `make_<name>_pre_post_processors` |
| Wire built-in policy | `factory.py` | Update `get_policy_class` + `make_policy_config` branches |
| Plugin policy path | `factory.py:_get_policy_cls_from_policy_name` | Dynamic import fallback for third-party packages |

## CONVENTIONS
- Folder pattern per policy: config/model/processor (+ README).
- Config classes derive from `PreTrainedConfig`; policy classes derive from `PreTrainedPolicy`.
- Keep heavy backend imports local in factory branches (dynamic import pattern).

## ANTI-PATTERNS
- Do not add a policy without registry + factory + processor factory coverage.
- Do not break naming conventions (`*Config` -> `*Policy`, `configuration_` -> `modeling_`).
- Do not hardcode dataset feature assumptions; use `dataset_to_policy_features`/`env_to_policy_features` flow via `make_policy`.

## NOTES
- Some backends are very large (`wall_x`, `xvla`, `groot`); prefer narrow edits and targeted tests.
- `SAC` and `TDMPC` live here but online RL orchestration is in `src/lerobot/rl/`.

## COMMANDS
- Inspect policy config wiring: `python -c "from lerobot.policies.factory import make_policy_config; print(make_policy_config('act'))"`
- Run policy-focused tests: `pytest -sv tests/policies`
