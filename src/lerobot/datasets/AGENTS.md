# DATASETS KNOWLEDGE

## OVERVIEW
`src/lerobot/datasets` contains dataset format/runtime APIs, metadata sync with the Hub, video/image IO, online buffer support, and migration utilities.

## WHERE TO LOOK
| Task | Location | Notes |
|------|----------|-------|
| Core dataset API | `lerobot_dataset.py` | `LeRobotDataset`, metadata lifecycle, read/write paths |
| Dataset tooling | `dataset_tools.py` | split/merge/delete/edit flows |
| Feature and validation helpers | `utils.py` | schema checks, stats/task/episode helpers |
| Online RL data | `online_buffer.py` | online/offline mixing + sampler weights |
| Video path | `video_utils.py` | decode/encode and metadata ops |
| v3 migration scripts | `v30/` | conversion and stats augmentation scripts |

## CONVENTIONS
- LeRobotDataset format couples parquet metadata with video/image assets.
- Metadata syncing and version checks happen through dataset metadata helpers.
- HF Hub integration is first-class (`snapshot_download`, push helpers).

## ANTI-PATTERNS
- Do not bypass schema/version checks when loading or editing datasets.
- Do not modify episode/video indexing logic without updating associated metadata writers.
- Do not treat artifacts as small text fixtures; tests rely on git-lfs managed assets.

## NOTES
- Dataset code is high impact and large; prefer targeted edits with focused tests.
- CLI-facing dataset operations are surfaced via `src/lerobot/scripts/lerobot_edit_dataset.py`.

## COMMANDS
- Run dataset tests: `pytest -sv tests/datasets`
- Inspect dataset metadata quickly: `python -c "from lerobot.datasets.lerobot_dataset import LeRobotDatasetMetadata; print('ok')"`
