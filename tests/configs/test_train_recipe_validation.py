#!/usr/bin/env python

import draccus
import pytest

from lerobot.configs.parser import validate_recipe_cli_args
from lerobot.configs.train import PIRLConfig, PIRLFlowSDEConfig, TrainRLServerPipelineConfig


def test_train_rl_server_config_parse_defaults_without_recipe():
    cfg = draccus.parse(config_class=TrainRLServerPipelineConfig, args=[])

    assert cfg.recipe is None
    assert cfg.pirl.variant is None


def test_train_rl_server_config_parse_pi_rl_flow_noise():
    cfg = draccus.parse(
        config_class=TrainRLServerPipelineConfig,
        args=[
            "--recipe=pi-rl",
            "--pirl.variant=flow-noise",
            "--pirl.temperature=0.7",
            "--pirl.target_noise_scale=0.1",
            "--pirl.flow_noise.std=0.2",
        ],
    )

    assert cfg.recipe == "pi-rl"
    assert cfg.pirl.variant == "flow-noise"
    assert cfg.pirl.flow_noise.std == 0.2


def test_train_rl_server_config_parse_pi_rl_flow_sde():
    cfg = draccus.parse(
        config_class=TrainRLServerPipelineConfig,
        args=[
            "--recipe=pi-rl",
            "--pirl.variant=flow-sde",
            "--pirl.temperature=0.7",
            "--pirl.target_noise_scale=0.1",
            "--pirl.flow_sde.sigma_min=0.01",
            "--pirl.flow_sde.sigma_max=0.3",
        ],
    )

    assert cfg.recipe == "pi-rl"
    assert cfg.pirl.variant == "flow-sde"
    assert cfg.pirl.flow_sde.sigma_min == 0.01
    assert cfg.pirl.flow_sde.sigma_max == 0.3


def test_validate_rejects_non_canonical_recipe_with_fix_hint():
    cfg = TrainRLServerPipelineConfig(recipe="pi_rl")

    with pytest.raises(ValueError, match="Invalid `recipe` value 'pi_rl'.*canonical `pi-rl`"):
        cfg.validate()


def test_validate_rejects_missing_variant_when_pi_rl_enabled():
    cfg = TrainRLServerPipelineConfig(recipe="pi-rl")

    with pytest.raises(ValueError, match="Invalid `pirl.variant` value None.*flow-noise.*flow-sde"):
        cfg.validate()


def test_validate_rejects_missing_flow_noise_std():
    cfg = TrainRLServerPipelineConfig(
        recipe="pi-rl",
        pirl=PIRLConfig(variant="flow-noise", temperature=0.7, target_noise_scale=0.1),
    )

    with pytest.raises(ValueError, match="Invalid `pirl.flow_noise.std` value None.*positive float"):
        cfg.validate()


def test_validate_rejects_unknown_variant():
    cfg = TrainRLServerPipelineConfig(
        recipe="pi-rl",
        pirl=PIRLConfig(variant="flow-noisee", temperature=0.7, target_noise_scale=0.1),
    )

    with pytest.raises(ValueError, match="Invalid `pirl.variant` value 'flow-noisee'.*flow-noise.*flow-sde"):
        cfg.validate()


def test_validate_rejects_invalid_flow_sde_bounds():
    cfg = TrainRLServerPipelineConfig(
        recipe="pi-rl",
        pirl=PIRLConfig(
            variant="flow-sde",
            temperature=0.7,
            target_noise_scale=0.1,
            flow_sde=PIRLFlowSDEConfig(sigma_min=0.3, sigma_max=0.2),
        ),
    )

    with pytest.raises(ValueError, match="Invalid `pirl.flow_sde.sigma_max` value 0.2.*greater than"):
        cfg.validate()


def test_parser_recipe_preflight_rejects_non_canonical_spelling():
    with pytest.raises(ValueError, match="Invalid `recipe` value 'PI_RL'.*canonical `pi-rl`"):
        validate_recipe_cli_args(["--recipe=PI_RL"])
