# Phase 2: Learner PI-RL Training Path - Context

**Gathered:** 2026-02-22
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 2 delivers learner-side PI-RL optimization behavior and checkpoint/resume support while reusing the
existing actor/learner transport and replay flow. Scope is limited to recipe-driven learner behavior,
flow-matching policy contract integration (XVLA first), and LIBERO training smoke execution; evaluation
benchmark gating remains in Phase 3.

</domain>

<decisions>
## Implementation Decisions

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

</decisions>

<specifics>
## Specific Ideas

- Use HILSERL_SIM-style operational flow (`python -m lerobot.rl.learner` and `python -m lerobot.rl.actor`) as the user-facing baseline.
- Keep PI-RL as a recipe-layer behavior independent from policy taxonomy, with XVLA as the first validated target.
- Keep LIBERO setup self-contained for reproducibility (`pip install -e ".[libero]"` and `MUJOCO_GL=egl`) in downstream runbooks.

</specifics>

<deferred>
## Deferred Ideas

None - discussion stayed within phase scope.

</deferred>

---

*Phase: 02-learner-pi-rl-training-path*
*Context gathered: 2026-02-22*
