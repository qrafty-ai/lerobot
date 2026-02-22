# Copyright 2024 The HuggingFace Inc. team. All rights reserved.
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
# pyright: reportImportCycles=false, reportIncompatibleVariableOverride=false
import builtins
import datetime as dt
import hashlib
import json
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import draccus
from huggingface_hub import hf_hub_download
from huggingface_hub.errors import HfHubHTTPError

from lerobot import envs
from lerobot.configs import parser
from lerobot.configs.default import DatasetConfig, EvalConfig, PeftConfig, WandBConfig
from lerobot.configs.policies import PreTrainedConfig
from lerobot.configs.types import (
    PI_RL_RECIPE_ALLOWED_VARIANTS,
    PI_RL_RECIPE_VALUE,
    PIRLVariantType,
    RecipeType,
)
from lerobot.optim import OptimizerConfig
from lerobot.optim.schedulers import LRSchedulerConfig
from lerobot.utils.hub import HubMixin

TRAIN_CONFIG_NAME = "train_config.json"
PI_RL_PHASE1_ALLOWED_POLICIES = ("xvla",)
PI_RL_CONFIG_PATH_METADATA_KEY = "__lerobot_recipe_config_path__"
PI_RL_CONFIG_HASH_METADATA_KEY = "__lerobot_recipe_config_hash__"
INLINE_CONFIG_PATH = "<inline>"


@dataclass(frozen=True)
class RecipePreflightContext:
    recipe: str | None
    policy_type: str
    variant: str | None
    config_path: str
    config_hash: str


def _normalize_config_path(config_path: str | None) -> str:
    if config_path is None:
        return INLINE_CONFIG_PATH
    return str(Path(config_path).expanduser().resolve())


def resolve_runtime_config_path() -> str:
    return _normalize_config_path(parser.parse_arg("config_path"))


