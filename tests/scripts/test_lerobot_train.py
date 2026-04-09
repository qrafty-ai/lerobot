import torch
import pytest
from contextlib import nullcontext

from lerobot.scripts.lerobot_train import (
    compute_weighted_loss,
    get_human_demo_batch_weights,
    policy_forward_supports_reduction_arg,
    update_policy,
)
from lerobot.utils.logging_utils import AverageMeter, MetricsTracker


def test_get_human_demo_batch_weights_scales_and_normalizes():
    batch = {"is_human_demo": torch.tensor([0, 1, 2, 0], dtype=torch.int64)}

    weights = get_human_demo_batch_weights(
        batch=batch,
        key="is_human_demo",
        scale=3.0,
        batch_size=4,
        device=torch.device("cpu"),
        dtype=torch.float32,
    )

    torch.testing.assert_close(weights, torch.tensor([0.5, 1.5, 1.5, 0.5]))
    torch.testing.assert_close(weights.sum(), torch.tensor(4.0))


def test_compute_weighted_loss_uses_normalized_batch_weights():
    per_sample_loss = torch.tensor([1.0, 1.0, 10.0, 1.0])
    batch_weights = torch.tensor([0.5, 1.5, 1.5, 0.5])

    loss = compute_weighted_loss(per_sample_loss, batch_weights)

    torch.testing.assert_close(loss, torch.tensor(4.375))


def test_get_human_demo_batch_weights_errors_on_missing_key():
    with pytest.raises(ValueError, match="missing from the batch"):
        get_human_demo_batch_weights(
            batch={},
            key="is_human_demo",
            scale=2.0,
            batch_size=2,
            device=torch.device("cpu"),
            dtype=torch.float32,
        )


def test_get_human_demo_batch_weights_errors_on_unusable_shape():
    batch = {"is_human_demo": torch.ones(2, 2, dtype=torch.float32)}

    with pytest.raises(ValueError, match="Expected one value per sample"):
        get_human_demo_batch_weights(
            batch=batch,
            key="is_human_demo",
            scale=2.0,
            batch_size=2,
            device=torch.device("cpu"),
            dtype=torch.float32,
        )


class DummyAccelerator:
    num_processes = 1

    def autocast(self):
        return nullcontext()

    def backward(self, loss: torch.Tensor) -> None:
        loss.backward()

    def clip_grad_norm_(self, parameters, max_norm: float) -> torch.Tensor:
        return torch.nn.utils.clip_grad_norm_(parameters, max_norm)

    def unwrap_model(self, policy, keep_fp32_wrapper: bool = True):  # noqa: ARG002
        return policy


class ReductionAwarePolicy(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.weight = torch.nn.Parameter(torch.tensor(1.0))

    def forward(self, batch, reduction: str = "mean"):
        per_sample_loss = batch["per_sample_loss"] * self.weight
        if reduction == "none":
            return per_sample_loss, {"loss": per_sample_loss.mean().item()}
        return per_sample_loss.mean(), {"loss": per_sample_loss.mean().item()}


class ReductionUnsupportedPolicy(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.weight = torch.nn.Parameter(torch.tensor(1.0))

    def forward(self, batch):
        per_sample_loss = batch["per_sample_loss"] * self.weight
        return per_sample_loss.mean(), {"loss": per_sample_loss.mean().item()}


class XVLAStylePolicy(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.weight = torch.nn.Parameter(torch.tensor(1.0))

    def forward(self, batch, reduction: str = "mean"):
        action_loss = batch["per_sample_loss"] * self.weight
        gripper_loss = batch["gripper_loss"] * self.weight
        total_loss = action_loss + gripper_loss
        output_dict = {
            "action_loss": action_loss.mean().item(),
            "gripper_loss": gripper_loss.mean().item(),
            "loss": total_loss.mean().item(),
        }
        if reduction == "none":
            return total_loss, output_dict
        return total_loss.mean(), output_dict


def make_train_metrics() -> MetricsTracker:
    return MetricsTracker(
        batch_size=4,
        num_frames=4,
        num_episodes=1,
        metrics={
            "loss": AverageMeter("loss"),
            "grad_norm": AverageMeter("grad_norm"),
            "lr": AverageMeter("lr"),
            "update_s": AverageMeter("update_s"),
        },
    )


def test_update_policy_applies_human_demo_weighting_when_policy_supports_reduction():
    policy = ReductionAwarePolicy()
    optimizer = torch.optim.SGD(policy.parameters(), lr=0.1)
    batch = {
        "per_sample_loss": torch.tensor([1.0, 2.0, 3.0, 4.0]),
        "is_human_demo": torch.tensor([0, 1, 0, 1], dtype=torch.int64),
    }

    train_metrics, _ = update_policy(
        train_metrics=make_train_metrics(),
        policy=policy,
        batch=batch,
        optimizer=optimizer,
        grad_clip_norm=0.0,
        accelerator=DummyAccelerator(),
        human_demo_key="is_human_demo",
        human_demo_scale=3.0,
    )

    assert train_metrics.loss.val == pytest.approx(2.75)


def test_update_policy_falls_back_when_policy_does_not_support_reduction(caplog):
    policy = ReductionUnsupportedPolicy()
    optimizer = torch.optim.SGD(policy.parameters(), lr=0.1)
    batch = {
        "per_sample_loss": torch.tensor([1.0, 2.0, 3.0, 4.0]),
        "is_human_demo": torch.tensor([0, 1, 0, 1], dtype=torch.int64),
    }

    with caplog.at_level("WARNING"):
        train_metrics, _ = update_policy(
            train_metrics=make_train_metrics(),
            policy=policy,
            batch=batch,
            optimizer=optimizer,
            grad_clip_norm=0.0,
            accelerator=DummyAccelerator(),
            human_demo_key="is_human_demo",
            human_demo_scale=3.0,
        )

    assert train_metrics.loss.val == pytest.approx(2.5)
    assert "skipping human-demo weighting" in caplog.text


def test_xvla_style_policy_supports_reduction_arg() -> None:
    assert policy_forward_supports_reduction_arg(XVLAStylePolicy())


def test_update_policy_applies_human_demo_weighting_for_xvla_style_policy(caplog):
    policy = XVLAStylePolicy()
    optimizer = torch.optim.SGD(policy.parameters(), lr=0.1)
    batch = {
        "per_sample_loss": torch.tensor([1.0, 2.0, 3.0, 4.0]),
        "gripper_loss": torch.tensor([0.5, 0.5, 0.5, 0.5]),
        "is_human_demo": torch.tensor([0, 1, 0, 1], dtype=torch.int64),
    }

    with caplog.at_level("WARNING"):
        train_metrics, _ = update_policy(
            train_metrics=make_train_metrics(),
            policy=policy,
            batch=batch,
            optimizer=optimizer,
            grad_clip_norm=0.0,
            accelerator=DummyAccelerator(),
            human_demo_key="is_human_demo",
            human_demo_scale=3.0,
        )

    assert train_metrics.loss.val == pytest.approx(3.25)
    assert "skipping human-demo weighting" not in caplog.text
