# Phase 1: PI-RL Recipe Foundation - Context

**Gathered:** 2026-02-22
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 1 delivers recipe-level PI-RL selection and validation so PI-RL is enabled independently from policy type,
with XVLA as the only eligible target in this phase. This phase clarifies selection, validation, and user-facing
behavior at startup; it does not add learner algorithm internals beyond recipe-mode routing.

</domain>

<decisions>
## Implementation Decisions

### Entrypoint contract
- PI-RL must be activated through an explicit top-level recipe field, following VERL-style explicit selection.
- Canonical user-facing recipe value is strict `pi-rl`.
- Actor and learner must use one shared config file path for recipe selection.
- If PI-RL recipe mode is not provided, default behavior remains existing non-PI-RL training path.
- Any actor/learner recipe mismatch is a hard failure.

### Policy eligibility
- Phase 1 allows only XVLA for `pi-rl` recipe mode.
- Using a non-eligible policy with `pi-rl` must hard fail and print the allowed policy list.
- Eligibility validation happens as a preflight check before actor/learner startup.
- Post-phase expansion should be controlled by a policy capability flag.

### Variant controls
- Phase 1 exposes both variants: `flow-noise` and `flow-sde`.
- Variant is required when `pi-rl` is selected (no implicit default).
- Tuning surface remains minimal in Phase 1 (must-have knobs only).
- Invalid or missing variant-specific knobs must hard fail with concrete fix hints.

### Selection feedback
- Invalid config errors must be actionable and include exact field + invalid value + fix guidance.
- Valid config should print a concise preflight summary (recipe, policy, variant, config path).
- Incorrect recipe spelling must fail and suggest canonical `pi-rl`.
- If actor/learner config paths differ, error must include both paths and stop execution.

### Claude's Discretion
- Exact naming of minimal variant knobs in Phase 1.
- Preflight summary output format and ordering.
- Exact wording style for validation/error messages.

</decisions>

<specifics>
## Specific Ideas

- "Follow VERL implementation" is a required guiding principle for recipe activation ergonomics.
- Strict explicit mode is preferred over implicit detection or fallback behavior.

</specifics>

<deferred>
## Deferred Ideas

None - discussion stayed within phase scope.

</deferred>

---

*Phase: 01-pi-rl-recipe-foundation*
*Context gathered: 2026-02-22*