def compute_runtime_config_hash(cfg: "TrainPipelineConfig") -> str:
    encoded_cfg = draccus.encode(cfg)
    normalized_cfg = json.dumps(encoded_cfg, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(normalized_cfg.encode("utf-8")).hexdigest()


def build_recipe_preflight_context(cfg: "TrainPipelineConfig") -> RecipePreflightContext:
    recipe = cfg._to_string_or_none(cfg.recipe)
    variant = cfg._to_string_or_none(cfg.pirl.variant)
    policy_type = "<unset>" if cfg.policy is None else cfg.policy.type
    return RecipePreflightContext(
        recipe=recipe,
        policy_type=policy_type,
        variant=variant,
        config_path=resolve_runtime_config_path(),
        config_hash=compute_runtime_config_hash(cfg),
    )


def validate_recipe_runtime_preflight(cfg: "TrainPipelineConfig") -> RecipePreflightContext:
    context = build_recipe_preflight_context(cfg)
    if context.recipe != PI_RL_RECIPE_VALUE:
        return context

    if context.policy_type not in PI_RL_PHASE1_ALLOWED_POLICIES:
        allowed_policy_types = ", ".join(PI_RL_PHASE1_ALLOWED_POLICIES)
        raise ValueError(
            f"Invalid `policy.type` value {context.policy_type!r} for `recipe=pi-rl`. "
            f"Allowed policy types in Phase 1: [{allowed_policy_types}]."
        )

    return context


def log_recipe_preflight_summary(context: RecipePreflightContext, role: str) -> None:
    if context.recipe is None:
        return

    logging.info(
        "[%s] recipe preflight: recipe=%s policy=%s variant=%s config_path=%s",
        role,
        context.recipe,
        context.policy_type,
        context.variant,
        context.config_path,
    )


@dataclass
class PIRLFlowNoiseConfig:
    std: float | None = None


@dataclass
class PIRLFlowSDEConfig:
    sigma_min: float | None = None
    sigma_max: float | None = None


@dataclass
class PIRLConfig:
    variant: str | PIRLVariantType | None = None
    temperature: float | None = None
    target_noise_scale: float | None = None
    flow_noise: PIRLFlowNoiseConfig = field(default_factory=PIRLFlowNoiseConfig)
    flow_sde: PIRLFlowSDEConfig = field(default_factory=PIRLFlowSDEConfig)


@dataclass
class TrainPipelineConfig(HubMixin):
    dataset: DatasetConfig
    env: envs.EnvConfig | None = None
    policy: PreTrainedConfig | None = None
    # Set `dir` to where you would like to save all of the run outputs. If you run another training session
    # with the same value for `dir` its contents will be overwritten unless you set `resume` to true.
    output_dir: Path | None = None
    job_name: str | None = None
    # Set `resume` to true to resume a previous run. In order for this to work, you will need to make sure
    # `dir` is the directory of an existing run with at least one checkpoint in it.
    # Note that when resuming a run, the default behavior is to use the configuration from the checkpoint,
    # regardless of what's provided with the training command at the time of resumption.
    resume: bool = False
    # `seed` is used for training (eg: model initialization, dataset shuffling)
    # AND for the evaluation environments.
    seed: int | None = 1000
    # Number of workers for the dataloader.
    num_workers: int = 4
    batch_size: int = 8
    steps: int = 100_000
    eval_freq: int = 20_000
    log_freq: int = 200
    tolerance_s: float = 1e-4
    save_checkpoint: bool = True
    # Checkpoint is saved every `save_freq` training iterations and after the last training step.
    save_freq: int = 20_000
    use_policy_training_preset: bool = True
    optimizer: OptimizerConfig | None = None
    scheduler: LRSchedulerConfig | None = None
    eval: EvalConfig = field(default_factory=EvalConfig)
    wandb: WandBConfig = field(default_factory=WandBConfig)
    peft: PeftConfig | None = None
    recipe: str | RecipeType | None = None
    pirl: PIRLConfig = field(default_factory=PIRLConfig)

    # RA-BC (Reward-Aligned Behavior Cloning) parameters
    use_rabc: bool = False  # Enable reward-weighted training
    rabc_progress_path: str | None = None  # Path to precomputed SARM progress parquet file
    rabc_kappa: float = 0.01  # Hard threshold for high-quality samples
    rabc_epsilon: float = 1e-6  # Small constant for numerical stability
    rabc_head_mode: str | None = "sparse"  # For dual-head models: "sparse" or "dense"

    # Rename map for the observation to override the image and state keys
    rename_map: dict[str, str] = field(default_factory=dict)
    checkpoint_path: Path | None = field(init=False, default=None)

    def _format_validation_error(self, field_path: str, bad_value: Any, fix_hint: str) -> ValueError:
        return ValueError(f"Invalid `{field_path}` value {bad_value!r}. {fix_hint}")

    def _to_string_or_none(self, value: Any) -> str | None:
        if value is None:
            return None
        if isinstance(value, str):
            return value
        if isinstance(value, (RecipeType, PIRLVariantType)):
            return value.value
        return str(value)

    def _validate_positive_float(self, field_path: str, value: float | None) -> None:
        if value is None:
            raise self._format_validation_error(field_path, value, f"Set `--{field_path}=<positive float>`.")
        if value <= 0:
            raise self._format_validation_error(
                field_path,
                value,
                f"Expected a positive value for `{field_path}`. Set `--{field_path}=<positive float>`.",
            )

    def _validate_pi_rl_variant(self, variant: str) -> None:
        if variant == PIRLVariantType.FLOW_NOISE.value:
            self._validate_positive_float("pirl.flow_noise.std", self.pirl.flow_noise.std)
            return

        self._validate_positive_float("pirl.flow_sde.sigma_min", self.pirl.flow_sde.sigma_min)
        self._validate_positive_float("pirl.flow_sde.sigma_max", self.pirl.flow_sde.sigma_max)
        if self.pirl.flow_sde.sigma_max is not None and self.pirl.flow_sde.sigma_min is not None:
            if self.pirl.flow_sde.sigma_max <= self.pirl.flow_sde.sigma_min:
                raise self._format_validation_error(
                    "pirl.flow_sde.sigma_max",
                    self.pirl.flow_sde.sigma_max,
                    "`pirl.flow_sde.sigma_max` must be greater than `pirl.flow_sde.sigma_min`.",
                )

    def _validate_recipe(self) -> None:
        recipe_value = self._to_string_or_none(self.recipe)
        if recipe_value is None:
            return

        if recipe_value != PI_RL_RECIPE_VALUE:
            raise self._format_validation_error(
                "recipe",
                recipe_value,
                "Use canonical `pi-rl` (example: `--recipe=pi-rl`) or omit `recipe` for default behavior.",
            )

        variant = self._to_string_or_none(self.pirl.variant)
        if variant is None:
            raise self._format_validation_error(
                "pirl.variant",
                variant,
                "Set `--pirl.variant=flow-noise` or `--pirl.variant=flow-sde` when `recipe=pi-rl`.",
            )
        if variant not in PI_RL_RECIPE_ALLOWED_VARIANTS:
            raise self._format_validation_error(
                "pirl.variant",
                variant,
                "Expected one of ['flow-noise', 'flow-sde'].",
            )

        self._validate_positive_float("pirl.temperature", self.pirl.temperature)
        self._validate_positive_float("pirl.target_noise_scale", self.pirl.target_noise_scale)
        self._validate_pi_rl_variant(variant)

    def validate(self) -> None:
        self._validate_recipe()
        # HACK: We parse again the cli args here to get the pretrained paths if there was some.
        policy_path = parser.get_path_arg("policy")
        if policy_path:
            # Only load the policy config
            cli_overrides = parser.get_cli_overrides("policy")
            loaded_policy = PreTrainedConfig.from_pretrained(policy_path, cli_overrides=cli_overrides)
            loaded_policy.pretrained_path = Path(policy_path)
            self.policy = loaded_policy
        elif self.resume:
            # The entire train config is already loaded, we just need to get the checkpoint dir
            config_path = parser.parse_arg("config_path")
            if not config_path:
                raise ValueError(
                    f"A config_path is expected when resuming a run. Please specify path to {TRAIN_CONFIG_NAME}"
                )

            if not Path(config_path).resolve().exists():
                raise NotADirectoryError(
                    f"{config_path=} is expected to be a local path. "
                    "Resuming from the hub is not supported for now."
                )

            policy_dir = Path(config_path).parent
            if self.policy is not None:
                self.policy.pretrained_path = policy_dir
            self.checkpoint_path = policy_dir.parent

        if self.policy is None:
            raise ValueError(
                "Policy is not configured. Please specify a pretrained policy with `--policy.path`."
            )
        assert self.policy is not None

        if not self.job_name:
            if self.env is None:
                self.job_name = f"{self.policy.type}"
            else:
                self.job_name = f"{self.env.type}_{self.policy.type}"

        if not self.resume and isinstance(self.output_dir, Path) and self.output_dir.is_dir():
            raise FileExistsError(
                f"Output directory {self.output_dir} already exists and resume is {self.resume}. "
                f"Please change your output directory so that {self.output_dir} is not overwritten."
            )
        elif not self.output_dir:
            now = dt.datetime.now()
            train_dir = f"{now:%Y-%m-%d}/{now:%H-%M-%S}_{self.job_name}"
            self.output_dir = Path("outputs/train") / train_dir

        if isinstance(self.dataset.repo_id, list):
            raise NotImplementedError("LeRobotMultiDataset is not currently implemented.")

        if not self.use_policy_training_preset and (self.optimizer is None or self.scheduler is None):
            raise ValueError("Optimizer and Scheduler must be set when the policy presets are not used.")
        elif self.use_policy_training_preset and not self.resume:
            self.optimizer = self.policy.get_optimizer_preset()
            self.scheduler = self.policy.get_scheduler_preset()

        if self.policy.push_to_hub and not self.policy.repo_id:
            raise ValueError(
                "'policy.repo_id' argument missing. Please specify it to push the model to the hub."
            )

        if self.use_rabc and not self.rabc_progress_path:
            # Auto-detect from dataset path
            repo_id = self.dataset.repo_id
            if self.dataset.root:
                self.rabc_progress_path = str(Path(self.dataset.root) / "sarm_progress.parquet")
            else:
                self.rabc_progress_path = f"hf://datasets/{repo_id}/sarm_progress.parquet"

    @classmethod
    def __get_path_fields__(cls) -> list[str]:
        """This enables the parser to load config from the policy using `--policy.path=local/dir`"""
        return ["policy"]

    def to_dict(self) -> dict[str, Any]:
        return draccus.encode(self)  # type: ignore[no-any-return]  # because of the third-party library draccus uses Any as the return type

    def _save_pretrained(self, save_directory: Path) -> None:
        with open(save_directory / TRAIN_CONFIG_NAME, "w") as f, draccus.config_type("json"):
            draccus.dump(self, f, indent=4)

    @classmethod
    def from_pretrained(
        cls: builtins.type["TrainPipelineConfig"],
        pretrained_name_or_path: str | Path,
        *,
        force_download: bool = False,
        resume_download: bool | None = None,
        proxies: dict[Any, Any] | None = None,
        token: str | bool | None = None,
        cache_dir: str | Path | None = None,
        local_files_only: bool = False,
        revision: str | None = None,
        **kwargs: Any,
    ) -> "TrainPipelineConfig":
        model_id = str(pretrained_name_or_path)
        config_file: str | None = None
        if Path(model_id).is_dir():
            if TRAIN_CONFIG_NAME in os.listdir(model_id):
                config_file = os.path.join(model_id, TRAIN_CONFIG_NAME)
            else:
                print(f"{TRAIN_CONFIG_NAME} not found in {Path(model_id).resolve()}")
        elif Path(model_id).is_file():
            config_file = model_id
        else:
            try:
                config_file = hf_hub_download(
                    repo_id=model_id,
                    filename=TRAIN_CONFIG_NAME,
                    revision=revision,
                    cache_dir=cache_dir,
                    force_download=force_download,
                    proxies=proxies,
                    resume_download=resume_download,
                    token=token,
                    local_files_only=local_files_only,
                )
            except HfHubHTTPError as e:
                raise FileNotFoundError(
                    f"{TRAIN_CONFIG_NAME} not found on the HuggingFace Hub in {model_id}"
                ) from e

        cli_args = kwargs.pop("cli_args", [])
        with draccus.config_type("json"):
            return draccus.parse(cls, config_file, args=cli_args)


@dataclass(kw_only=True)
class TrainRLServerPipelineConfig(TrainPipelineConfig):
    # NOTE: In RL, we don't need an offline dataset
    # TODO: Make `TrainPipelineConfig.dataset` optional
    dataset: DatasetConfig | None = None  # type: ignore[assignment] # because the parent class has made it's type non-optional
