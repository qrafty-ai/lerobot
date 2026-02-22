# Phase 2: Learner PI-RL Training Path - Research

**Researched:** 2026-02-22
**Domain:** Distributed online RL learner/actor runtime + flow-matching VLA fine-tuning (XVLA) + LIBERO
**Confidence:** MEDIUM

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

### Run profile
- Default profile is smoke-first for fast execution and quick failure detection.
- Longer benchmarking-oriented runs are explicit opt-in rather than default behavior.

### Runtime launch path
- Primary runtime UX is explicit two-terminal orchestration using separate learner and actor commands.
- Launch style follows HILSERL_SIM-style process separation for clarity and debuggability.

### LIBERO training scope
- Default Phase 2 smoke suite target is `libero_10`.
- Suite override remains user-configurable, but `libero_10` is the documented baseline for sign-off.

### Phase gate behavior
- Phase 2 gate requires PI-RL training smoke completion only.
- Evaluation is not a Phase 2 gate; full evaluation matrix remains Phase 3 scope.

### Failure behavior
- Resume/checkpoint metadata mismatch is a hard-fail condition.
- Errors must be actionable and identify mismatched fields and expected values.

### Checkpoint policy
- Use fixed learner-step checkpoint cadence plus a rolling "latest" pointer.
- Resume path must read from existing conventions without introducing a new checkpoint format.

### Claude's Discretion
- Exact default smoke step count and checkpoint interval values.
- Console wording/order for launch and mismatch diagnostics.
- Minimal additional training telemetry fields shown during smoke runs.

### Deferred Ideas (OUT OF SCOPE)

None - discussion stayed within phase scope.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| LRN-01 | User can run learner in PI-RL recipe mode and execute a PI-RL-specific optimization branch | `src/lerobot/rl/learner.py` is currently SAC-centric (assumes SACPolicy + SACConfig fields). Phase 2 must add a `recipe=pi-rl` branch that trains a flow-matching policy (XVLA) without SAC-only assumptions. |
| LRN-02 | User can train PI-RL online using existing replay-buffer transition schema and queue/gRPC flow | Transport (`src/lerobot/rl/learner_service.py`, `src/lerobot/rl/queue.py`, `src/lerobot/transport/services.proto`) and transition schema (`Transition` with `state/action/reward/next_state/done/truncated/complementary_info`) already exist and can be reused unchanged. |
| LRN-03 | User can checkpoint and resume PI-RL recipe training using existing checkpoint conventions | Checkpoint layout and symlink conventions are already standardized by `src/lerobot/utils/train_utils.py` (`checkpoints/<step>/pretrained_model/`, `checkpoints/last`). Learner also has resume orchestration in `src/lerobot/rl/learner.py:handle_resume_logic` + `load_training_state`. PI-RL must store/validate recipe metadata and keep actionable mismatch errors. |
| LRN-04 | User can execute a self-contained LIBERO training smoke run for PI-RL (XVLA target) using documented orchestration | LIBERO env exists (`src/lerobot/envs/libero.py`, extra `lerobot[libero]`). XVLA policy exists (`src/lerobot/policies/xvla/`). Phase 2 must bridge the current RL runtime (actor/learner) to work with `EnvConfig=libero` and `policy.type=xvla` under `recipe=pi-rl`, including language tokenization plumbing needed by XVLA. |
</phase_requirements>

## Summary

Phase 2 planning hinges on one practical fact: the current distributed RL runtime (`src/lerobot/rl/actor.py`, `src/lerobot/rl/learner.py`) is not just "SAC by default"—it directly reads many SAC-only config fields (e.g. `cfg.policy.online_steps`, buffer capacities, concurrency, UTD ratio) and treats the policy as `SACPolicy` with an `.actor` module for parameter streaming. XVLA (flow-matching VLA) is a `PreTrainedPolicy` without those SAC-only fields, so PI-RL cannot be implemented as a small learner-only patch unless the runtime is made recipe-driven and policy-agnostic.

The good news for planning: Phase 1 already added strict recipe validation + config hash/path metadata (`validate_recipe_runtime_preflight`, `build_recipe_preflight_context`, `PI_RL_CONFIG_*` keys) and the transport/replay backbone is reusable. The planning focus should be: (1) introduce a PI-RL learner update path that trains `XVLAPolicy` using the existing transition schema, (2) introduce minimal runtime config for PI-RL runs (steps, buffer size, concurrency, push frequency) outside SAC policy config, (3) make LIBERO + XVLA observations compatible with XVLA's required language-token inputs so the smoke run is feasible.

