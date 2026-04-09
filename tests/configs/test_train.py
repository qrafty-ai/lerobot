from types import SimpleNamespace

import pytest

from lerobot.configs.train import TrainPipelineConfig


class DummyPolicyConfig:
    type = "dummy"
    pretrained_path = None
    push_to_hub = False
    repo_id = None

    def get_optimizer_preset(self):
        return SimpleNamespace(grad_clip_norm=1.0)

    def get_scheduler_preset(self):
        return SimpleNamespace()


def make_train_config(tmp_path, **overrides) -> TrainPipelineConfig:
    cfg = TrainPipelineConfig(
        dataset=SimpleNamespace(repo_id="dummy/repo", root=None),
        policy=DummyPolicyConfig(),
        output_dir=tmp_path / "output",
        **overrides,
    )
    return cfg


def test_validate_rejects_human_demo_weighting_with_rabc(tmp_path):
    cfg = make_train_config(
        tmp_path,
        use_rabc=True,
        human_demo_key="observation.is_human_demo",
    )

    with pytest.raises(ValueError, match="use_rabc and human_demo_key"):
        cfg.validate()


@pytest.mark.parametrize("scale", [0.0, -1.0])
def test_validate_requires_positive_human_demo_scale(tmp_path, scale):
    cfg = make_train_config(
        tmp_path,
        human_demo_key="observation.is_human_demo",
        human_demo_scale=scale,
    )

    with pytest.raises(ValueError, match="human_demo_scale must be strictly positive"):
        cfg.validate()


def test_validate_rejects_human_demo_scale_without_key(tmp_path):
    cfg = make_train_config(tmp_path, human_demo_scale=2.0)

    with pytest.raises(ValueError, match="human_demo_scale requires human_demo_key"):
        cfg.validate()


def test_validate_accepts_human_demo_weighting_config(tmp_path):
    cfg = make_train_config(
        tmp_path,
        human_demo_key="observation.is_human_demo",
        human_demo_scale=3.0,
    )

    cfg.validate()
    assert cfg.human_demo_key == "observation.is_human_demo"
    assert cfg.human_demo_scale == 3.0
