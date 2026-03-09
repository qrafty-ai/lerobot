#!/usr/bin/env python

from pathlib import Path

import pytest
import torch

pytest.importorskip("transformers")

from lerobot.configs.types import FeatureType, PolicyFeature
from lerobot.policies.xvla.configuration_xvla import XVLAConfig
from lerobot.policies.xvla.modeling_xvla import XVLAPolicy


def make_tiny_xvla_config(max_state_dim: int) -> XVLAConfig:
    florence_config = {
        "projection_dim": 16,
        "vision_config": {
            "projection_dim": 16,
            "dim_embed": [8, 8, 16, 16],
            "num_heads": [1, 1, 2, 2],
            "num_groups": [1, 1, 2, 2],
            "depths": [1, 1, 1, 1],
            "window_size": 2,
            "patch_size": [7, 3, 3, 3],
            "patch_stride": [4, 2, 2, 2],
            "patch_padding": [3, 1, 1, 1],
        },
        "text_config": {
            "vocab_size": 32,
            "d_model": 16,
            "encoder_attention_heads": 1,
            "decoder_attention_heads": 1,
            "encoder_layers": 1,
            "decoder_layers": 1,
            "encoder_ffn_dim": 32,
            "decoder_ffn_dim": 32,
            "max_position_embeddings": 32,
            "bos_token_id": 0,
            "eos_token_id": 2,
            "pad_token_id": 1,
            "num_beams": 1,
        },
    }

    return XVLAConfig(
        florence_config=florence_config,
        input_features={
            "observation.images.image": PolicyFeature(type=FeatureType.VISUAL, shape=(3, 32, 32)),
            "observation.state": PolicyFeature(type=FeatureType.STATE, shape=(max_state_dim,)),
        },
        output_features={
            "action": PolicyFeature(type=FeatureType.ACTION, shape=(20,)),
        },
        hidden_size=16,
        depth=1,
        num_heads=1,
        num_domains=2,
        len_soft_prompts=2,
        dim_time=4,
        max_len_seq=64,
        max_state_dim=max_state_dim,
        max_action_dim=20,
        chunk_size=2,
        n_action_steps=2,
        tokenizer_max_length=8,
        num_image_views=1,
        resize_imgs_with_padding=(32, 32),
        device="cpu",
    )


def test_from_pretrained_reinitializes_action_encoder_for_larger_max_state_dim(tmp_path: Path):
    checkpoint_cfg = make_tiny_xvla_config(max_state_dim=20)
    checkpoint_policy = XVLAPolicy(checkpoint_cfg)
    _ = checkpoint_policy.save_pretrained(tmp_path)

    runtime_cfg = make_tiny_xvla_config(max_state_dim=24)
    runtime_cfg.allow_reinit_action_encoder_for_larger_max_state_dim = True
    loaded_policy = XVLAPolicy.from_pretrained(tmp_path, config=runtime_cfg)

    checkpoint_weight = checkpoint_policy.model.transformer.action_encoder.fc.weight.view(2, 44, 16)
    loaded_weight = loaded_policy.model.transformer.action_encoder.fc.weight.view(2, 48, 16)

    assert loaded_policy.model.dim_proprio == 24
    assert loaded_policy.model.transformer.action_encoder.input_size == 48
    assert loaded_policy.model.transformer.action_encoder.fc.weight.shape == (2, 768)
    torch.testing.assert_close(loaded_weight[:, :20, :], checkpoint_weight[:, :20, :], rtol=0, atol=0)
    torch.testing.assert_close(loaded_weight[:, 20:40, :], checkpoint_weight[:, 20:40, :], rtol=0, atol=0)
    torch.testing.assert_close(loaded_weight[:, 44:48, :], checkpoint_weight[:, 40:44, :], rtol=0, atol=0)

    torch.testing.assert_close(
        checkpoint_policy.model.transformer.action_encoder.bias.weight,
        loaded_policy.model.transformer.action_encoder.bias.weight,
        rtol=0,
        atol=0,
    )
    torch.testing.assert_close(
        checkpoint_policy.model.transformer.action_decoder.fc.weight,
        loaded_policy.model.transformer.action_decoder.fc.weight,
        rtol=0,
        atol=0,
    )


def test_from_pretrained_requires_opt_in_for_larger_max_state_dim(tmp_path: Path):
    checkpoint_cfg = make_tiny_xvla_config(max_state_dim=20)
    checkpoint_policy = XVLAPolicy(checkpoint_cfg)
    _ = checkpoint_policy.save_pretrained(tmp_path)

    runtime_cfg = make_tiny_xvla_config(max_state_dim=24)

    with pytest.raises(RuntimeError, match="allow_reinit_action_encoder_for_larger_max_state_dim"):
        XVLAPolicy.from_pretrained(tmp_path, config=runtime_cfg)