**Primary recommendation:** Plan Phase 2 as “generalize RL runtime enough to run XVLA + PI-RL smoke on LIBERO” (not just “add a new loss”), and keep SAC behavior unchanged by isolating SAC assumptions behind a legacy branch.

## Project Context Discovered

- `CLAUDE.md`: not found in repository root (no additional project-specific instructions).
- `.agents/skills/`: not found (no project-specific skills to follow).

## Standard Stack

### Core
| Component | Where | Purpose | Confidence |
|---|---|---|---|
| Draccus config + `@parser.wrap()` | `src/lerobot/configs/parser.py` | Uniform CLI/config loading for scripts | HIGH |
| Distributed RL transport (gRPC + queues) | `src/lerobot/rl/learner_service.py`, `src/lerobot/rl/actor.py` | Actor↔learner transitions, interactions, parameter streaming | HIGH |
| Transition schema | `src/lerobot/utils/transition.py`, `src/lerobot/transport/utils.py` | Serialize transitions without proto changes | HIGH |
| ReplayBuffer | `src/lerobot/rl/buffer.py` | Online storage/sampling on learner | HIGH |
| Checkpoint/resume conventions | `src/lerobot/utils/train_utils.py`, `src/lerobot/rl/learner.py` | Persist policy + optimizer state; resume with `checkpoints/last` | HIGH |
| XVLA policy | `src/lerobot/policies/xvla/modeling_xvla.py` | Flow-matching policy that can compute a supervised loss on (obs, action) | HIGH |
| LIBERO env | `src/lerobot/envs/libero.py` | Smoke benchmark target (`libero_10`) | HIGH |

### Supporting
| Component | Where | Purpose | Notes |
|---|---|---|---|
| PI-RL recipe config and validation | `src/lerobot/configs/train.py`, `src/lerobot/configs/types.py` | Gate recipe values + store PI-RL hyperparams (`pirl.*`) | Phase 1 complete; Phase 2 must *use* these fields |
| TokenizerProcessorStep | `src/lerobot/processor/tokenizer_processor.py` | Create `observation.language.tokens` from `TransitionKey.COMPLEMENTARY_DATA['task']` | Needed for XVLA on LIBERO |
| LIBERO + transformers extras | `pyproject.toml` optional deps | Install deps (`lerobot[libero]`, `lerobot[xvla]`) | LIBERO extra pulls `hf-libero`, XVLA needs transformers |

## Architecture Patterns

### Pattern 1: Recipe Preflight as the Switch (already in place)

- Use `validate_recipe_runtime_preflight(cfg)` at process start.
- Use `build_recipe_preflight_context(cfg)` to compute `recipe/policy_type/variant/config_path/config_hash`.
- Use `log_recipe_preflight_summary(..., role=...)` for deterministic startup logs.

Relevant code:
- `src/lerobot/configs/train.py`: `RecipePreflightContext`, `validate_recipe_runtime_preflight`, `compute_runtime_config_hash`.
- `src/lerobot/scripts/lerobot_train.py`: hard-fails on `recipe=pi-rl` and directs users to RL runtime.

Planning implication:
- The Phase 2 plan should treat “recipe switch” as the *entry point* to PI-RL behavior, not policy type checks scattered through the runtime.

### Pattern 2: Config Sync and Mismatch Hard-Fail (already in place)

- Learner adds config metadata on first parameter push:
  - `src/lerobot/rl/learner.py:push_actor_policy_to_queue(... include_config_metadata=True ...)`
- Actor validates on first load and raises actionable mismatch:
  - `src/lerobot/rl/actor.py:update_policy_parameters` compares `actor_preflight.config_path/hash` vs learner payload.

Planning implication:
- Phase 2 “resume/checkpoint metadata mismatch” should follow the same style: explicit fields + expected/actual in the exception message.

### Pattern 3: Checkpoint/Resume Uses Shared Train Conventions (already in place)

- Directory structure and symlink:
  - `src/lerobot/utils/train_utils.py:save_checkpoint`, `update_last_checkpoint`.
- Learner resume:
  - `src/lerobot/rl/learner.py:handle_resume_logic` loads config from `checkpoints/last/pretrained_model/train_config.json`.
  - `src/lerobot/rl/learner.py:load_training_state` loads optimizer(s) + step.

Planning implication:
- PI-RL must reuse `save_checkpoint` (same format) and only extend “training state” minimally (e.g. recipe/variant fields) if needed.

### Pattern 4: Separate “RL Runtime Config” from “Policy Config” (needed for PI-RL)

