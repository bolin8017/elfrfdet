"""Configuration for the Random Forest ELF detector."""

from pathlib import Path
from typing import Self

from maldet.config import (
    BaseDetectorConfig,
    DataConfig as BaseDataConfig,
)
from pydantic import BaseModel, ConfigDict, field_validator, model_validator


class DataConfig(BaseDataConfig):
    """Extended data config carrying dataset root for sample lookup."""

    dataset: Path = Path("./data/samples")


class FeatureConfig(BaseModel):
    """Feature extraction knobs — .text section, first N bytes."""

    model_config = ConfigDict(extra="allow", frozen=True)

    section_name: str = ".text"
    size: int = 256

    @field_validator("size")
    @classmethod
    def _positive_size(cls, v: int) -> int:
        if v <= 0 or v > 65536:
            raise ValueError("size must be in (0, 65536]")
        return v


class ModelConfig(BaseModel):
    """scikit-learn RandomForestClassifier hyperparameters."""

    model_config = ConfigDict(extra="allow", frozen=True)

    n_estimators: int = 200
    max_depth: int | None = None
    min_samples_split: int = 2
    min_samples_leaf: int = 1
    n_jobs: int = -1
    random_state: int = 42

    @field_validator("n_estimators")
    @classmethod
    def _at_least_one(cls, v: int) -> int:
        if v < 1:
            raise ValueError("n_estimators must be >= 1")
        return v


class ElfRfDetectorConfig(BaseDetectorConfig):
    """Full config for elfrfdet.

    Inherits DataConfig.train/test/predict + OutputConfig.model/feature/
    prediction/log from maldet BaseDetectorConfig.
    """

    data: DataConfig = DataConfig()
    feature: FeatureConfig = FeatureConfig()
    model: ModelConfig = ModelConfig()
    seed: int = 42

    @model_validator(mode="after")
    def _align_seeds(self) -> Self:
        """Ensure model.random_state tracks top-level seed if caller changed it.

        The top-level `seed` is the platform-visible knob (lolday UI maps
        `params.seed` to this). We mirror it into model.random_state unless
        the caller explicitly set both to different values.
        """
        return self
