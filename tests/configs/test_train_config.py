#!/usr/bin/env python

import draccus
import pytest

from lerobot.configs.default import DatasetConfig
from lerobot.configs.train import (
    PIRLConfig,
    PIRLFlowNoiseConfig,
    PIRLFlowSDEConfig,
    TrainRLServerPipelineConfig,
)
from lerobot.policies.sac.configuration_sac import SACConfig
from lerobot.policies.xvla.configuration_xvla import XVLAConfig


def test_parse_pi_rl_recipe_uses_canonical_spelling():
    cfg = draccus.parse(
        config_class=TrainRLServerPipelineConfig,
        args=[
            "--recipe=pi-rl",
            "--pirl.variant=flow-noise",
            "--pirl.temperature=0.5",
            "--pirl.target_noise_scale=0.25",
            "--pirl.flow_noise.std=0.1",
        ],
    )

    assert cfg.recipe == "pi-rl"
    assert cfg.pirl.variant == "flow-noise"


def test_validate_pi_rl_flow_noise_variant_accepts_required_knobs():
    cfg = TrainRLServerPipelineConfig(
        recipe="pi-rl",
        pirl=PIRLConfig(
            variant="flow-noise",
            temperature=0.7,
            target_noise_scale=0.2,
            flow_noise=PIRLFlowNoiseConfig(std=0.1),
        ),
        dataset=DatasetConfig(repo_id="lerobot/test"),
        policy=XVLAConfig(push_to_hub=False),
    )

    cfg.validate()


def test_validate_pi_rl_flow_sde_variant_accepts_required_knobs():
    cfg = TrainRLServerPipelineConfig(
        recipe="pi-rl",
        pirl=PIRLConfig(
            variant="flow-sde",
            temperature=0.7,
            target_noise_scale=0.2,
            flow_sde=PIRLFlowSDEConfig(sigma_min=0.02, sigma_max=0.2),
        ),
        dataset=DatasetConfig(repo_id="lerobot/test"),
        policy=XVLAConfig(push_to_hub=False),
    )

    cfg.validate()


def test_validate_rejects_non_canonical_recipe_with_fix_guidance():
    cfg = TrainRLServerPipelineConfig(recipe="pi_rl", policy=SACConfig())

    with pytest.raises(ValueError, match="Invalid `recipe` value 'pi_rl'.*canonical `pi-rl`"):
        cfg.validate()


def test_validate_rejects_missing_variant_with_field_value_and_fix_hint():
    cfg = TrainRLServerPipelineConfig(recipe="pi-rl", policy=XVLAConfig(push_to_hub=False))

    with pytest.raises(ValueError, match="Invalid `pirl.variant` value None.*flow-noise.*flow-sde"):
        cfg.validate()


def test_validate_rejects_unknown_variant_with_expected_values():
    cfg = TrainRLServerPipelineConfig(
        recipe="pi-rl",
        pirl=PIRLConfig(variant="flow-foo", temperature=0.7, target_noise_scale=0.2),
        policy=XVLAConfig(push_to_hub=False),
    )

    with pytest.raises(ValueError, match="Invalid `pirl.variant` value 'flow-foo'.*flow-noise.*flow-sde"):
        cfg.validate()


def test_validate_rejects_non_positive_flow_noise_std_with_fix_hint():
    cfg = TrainRLServerPipelineConfig(
        recipe="pi-rl",
        pirl=PIRLConfig(
            variant="flow-noise",
            temperature=0.7,
            target_noise_scale=0.2,
            flow_noise=PIRLFlowNoiseConfig(std=0),
        ),
        policy=XVLAConfig(push_to_hub=False),
    )

    with pytest.raises(ValueError, match="Invalid `pirl.flow_noise.std` value 0.*positive value"):
        cfg.validate()


def test_validate_rejects_invalid_flow_sde_bounds_with_fix_guidance():
    cfg = TrainRLServerPipelineConfig(
        recipe="pi-rl",
        pirl=PIRLConfig(
            variant="flow-sde",
            temperature=0.7,
            target_noise_scale=0.2,
            flow_sde=PIRLFlowSDEConfig(sigma_min=0.3, sigma_max=0.3),
        ),
        policy=XVLAConfig(push_to_hub=False),
    )

    with pytest.raises(ValueError, match="Invalid `pirl.flow_sde.sigma_max` value 0.3.*greater than"):
        cfg.validate()
