# elfrfdet

Random Forest malware detector for Linux ELF binaries. Feature = first 256 bytes of the `.text` section, as a `uint8` vector. Reference template for the [lolday](https://github.com/louiskyee/lolday) platform on the [maldet 1.0](https://github.com/bolin8017/maldet) framework.

## Install

```bash
pip install -e .[dev]
maldet check
maldet describe
```

## CLI

```bash
maldet run train    --config config.yaml
maldet run evaluate --config config.yaml
maldet run predict  --config config.yaml
```

A minimal `config.yaml` for local smoke-testing:

```yaml
defaults: [_self_]
stage: train
paths:
  config_dir: ${oc.env:PWD}
  output_dir: /tmp/elfrfdet-out
  samples_root: /path/to/samples           # <sha[:2]>/<sha> layout
  source_model: /tmp/elfrfdet-out/model
data:
  train_csv: /path/to/train.csv            # columns: file_name,label[,family]
  test_csv:  /path/to/test.csv
  predict_csv: /path/to/predict.csv
model:
  _target_: sklearn.ensemble.RandomForestClassifier
  n_estimators: 100
  random_state: 42
```

## Dataset format

CSV with columns `file_name,label[,family]`. `file_name` is a SHA-256 hex string; the actual ELF lives at `<samples_root>/<sha[:2]>/<sha>`. `label` is `Malware` or `Benign`.

## How it works

1. **Feature extraction** (`src/elfrfdet/features.py::Text256Extractor`): open each ELF with `pyelftools`, read `.text.data()[:256]`, zero-pad to 256 bytes if shorter. All three operations — `ELFFile(f)`, `get_section_by_name(".text")`, and `section.data()` — share one `try/except` block because pyelftools lazy-parses the section-header string table; `ELFParseError` can fire on the section access (or even on `data()`), not just on the `ELFFile(f)` constructor.
2. **Model** (`src/elfrfdet/models.py::make_rf`): `sklearn.ensemble.RandomForestClassifier`, default `n_estimators=100`.
3. **Output**: `model/model.joblib`, `metrics.json`, `predictions.csv`, `events.jsonl` under `paths.output_dir`.

## On lolday

1. Register: `POST /api/v1/detectors { git_url: "https://github.com/bolin8017/elfrfdet.git" }` — lolday's detector validator parses `maldet.toml` and creates the Detector row.
2. Build a tag: `POST /api/v1/detectors/{id}/builds { git_tag: "v2.0.0" }`.
3. Submit a job: `POST /api/v1/jobs { type: "train", resource_profile: "standard", ... }`. With `manifest.resources.supports = ["cpu"]`, only `standard` (cpu) jobs are accepted; multi-GPU profiles are rejected by lolday's job-submission validator (CPU-only manifest).

## Migrating from v0.1.x

v2 is a full rewrite on the maldet 1.0 framework — incompatible with v0's `BaseDetector` ABC. The v0 `ElfRfDetectorConfig` Pydantic model is gone; configuration flows through Hydra YAML and `maldet.toml`. The v0 `elfrfdet` CLI command no longer exists; use `maldet run <stage>`. v0 tags (`v0.1.1` and earlier) remain on this repo for historical reference but are deprecated.

## License

MIT
