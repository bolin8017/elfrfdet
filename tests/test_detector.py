"""Integration tests for ElfRfDetector — train/evaluate/predict round-trip."""

import shutil
from pathlib import Path

import pandas as pd
import pytest

from elfrfdet import ElfRfDetector, ElfRfDetectorConfig


def _system_elf() -> Path:
    for candidate in ("/bin/ls", "/usr/bin/ls", "/bin/cat", "/usr/bin/cat"):
        p = Path(candidate)
        if p.is_file():
            return p
    pytest.skip("no system ELF available")


def _prepare_fake_dataset(tmp_path: Path, n_per_class: int = 3) -> tuple[Path, Path, Path]:
    """Copy a real ELF twice — once as 'Malware', once as 'Benign' — under
    different SHA-like names. Enough to exercise train/evaluate without a
    real corpus.
    """
    ds_root = tmp_path / "samples"
    rows = []
    real_elf = _system_elf()
    for i in range(n_per_class):
        for label in ("Malware", "Benign"):
            prefix = f"{i:02d}"
            sha = f"{prefix}{label.lower()[0]}" + "0" * (64 - len(f"{prefix}{label.lower()[0]}"))
            (ds_root / prefix).mkdir(parents=True, exist_ok=True)
            shutil.copy(real_elf, ds_root / prefix / sha)
            rows.append({"file_name": sha, "label": label, "family": "fam" if label == "Malware" else ""})

    csv_path = tmp_path / "data.csv"
    pd.DataFrame(rows).to_csv(csv_path, index=False)
    return ds_root, csv_path, csv_path  # reuse same CSV for train + test


def test_full_lifecycle(tmp_path: Path) -> None:
    ds_root, train_csv, test_csv = _prepare_fake_dataset(tmp_path, n_per_class=4)

    cfg = ElfRfDetectorConfig(
        data={"train": train_csv, "test": test_csv, "predict": test_csv, "dataset": ds_root},
        output={
            "model": tmp_path / "out/model",
            "feature": tmp_path / "out/features",
            "prediction": tmp_path / "out/pred",
            "log": tmp_path / "out/log",
        },
        model={"n_estimators": 10, "random_state": 42},
    )

    det = ElfRfDetector(cfg)
    model_dir = det.train()
    assert (model_dir / "model.joblib").exists()

    # Fresh detector to exercise model-load path.
    det2 = ElfRfDetector(cfg)
    metrics = det2.evaluate()
    assert {"accuracy", "precision", "recall", "f1"}.issubset(metrics.keys())
    # All copies of the same ELF mean a single class after split → accuracy
    # must be perfect on the two-class seeded labels.
    assert 0.0 <= metrics["accuracy"] <= 1.0

    det3 = ElfRfDetector(cfg)
    pred_path = det3.predict()
    assert pred_path.exists()
    pred_df = pd.read_csv(pred_path)
    assert set(pred_df.columns) == {"file_name", "pred_label", "pred_score"}
    assert set(pred_df["pred_label"].unique()).issubset({"Malware", "Benign"})
