"""Random Forest ELF malware detector.

Inherits from maldet.BaseDetector. Implements the train/evaluate/predict
contract using sklearn.ensemble.RandomForestClassifier on a `(N, size)`
uint8 matrix — each row is the first `size` bytes of the sample's `.text`
section.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from maldet import BaseDetector
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)

from .config import ElfRfDetectorConfig
from .text256 import extract_text256

MODEL_FILENAME = "model.joblib"


class ElfRfDetector(BaseDetector):
    """RandomForest detector over the first 256 bytes of `.text`."""

    config_class = ElfRfDetectorConfig

    def __init__(self, config: ElfRfDetectorConfig | None = None) -> None:
        super().__init__(config)
        self._model: RandomForestClassifier | None = None
        self.logger.info(
            "detector_initialized",
            n_estimators=self.config.model.n_estimators,
            feature_size=self.config.feature.size,
        )

    def train(self) -> Path:
        df = self._load_csv(self.config.data.train)
        X, y = self._build_matrix(df)
        self.logger.info("training_started", samples=X.shape[0], features=X.shape[1])

        self._model = RandomForestClassifier(
            n_estimators=self.config.model.n_estimators,
            max_depth=self.config.model.max_depth,
            min_samples_split=self.config.model.min_samples_split,
            min_samples_leaf=self.config.model.min_samples_leaf,
            n_jobs=self.config.model.n_jobs,
            random_state=self.config.model.random_state,
        )
        self._model.fit(X, y)

        model_dir = self.config.output.model
        self.ensure_directory_exists(model_dir)
        model_path = model_dir / MODEL_FILENAME
        joblib.dump(self._model, model_path)
        self.logger.info("training_completed", model_path=str(model_path))
        return model_dir

    def evaluate(self) -> dict[str, Any]:
        if self._model is None:
            self._load_model()
        df = self._load_csv(self.config.data.test)
        X, y = self._build_matrix(df)
        self.logger.info("evaluation_started", samples=X.shape[0])

        y_pred = self._model.predict(X)
        metrics = {
            "accuracy": float(accuracy_score(y, y_pred)),
            "precision": float(precision_score(y, y_pred, zero_division=0)),
            "recall": float(recall_score(y, y_pred, zero_division=0)),
            "f1": float(f1_score(y, y_pred, zero_division=0)),
            "confusion_matrix": confusion_matrix(y, y_pred).tolist(),
            "n_samples": int(X.shape[0]),
        }
        self.logger.info(
            "evaluation_completed", accuracy=metrics["accuracy"], f1=metrics["f1"]
        )
        return metrics

    def predict(self) -> Path:
        if self._model is None:
            self._load_model()
        df = self._load_csv(self.config.data.predict)
        X, _ = self._build_matrix(df, require_labels=False)
        self.logger.info("prediction_started", samples=X.shape[0])

        probs = self._model.predict_proba(X)
        malware_idx = list(self._model.classes_).index(1)
        malware_scores = probs[:, malware_idx]
        preds = self._model.predict(X)

        out_df = pd.DataFrame({
            "file_name": df["file_name"].values,
            "pred_label": ["Malware" if p == 1 else "Benign" for p in preds],
            "pred_score": malware_scores,
        })

        out_path = self.config.output.prediction
        self.ensure_directory_exists(out_path)
        # Platform reads predictions.csv regardless of output.prediction's
        # basename, so preserve the filename upxelfdet set as convention.
        if out_path.is_dir() or out_path.suffix == "":
            out_path = out_path / "predictions.csv"
        out_df.to_csv(out_path, index=False)
        self.logger.info("prediction_completed", output=str(out_path))
        return out_path

    def _load_csv(self, path: Path) -> pd.DataFrame:
        if not path.exists():
            raise FileNotFoundError(f"dataset CSV not found: {path}")
        df = pd.read_csv(path)
        if "file_name" not in df.columns:
            raise ValueError(f"{path}: CSV missing 'file_name' column")
        return df

    def _build_matrix(
        self, df: pd.DataFrame, require_labels: bool = True
    ) -> tuple[np.ndarray, np.ndarray]:
        """Extract `.text[:size]` for every row. Drop rows that fail to parse.

        Returns (X, y) where y is int array (1=Malware, 0=Benign). When
        `require_labels=False` (predict), y is an empty array.
        """
        dataset_root = self.config.data.dataset
        size = self.config.feature.size

        vectors: list[np.ndarray] = []
        labels: list[int] = []
        kept_rows: list[int] = []

        for idx, row in df.iterrows():
            sha = row["file_name"]
            sample_path = dataset_root / sha[:2] / sha
            try:
                vec = extract_text256(sample_path, size=size)
            except (FileNotFoundError, ValueError) as exc:
                self.logger.warning(
                    "sample_skipped", file=sha, reason=str(exc)
                )
                continue
            vectors.append(vec)
            kept_rows.append(idx)
            if require_labels:
                label = row.get("label")
                if label not in ("Malware", "Benign"):
                    raise ValueError(
                        f"row {idx}: label must be 'Malware' or 'Benign', got {label!r}"
                    )
                labels.append(1 if label == "Malware" else 0)

        if not vectors:
            raise RuntimeError("no valid samples after feature extraction")

        # Trim the DataFrame in-place so callers see the aligned rows.
        df.drop(index=[i for i in df.index if i not in kept_rows], inplace=True)
        df.reset_index(drop=True, inplace=True)

        X = np.stack(vectors).astype(np.uint8)
        y = np.asarray(labels, dtype=np.int64) if require_labels else np.array([])
        return X, y

    def _load_model(self) -> None:
        model_path = self.config.output.model / MODEL_FILENAME
        if not model_path.exists():
            raise FileNotFoundError(f"trained model not found: {model_path}")
        self._model = joblib.load(model_path)
        self.logger.info("model_loaded", path=str(model_path))
