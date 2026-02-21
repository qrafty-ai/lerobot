# TESTS KNOWLEDGE

## OVERVIEW
`tests/` mirrors runtime modules and adds shared fixtures/mocks/artifacts for hardware, dataset, processor, policy, and RL coverage.

## WHERE TO LOOK
| Task | Location | Notes |
|------|----------|-------|
| Global pytest config | `conftest.py` | plugin fixtures + typed contract helpers |
| Skip/dependency guards | `utils.py` | `require_*` decorators for env/device/packages |
| Processor coverage | `processor/` | extensive pipeline + step behavior checks |
| Policy coverage | `policies/` | backend-specific tests by policy family |
| RL integration tests | `rl/` | actor/learner/service/queue tests |
| Shared fixtures/mocks | `fixtures/`, `mocks/` | test dependency injection |

## CONVENTIONS
- Use `pytest` naming (`test_*.py`, `test_*` functions).
- Guard optional/hardware dependencies with `tests/utils.py` decorators.
- Keep tests module-aligned with corresponding `src/lerobot/*` areas.

## ANTI-PATTERNS
- Do not add hardware-dependent tests without skip guards.
- Do not assume CUDA is always available; tests are device-conditional.
- Do not mutate artifact fixtures in-place; treat `tests/artifacts` as test data inputs.

## NOTES
- Full suite expects git-lfs assets present (`git lfs pull`).
- CI splits fast/full/nightly workflows; avoid tests that only pass in one mode unless explicitly marked.

## COMMANDS
- Full test run: `pytest -sv ./tests`
- Fast iteration by area: `pytest -sv tests/processor` (or `tests/policies`, `tests/rl`)
