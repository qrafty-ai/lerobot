# PROCESSOR KNOWLEDGE

## OVERVIEW
`src/lerobot/processor` is the transition-processing framework: registry-driven steps, serializable pipelines, and policy/robot bridge transforms.

## WHERE TO LOOK
| Task | Location | Notes |
|------|----------|-------|
| Core pipeline behavior | `pipeline.py` | `ProcessorStepRegistry`, `DataProcessorPipeline`, preload/save logic |
| Step registration examples | `hil_processor.py`, `normalize_processor.py`, `batch_processor.py` | Use `@ProcessorStepRegistry.register(...)` |
| Type bridge helpers | `converters.py`, `core.py` | Transition schema + batch conversion |
| Policy/robot mapping | `policy_robot_bridge.py` | Action-space translation steps |

## CONVENTIONS
- Every reusable step should be registry-registered for portable loading.
- Steps should implement both runtime transform (`__call__`) and feature transform (`transform_features`).
- Pipeline persistence uses config JSON + optional safetensors state files.

## ANTI-PATTERNS
- Do not mutate shared transition payloads in-place; copy transition data before edits.
- Do not create unregistered custom steps if they need serialization/from_pretrained support.
- Do not bypass `from_pretrained` validation paths when loading processor configs.

## NOTES
- Processor migration paths exist for older models; see migration handling in `pipeline.py`.
- `PolicyProcessorPipeline` and `RobotProcessorPipeline` are type aliases over the same core engine.

## COMMANDS
- Run processor test suite: `pytest -sv tests/processor`
- Inspect registered steps quickly: `python -c "from lerobot.processor import ProcessorStepRegistry; print(len(ProcessorStepRegistry.list()))"`
