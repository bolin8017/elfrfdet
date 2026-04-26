"""Tests for maldet.toml shape — guard against accidental drift."""

from __future__ import annotations

from pathlib import Path

from maldet.manifest import load_manifest


REPO_ROOT = Path(__file__).resolve().parent.parent


def test_manifest_loads_via_maldet() -> None:
    m = load_manifest(REPO_ROOT / "maldet.toml")
    assert m.detector.name == "elfrfdet"
    assert m.detector.version == "2.0.0"
    assert m.detector.framework == "sklearn"


def test_manifest_resources_cpu_only() -> None:
    m = load_manifest(REPO_ROOT / "maldet.toml")
    assert m.resources.supports == ["cpu"]
    assert m.resources.gpu_required is False


def test_manifest_lifecycle_no_distributed() -> None:
    m = load_manifest(REPO_ROOT / "maldet.toml")
    assert m.lifecycle.supports_distributed is False
    assert set(m.lifecycle.stages) == {"train", "evaluate", "predict"}


def test_manifest_stages_reference_local_extractor() -> None:
    m = load_manifest(REPO_ROOT / "maldet.toml")
    train = m.stages["train"]
    assert train.extractor == "elfrfdet.features:Text256Extractor"
    assert train.model == "elfrfdet.models:make_rf"
    assert train.trainer == "maldet.trainers.sklearn_trainer:SklearnTrainer"