Observed coupling:
- `src/lerobot/rl/actor.py` and `src/lerobot/rl/learner.py` read SAC-only config fields like:
  - `cfg.policy.online_steps`, `cfg.policy.online_step_before_learning`, `cfg.policy.utd_ratio`
  - `cfg.policy.online_buffer_capacity`, `cfg.policy.offline_buffer_capacity`
  - `cfg.policy.concurrency.*`, `cfg.policy.actor_learner_config.*`

XVLA config (`src/lerobot/policies/xvla/configuration_xvla.py`) does not provide these.

Planning implication:
- Phase 2 should introduce a minimal runtime config surface in `TrainRLServerPipelineConfig` (or another config object referenced by it) for:
  - total interaction steps (actor)
  - total optimization steps (learner)
  - replay buffer capacity
  - concurrency (threads vs processes)
  - parameter push frequency / queue timeouts
- Keep backward compatibility by mapping legacy SAC fields when `policy.type == 'sac'`.

## Key Technical Gaps to Account For (Critical for Planning)

### Gap A: XVLA requires language tokens, but LIBERO env/features do not expose them by default

- XVLA forward path requires `observation.language.tokens` (`OBS_LANGUAGE_TOKENS`). See `src/lerobot/policies/xvla/modeling_xvla.py`.
- LIBERO env observation (`src/lerobot/envs/libero.py`) returns pixels + robot_state, but does not include task language in observation.
- `TokenizerProcessorStep` can generate tokens, but it expects a task string in `TransitionKey.COMPLEMENTARY_DATA['task']` (not in observation). See `src/lerobot/processor/tokenizer_processor.py`.

Planning implication:
- The smoke run plan must include plumbing to carry the LIBERO task description into the transition complementary data and add a tokenizer step in the env/policy preprocessing pipeline.

### Gap B: `make_policy(... env_cfg=LiberoEnv ...)` will not infer language-token features automatically

- `make_policy` infers `cfg.input_features` from `env_to_policy_features(env_cfg)` when `cfg.input_features` is empty. See `src/lerobot/policies/factory.py`.
- `LiberoEnv` feature map does not include language tokens (see `src/lerobot/envs/configs.py`), so naive inference omits language features.

Planning implication:
- Either the training config must explicitly set XVLA input features to include language tokens, or the LIBERO env config must declare language-token features so inference includes them.

### Gap C: Parameter streaming assumes `.actor` submodule

- Learner pushes `policy.actor.state_dict()`.
- Actor loads into `policy.actor.load_state_dict(...)`.

Planning implication:
- For XVLA, parameter sync must switch to streaming the whole policy state dict (or an XVLA-specific subset) while keeping SAC behavior unchanged.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---|---|---|---|
| Recipe parsing/validation | Ad-hoc argparse checks | `validate_recipe_runtime_preflight` | Already provides canonical errors + deterministic summary |
| Actor/learner mismatch detection | New side channel | Existing `PI_RL_CONFIG_*` metadata tensors | Already tested (`tests/rl/test_recipe_config_sync.py`) |
| Checkpoint format | A new PI-RL checkpoint layout | `save_checkpoint` + `checkpoints/last` symlink | Resume/readability + matches existing tooling |
| Tokenization | Custom string→tokens per-policy code | `TokenizerProcessorStep` | Centralized, feature-transform aware, consistent with other VLA policies |
| Transition transport | Proto changes for PI-RL | Reuse existing transition bytes payload | Requirements explicitly exclude proto redesign |

## Common Pitfalls

### Pitfall 1: Thinking “learner-only change” is enough

What goes wrong:
- XVLA + PI-RL can’t run because actor/learner assume SACConfig fields and `.actor` module.

How to avoid (planning):
- Make “runtime generalization” an explicit work item (config surface + parameter streaming + env loop path for LIBERO).

### Pitfall 2: Missing language tokens during LIBERO smoke

What goes wrong:
- XVLA throws `KeyError`/`ValueError` because `observation.language.tokens` is absent.

How to avoid (planning):
- Ensure the pipeline adds `TransitionKey.COMPLEMENTARY_DATA['task']` and runs `TokenizerProcessorStep` so tokens are present in observations before calling `policy.select_action` and before storing transitions.

### Pitfall 3: Resume works but silently changes semantics

What goes wrong:
- Resuming loads checkpoint config but runtime prints confusing information or actor/learner mismatch errors are not actionable.

How to avoid (planning):
- On resume, validate recipe/variant/config hash/path and raise errors listing expected vs actual fields (per Locked Decisions).

## Code Examples (Verified in This Codebase)

### Recipe preflight + config hash/path

```python
from lerobot.configs.train import validate_recipe_runtime_preflight, build_recipe_preflight_context

preflight = validate_recipe_runtime_preflight(cfg)
ctx = build_recipe_preflight_context(cfg)
# ctx has: recipe, policy_type, variant, config_path, config_hash
```

