#!/usr/bin/env python

import pytest
from accelerate import Accelerator

from lerobot.configs.default import DatasetConfig
from lerobot.configs.train import PIRLConfig, TrainPipelineConfig
from lerobot.policies.sac.configuration_sac import SACConfig
from lerobot.policies.xvla.configuration_xvla import XVLAConfig
from lerobot.scripts import lerobot_train


def test_train_route_blocks_pi_rl_mode(monkeypatch, tmp_path):
    monkeypatch.setattr(lerobot_train, "init_logging", lambda *args, **kwargs: None)
    accelerator = Accelerator(cpu=True)

    cfg = TrainPipelineConfig(
        dataset=DatasetConfig(repo_id="dummy/repo", root=str(tmp_path)),
        policy=XVLAConfig(),
        recipe="pi-rl",
        pirl=PIRLConfig(variant="flow-noise", temperature=0.7, target_noise_scale=0.1),
    )
    cfg.validate = lambda: None

    with pytest.raises(RuntimeError, match="distributed RL runtime"):
        lerobot_train.train(cfg, accelerator=accelerator)


def test_train_route_keeps_default_non_pi_rl_path(monkeypatch, tmp_path):
    monkeypatch.setattr(lerobot_train, "init_logging", lambda *args, **kwargs: None)
    accelerator = Accelerator(cpu=True)

    def _raise_dataset_called(_cfg):
        raise RuntimeError("DATASET_CALLED")

    monkeypatch.setattr(lerobot_train, "make_dataset", _raise_dataset_called)

    cfg = TrainPipelineConfig(
        dataset=DatasetConfig(repo_id="dummy/repo", root=str(tmp_path)),
        policy=SACConfig(),
    )
    cfg.validate = lambda: None
    cfg.seed = None

    with pytest.raises(RuntimeError, match="DATASET_CALLED"):
        lerobot_train.train(cfg, accelerator=accelerator)
