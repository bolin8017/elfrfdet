# elfrfdet

Random Forest malware detector for Linux ELF binaries. Feature = first 256
bytes of the `.text` section, as a `uint8` vector.

Built as a template for the
[lolday](https://github.com/louiskyee/lolday) platform — inherits the
[islab-malware-detector](https://github.com/bolin8017/islab-malware-detector)
`BaseDetector` spec.

## Usage

### CLI

```bash
elfrfdet init --output config.json   # generate default config
elfrfdet train    --config config.json
elfrfdet evaluate --config config.json
elfrfdet predict  --config config.json
```

### Dataset format

CSV with columns `file_name,label[,family]`. `file_name` is a SHA-256 string;
the actual ELF file lives at `<dataset_root>/<sha[:2]>/<sha>`. `label` is
`Malware` or `Benign`.

### On lolday

1. Register: `POST /api/v1/detectors { git_url: "https://github.com/bolin8017/elfrfdet.git" }`
2. Build a tag: `POST /api/v1/detectors/{id}/builds { git_tag: "v0.1.0" }`
3. Submit jobs: `POST /api/v1/jobs { type: "train", ... }` — `resource_profile` defaults to `standard` (1 GPU allocation, unused).

## How it works

1. **Feature extraction** (`text256.py`): open each ELF with `pyelftools`,
   grab `.text.data()[:256]`, zero-pad to 256 bytes if shorter.
2. **Model** (`detector.py`): `sklearn.ensemble.RandomForestClassifier`
   trained on the stacked `(N, 256)` uint8 matrix. Evaluation reports
   accuracy / precision / recall / F1.
3. **Output** (`predict`): writes `predictions.csv` with columns
   `file_name,pred_label,pred_score`.

## License

MIT
