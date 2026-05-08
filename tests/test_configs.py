"""Pydantic config classes for elfrfdet stages — used by maldet 1.1 introspect-schema."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from elfrfdet.configs import EvaluateConfig, PredictConfig, TrainConfig


def test_train_config_defaults() -> None:
    cfg = TrainConfig()
    assert cfg.n_estimators == 100
    assert cfg.max_depth is None
    assert cfg.random_state == 42


def test_train_config_rejects_extras() -> None:
    with pytest.raises(ValidationError):
        TrainConfig(unknown_field=1)


def test_train_config_rejects_zero_n_estimators() -> None:
    with pytest.raises(ValidationError):
        TrainConfig(n_estimators=0)


def test_evaluate_config_rejects_extras() -> None:
    with pytest.raises(ValidationError):
        EvaluateConfig(unknown=1)


def test_predict_config_defaults() -> None:
    cfg = PredictConfig()
    assert cfg.batch_size == 256


def test_predict_config_rejects_extras() -> None:
    with pytest.raises(ValidationError):
        PredictConfig(unknown=1)


def test_train_config_max_depth_accepts_none_and_positive() -> None:
    TrainConfig(max_depth=None)
    TrainConfig(max_depth=10)
    with pytest.raises(ValidationError):
        TrainConfig(max_depth=0)
