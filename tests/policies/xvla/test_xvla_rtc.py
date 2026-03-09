#!/usr/bin/env python

# Copyright 2025 The HuggingFace Inc. team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from types import SimpleNamespace
import pytest
import torch
from torch import nn

from lerobot.configs.types import FeatureType, PolicyFeature, RTCAttentionSchedule
from lerobot.policies.rtc.configuration_rtc import RTCConfig
from lerobot.policies.xvla.configuration_xvla import XVLAConfig
from lerobot.policies.xvla.modeling_xvla import XVLAPolicy
from lerobot.utils.constants import ACTION, OBS_IMAGES, OBS_LANGUAGE_TOKENS, OBS_STATE


class FakeEncoder(nn.Module):
    def forward(self, attention_mask=None, inputs_embeds=None):
        return (inputs_embeds,)


class FakeFlorence2ForConditionalGeneration(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = SimpleNamespace(projection_dim=4)
        self.language_model = SimpleNamespace(
            model=SimpleNamespace(encoder=FakeEncoder(), decoder=object(), shared=nn.Embedding(32, 4)),
            lm_head=object(),
        )
        self.embedding = nn.Embedding(32, 4)

    def _encode_image(self, valid_images):
        batch_size = valid_images.shape[0]
        return torch.ones(batch_size, 2, 4, device=valid_images.device, dtype=valid_images.dtype)

    def get_input_embeddings(self):
        return self.embedding

    def _merge_input_ids_with_image_features(self, image_features, inputs_embeds):
        attention_mask = torch.ones(inputs_embeds.shape[:2], device=inputs_embeds.device, dtype=torch.bool)
        return inputs_embeds, attention_mask


class FakeSoftPromptedTransformer(nn.Module):
    def __init__(self, *args, dim_action: int, **kwargs):
        super().__init__()
        self.dim_action = dim_action

    def forward(self, domain_id, action_with_noise, proprio, t, **enc):
        del domain_id, proprio, enc
        return 0.35 * action_with_noise + 0.15 * t.view(-1, 1, 1)


@pytest.fixture(autouse=True)
def patch_xvla_dependencies(monkeypatch):
    monkeypatch.setattr(
        "lerobot.policies.xvla.modeling_xvla.Florence2ForConditionalGeneration",
        FakeFlorence2ForConditionalGeneration,
    )
    monkeypatch.setattr(
        "lerobot.policies.xvla.modeling_xvla.SoftPromptedTransformer",
        FakeSoftPromptedTransformer,
    )
    monkeypatch.setattr(XVLAConfig, "get_florence_config", lambda self: SimpleNamespace())


def make_config(rtc_config: RTCConfig | None, action_mode: str = "ee6d", action_dim: int = 20) -> XVLAConfig:
    config = XVLAConfig(
        chunk_size=4,
        n_action_steps=2,
        num_denoising_steps=4,
        num_image_views=1,
        device="cpu",
        action_mode=action_mode,
        input_features={
            f"{OBS_IMAGES}.main": PolicyFeature(type=FeatureType.VISUAL, shape=(3, 8, 8)),
            OBS_STATE: PolicyFeature(type=FeatureType.STATE, shape=(20,)),
        },
        output_features={
            ACTION: PolicyFeature(type=FeatureType.ACTION, shape=(action_dim,)),
        },
        rtc_config=rtc_config,
    )
    return config


def make_batch() -> dict[str, torch.Tensor]:
    return {
        OBS_LANGUAGE_TOKENS: torch.tensor([[1, 2, 3, 4]], dtype=torch.long),
        f"{OBS_IMAGES}.main": torch.rand(1, 3, 8, 8, dtype=torch.float32),
        OBS_STATE: torch.rand(1, 20, dtype=torch.float32),
    }


def make_rtc_config(enabled: bool = True) -> RTCConfig:
    return RTCConfig(
        enabled=enabled,
        execution_horizon=3,
        max_guidance_weight=5.0,
        prefix_attention_schedule=RTCAttentionSchedule.EXP,
        debug=False,
    )


def test_xvla_rtc_initialization():
    policy = XVLAPolicy(make_config(make_rtc_config()))

    assert policy.rtc_processor is not None
    assert policy.model.rtc_processor is policy.rtc_processor
    assert policy._rtc_enabled() is True


def test_xvla_rtc_initialization_without_rtc_config():
    policy = XVLAPolicy(make_config(None))

    assert policy.rtc_processor is None
    assert policy.model.rtc_processor is None
    assert policy._rtc_enabled() is False


def test_xvla_rtc_inference_with_prev_chunk_changes_actions():
    policy = XVLAPolicy(make_config(make_rtc_config()))
    batch = make_batch()
    noise = torch.randn(1, policy.config.chunk_size, policy.model.dim_action)
    predict_action_chunk = getattr(policy, "predict_action_chunk")

    with torch.no_grad():
        _ = predict_action_chunk(batch, noise=noise.clone())
        actions_with_rtc = predict_action_chunk(
            batch, noise=noise.clone(), inference_delay=1, execution_horizon=3
        )
        assert policy.config.rtc_config is not None
        policy.config.rtc_config.enabled = False
        actions_without_rtc = predict_action_chunk(batch, noise=noise.clone())

    assert actions_with_rtc.shape == actions_without_rtc.shape == (1, policy.config.chunk_size, 20)
    assert not torch.allclose(actions_with_rtc, actions_without_rtc)


def test_xvla_rtc_inference_without_prev_chunk_matches_base():
    policy = XVLAPolicy(make_config(make_rtc_config()))
    batch = make_batch()
    noise = torch.randn(1, policy.config.chunk_size, policy.model.dim_action)
    predict_action_chunk = getattr(policy, "predict_action_chunk")

    with torch.no_grad():
        actions_with_rtc = predict_action_chunk(batch, noise=noise.clone(), prev_chunk_left_over=None)
        assert policy.config.rtc_config is not None
        policy.config.rtc_config.enabled = False
        actions_without_rtc = predict_action_chunk(batch, noise=noise.clone())

    assert torch.allclose(actions_with_rtc, actions_without_rtc)


def test_xvla_rtc_auto_action_space_uses_internal_raw_chunk():
    policy = XVLAPolicy(make_config(make_rtc_config(), action_mode="auto", action_dim=7))
    batch = make_batch()
    noise = torch.randn(1, policy.config.chunk_size, policy.model.dim_action)
    predict_action_chunk = getattr(policy, "predict_action_chunk")

    with torch.no_grad():
        first_actions = predict_action_chunk(batch, noise=noise.clone())
        second_actions = predict_action_chunk(
            batch, noise=noise.clone(), inference_delay=1, execution_horizon=3
        )

    assert first_actions.shape == (1, policy.config.chunk_size, 7)
    assert second_actions.shape == (1, policy.config.chunk_size, 7)


def test_xvla_rtc_requires_inference_delay_with_prev_chunk():
    policy = XVLAPolicy(make_config(make_rtc_config()))

    with pytest.raises(ValueError, match="inference_delay is required"):
        policy.predict_action_chunk(
            make_batch(),
            prev_chunk_left_over=torch.randn(1, policy.config.chunk_size, policy.model.dim_action),
        )


def test_xvla_rtc_select_action_raises():
    policy = XVLAPolicy(make_config(make_rtc_config()))

    with pytest.raises(AssertionError, match="RTC is not supported for select_action"):
        policy.select_action(make_batch())
