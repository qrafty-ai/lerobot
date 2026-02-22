#!/usr/bin/env python

from typing import Any, cast

import pytest
import torch
from torch import nn
from torch.multiprocessing import Queue

from lerobot.configs.train import (
    PI_RL_CONFIG_HASH_METADATA_KEY,
    PI_RL_CONFIG_PATH_METADATA_KEY,
    TrainRLServerPipelineConfig,
    build_recipe_preflight_context,
)
from lerobot.policies.sac.configuration_sac import SACConfig
from lerobot.policies.sac.modeling_sac import SACPolicy
from lerobot.transport.utils import bytes_to_state_dict, state_to_bytes
from tests.rl.test_actor_learner import find_free_port
from tests.utils import require_package


class _DummySyncPolicy(nn.Module):
    def __init__(self):
        super().__init__()
        self.actor = nn.Linear(2, 2)


@pytest.fixture
def cfg():
    cfg = TrainRLServerPipelineConfig()

    port = find_free_port()

    policy_cfg = SACConfig()
    policy_cfg.actor_learner_config.learner_host = "127.0.0.1"
    policy_cfg.actor_learner_config.learner_port = port
    policy_cfg.concurrency.actor = "threads"
    policy_cfg.concurrency.learner = "threads"
    policy_cfg.actor_learner_config.queue_get_timeout = 0.1

    cfg.policy = policy_cfg

    return cfg


@require_package("grpcio", "grpc")
def test_push_actor_policy_to_queue_includes_config_metadata_when_requested():
    from lerobot.rl.learner import push_actor_policy_to_queue

    parameters_queue = Queue()
    policy = _DummySyncPolicy()
    config_path = "/tmp/learner/train_config.json"
    config_hash = "abc123"

    push_actor_policy_to_queue(
        parameters_queue=parameters_queue,
        policy=policy,
        include_config_metadata=True,
        config_path=config_path,
        config_hash=config_hash,
    )

    payload = bytes_to_state_dict(parameters_queue.get())

    assert PI_RL_CONFIG_PATH_METADATA_KEY in payload
    assert PI_RL_CONFIG_HASH_METADATA_KEY in payload
    assert payload[PI_RL_CONFIG_PATH_METADATA_KEY].dtype == torch.uint8
    assert payload[PI_RL_CONFIG_HASH_METADATA_KEY].dtype == torch.uint8
    assert bytes(payload[PI_RL_CONFIG_PATH_METADATA_KEY].tolist()).decode("utf-8") == config_path
    assert bytes(payload[PI_RL_CONFIG_HASH_METADATA_KEY].tolist()).decode("utf-8") == config_hash


@require_package("grpcio", "grpc")
def test_update_policy_parameters_fails_on_actor_learner_config_mismatch(cfg):
    from lerobot.rl.actor import update_policy_parameters

    parameters_queue = Queue()
    policy = _DummySyncPolicy()

    actor_context = build_recipe_preflight_context(cfg)
    learner_path = "/tmp/other/train_config.json"
    learner_hash = "deadbeef"

    state_dict_payload: dict[str, Any] = {
        "policy": policy.actor.state_dict(),
        PI_RL_CONFIG_PATH_METADATA_KEY: torch.tensor(list(learner_path.encode("utf-8")), dtype=torch.uint8),
        PI_RL_CONFIG_HASH_METADATA_KEY: torch.tensor(list(learner_hash.encode("utf-8")), dtype=torch.uint8),
    }
    parameters_queue.put(state_to_bytes(cast(dict[str, torch.Tensor], state_dict_payload)))

    with pytest.raises(RuntimeError, match="Actor/Learner config mismatch") as exc_info:
        update_policy_parameters(
            policy=cast(SACPolicy, cast(object, policy)),
            parameters_queue=parameters_queue,
            device="cpu",
            cfg=cfg,
        )

    error_text = str(exc_info.value)
    assert actor_context.config_path in error_text
    assert learner_path in error_text
    assert actor_context.config_hash in error_text
    assert learner_hash in error_text
