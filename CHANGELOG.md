# Changelog

## [2.0.0] - 2026-04-26

### Breaking

- Full rewrite on top of [maldet 1.0](https://pypi.org/project/maldet/).
- Removed: v0 `BaseDetector` ABC, `ElfRfDetectorConfig` pydantic model, per-detector `elfrfdet` CLI.
- Package layout changed: `src/elfrfdet/{cli.py, config.py, detector.py, text256.py}` deleted; new `src/elfrfdet/{features.py, models.py}`. `from elfrfdet.detector import ElfRfDetector` and `from elfrfdet.text256 import …` no longer work.
- Configuration is now Hydra YAML + `maldet.toml`. CLI is `maldet run train|evaluate|predict --config <yaml>`.
- Dockerfile expects build-time args (`MALDET_NAME`, `MALDET_VERSION`, `MALDET_FRAMEWORK`, `MALDET_MANIFEST_B64`, `GIT_COMMIT`) emitted as OCI image labels — required by lolday's build pipeline (image-label contract).

## [0.1.1] - 2026-04-21

Final v0 release on the `islab-malware-detector` framework. Deprecated.