### Actor/learner config mismatch hard-fail

- Learner embeds metadata (uint8 tensors) into the parameter payload:
  - `src/lerobot/rl/learner.py:push_actor_policy_to_queue`
- Actor validates on first sync:
  - `src/lerobot/rl/actor.py:update_policy_parameters`

Tests:
- `tests/rl/test_recipe_config_sync.py`

### TokenizerProcessorStep expects complementary task text

```python
from lerobot.processor.tokenizer_processor import TokenizerProcessorStep

# TokenizerProcessorStep.get_task() reads:
# transition[TransitionKey.COMPLEMENTARY_DATA]["task"]
# and writes:
# observation["observation.language.tokens"]
# observation["observation.language.attention_mask"]
```

### Checkpoint conventions to reuse

```python
from lerobot.utils.train_utils import get_step_checkpoint_dir, save_checkpoint, update_last_checkpoint

checkpoint_dir = get_step_checkpoint_dir(cfg.output_dir, total_steps, step)
save_checkpoint(checkpoint_dir=checkpoint_dir, step=step, cfg=cfg, policy=policy, optimizer=optimizers)
update_last_checkpoint(checkpoint_dir)
```

## State of the Art (in this repo)

| Area | Current State | Planning Consequence |
|---|---|---|
| Recipe gating | Strict canonical `pi-rl` + variant validation exists in `TrainPipelineConfig.validate()` | Phase 2 should *not* add alternative spellings or bypass this gating |
| Actor/learner safety | Config path/hash metadata sync exists | Extend the same “hard-fail mismatch” philosophy to resume/checkpoint checks |
| RL runtime | Stable for SAC + HILSerl robot env | PI-RL requires decoupling runtime from SAC assumptions |
| LIBERO env | Present and supports `libero_10` default task suite | Phase 2 must make RL runtime capable of using it |

## Open Questions (Need Answers Before Final PLAN.md)

1. **What is the minimal PI-RL optimization objective for smoke-first?**
   - Known: XVLA already implements a supervised flow-matching loss on (obs, action) via `XVLAPolicy.forward`.
   - Unknown: whether Phase 2 is expected to implement full piRL (Flow-Noise/Flow-SDE likelihood + PPO) or a simpler advantage-weighted flow-matching update.
   - Recommendation: plan the code so the learner has a clean `pirl_update_step(...)` interface; start with advantage-weighted flow-matching (smoke) and leave room for a later PPO-style upgrade.

2. **Where should PI-RL runtime knobs live?**
   - Known: SAC-only knobs currently live in `SACConfig`, blocking XVLA.
   - Unknown: whether to add a new `cfg.rl` section to `TrainRLServerPipelineConfig` or reuse existing `TrainPipelineConfig.steps/log_freq/save_freq/batch_size` fields.
   - Recommendation: use existing top-level `TrainPipelineConfig` fields where possible (smoke-first), and introduce a minimal RL-runtime sub-config only for values that don't exist yet (buffer sizes, concurrency, push frequency).

3. **How will LIBERO task language be injected into transitions?**
   - Known: `LiberoEnv` has `self.task_description`, but it is not returned in obs.
   - Unknown: whether to add language to observation directly or to complementary_data for tokenizer processing.
   - Recommendation: prefer complementary_data + `TokenizerProcessorStep` (fits existing processor contract and keeps observation tensors device-consistent).

## Sources

### Primary (HIGH confidence)
- `src/lerobot/rl/learner.py` (current learner loop + checkpoint/resume + config metadata injection)
- `src/lerobot/rl/actor.py` (current actor loop + config metadata hard-fail)
- `src/lerobot/configs/train.py` (PI-RL recipe config + preflight context)
- `src/lerobot/policies/xvla/modeling_xvla.py` (XVLA loss/predict interface, requires language tokens)
- `src/lerobot/envs/libero.py` and `src/lerobot/envs/configs.py` (LIBERO env + default `libero_10`)
- `src/lerobot/processor/tokenizer_processor.py` (task→tokens plumbing)

### Secondary (MEDIUM confidence)
- piRL paper (for Flow-Noise/Flow-SDE conceptual grounding): https://arxiv.org/html/2510.25889v3

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH (verified in repo + `pyproject.toml` extras)
- Architecture constraints/couplings: HIGH (direct code reads)
- PI-RL algorithm details: MEDIUM (paper is clear, but repo’s current config surface suggests a smoke-first simplification)

**Valid until:** 2026-03-22 (revisit if PI-RL objective/algorithm is clarified or Phase 2 scope shifts)
