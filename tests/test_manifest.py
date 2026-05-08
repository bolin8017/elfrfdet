"""Tests for maldet.toml shape — guard against accidental drift."""

from __future__ import annotations

from pathlib import Path

from maldet.manifest import load_manifest

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_manifest_loads_via_maldet() -> None:
    m = load_manifest(REPO_ROOT / "maldet.toml")
    assert m.detector.name == "elfrfdet"
    assert m.detector.version == "4.1.0"
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


def test_manifest_has_config_class_per_stage() -> None:
    m = load_manifest(REPO_ROOT / "maldet.toml")
    assert m.stages["train"].config_class == "elfrfdet.configs:TrainConfig"
    assert m.stages["evaluate"].config_class == "elfrfdet.configs:EvaluateConfig"
    assert m.stages["predict"].config_class == "elfrfdet.configs:PredictConfig"
    # params_schema is the placeholder — populated by `maldet build`
    assert m.stages["train"].params_schema == {}
    assert m.stages["evaluate"].params_schema == {}
    assert m.stages["predict"].params_schema == {}


def test_introspect_schema_for_train_config_is_valid_json_schema(tmp_path: Path) -> None:
    """Round-trip: TrainConfig → introspect-schema → JSON Schema with the right shape."""
    import json

    from maldet.cli import app
    from typer.testing import CliRunner

    out = tmp_path / "train_schema.json"
    runner = CliRunner()
    result = runner.invoke(
        app,
        ["introspect-schema", "--config-class", "elfrfdet.configs:TrainConfig", "--out", str(out)],
    )
    assert result.exit_code == 0, (result.stdout, result.stderr)
    schema = json.loads(out.read_text())
    assert schema.get("additionalProperties") is False
    assert "n_estimators" in schema["properties"]
    assert schema["properties"]["n_estimators"]["minimum"] == 1
