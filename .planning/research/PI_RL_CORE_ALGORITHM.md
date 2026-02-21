# PI-RL Core Algorithm Logic (Recipe Layer)

**Purpose:** Canonical record of PI-RL core algorithm semantics for LeRobot implementation.
**Scope:** Training recipe logic only (not a policy type), applicable to flow-matching policies.
**First validation target:** XVLA.
**Last updated:** 2026-02-21

## Positioning

- PI-RL is an **online RL fine-tuning recipe** for flow-based VLA policies.
- In LeRobot terms, PI-RL should be selected as a **recipe mode** in training config/routing.
- PI-RL can become hybrid when optional offline data mixing is enabled.

## Inputs and Contracts

1. **Policy contract (flow-matching):** policy must expose inference action generation and training-time
   loss-relevant outputs needed by PI-RL updates.
2. **Runtime contract:** actor/learner transport and transition schema remain unchanged for MVP
   (`state`, `action`, `reward`, `next_state`, `done`, `truncated`, optional metadata).
3. **Config contract:** recipe mode + variant knobs (Flow-Noise / Flow-SDE style behavior),
   independent from policy type selection.

## Core Recipe Logic (Reference Flow)

1. Initialize from a supervised/aligned flow-matching checkpoint (XVLA first).
2. Run actor rollouts to collect online transitions using current policy parameters.
3. Push transitions to learner through existing queue/gRPC pipeline.
4. Build training batches from online replay (and optional offline replay in hybrid mode).
5. Compute PI-RL recipe objectives for chosen variant:
   - **Flow-Noise path:** tractable log-likelihood-oriented objective via noise modeling.
   - **Flow-SDE path:** denoising-interaction coupled objective for exploration and policy improvement.
6. Apply optimizer updates on learner-side trainable components according to PI-RL schedule.
7. Periodically publish actor-required parameters back to actor via existing parameter stream.
8. Continue rollout-update loop until stopping criteria (steps, convergence, budget, or quality thresholds).
9. Save checkpoints and metrics continuously; support resume from checkpoint.

## Pseudocode (Recipe-Level)

```text
initialize policy_theta from flow-matching checkpoint (XVLA baseline)
initialize learner optimizers, replay buffers, recipe_mode=pi_rl, variant in {flow_noise, flow_sde}

for each interaction cycle:
  actor collects trajectories with current theta
  send transitions -> learner transport queues

  learner ingests transitions into online replay
  batch <- sample(online replay [, offline replay])

  if variant == flow_noise:
      loss <- pi_rl_flow_noise_objective(batch, policy_theta)
  else if variant == flow_sde:
      loss <- pi_rl_flow_sde_objective(batch, policy_theta)

  theta <- optimizer_step(theta, loss)
  if publish_interval reached:
      stream actor-compatible params(theta_actor) to actor

  checkpoint + log metrics at configured intervals
```

## LeRobot Mapping (Where Logic Lives)

- **Recipe dispatch/orchestration:** `src/lerobot/rl/learner.py` (branch by recipe mode).
- **Actor rollout and parameter sync:** `src/lerobot/rl/actor.py`.
- **Transport contracts:** `src/lerobot/rl/learner_service.py` and transport proto pipeline.
- **Replay behavior:** `src/lerobot/rl/buffer.py` and learner replay initialization paths.
- **Flow-matching policy target (first):** `src/lerobot/policies/xvla/`.

## Verification Targets

- XVLA + PI-RL recipe mode runs end-to-end without transport/schema changes.
- Learner recipe branch updates and publishes parameters successfully.
- SAC path remains functional and non-regressed.
- Checkpoint/resume and logging work for PI-RL runs.

## Sources

- arXiv: `2510.25889` (PI-RL framing and variants).
- RLinf reference implementation structure (runner/actor/loss pipelines).
- Internal planning artifacts in `.planning/research/` and LeRobot RL codebase mapping.
