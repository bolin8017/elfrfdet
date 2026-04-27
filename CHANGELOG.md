# Changelog

## [2.0.3] - 2026-04-27

### Fixed

- Pins `maldet>=1.0.3,<2.0` (was `>=1.0,<2.0`) so pip cannot resolve to an
  older version. The v2.0.2 build hit a PyPI/CDN propagation race and pulled
  maldet 1.0.2 instead of 1.0.3, which kept the runner on the old
  Hydra-instantiate path and reproduced the "Missing key model" failure.

## [2.0.2] - 2026-04-27

### Fixed

- Pulls maldet >=1.0.3 transitively. v1.0.3 changes `StageRunner` to load the
  model class from the manifest's `[stages.train].model` symbol instead of
  Hydra-instantiating from `cfg.model._target_`. Unblocks lolday Phase 11d
  E2E, where the params guard forbids `_target_` overrides, leaving the
  v2.0.0/v2.0.1 train path crashing with `ConfigAttributeError: Missing key
  model`. No source changes here — bump exists to retrigger the lolday build
  pipeline against the patched framework.

## [2.0.1] - 2026-04-27

### Fixed

- Pulls maldet >=1.0.2 transitively, which now skips per-sample feature-extractor
  ValueErrors (e.g. ELF samples lacking `.text` for `Text256Extractor`) instead of
  aborting the whole train run on the first bad sample. No source changes here —
  bump exists to retrigger the lolday build pipeline against the patched framework.

## [2.0.0] - 2026-04-26

### Breaking

- Full rewrite on top of [maldet 1.0](https://pypi.org/project/maldet/).
- Removed: v0 `BaseDetector` ABC, `ElfRfDetectorConfig` pydantic model, per-detector `elfrfdet` CLI.
- Package layout changed: `src/elfrfdet/{cli.py, config.py, detector.py, text256.py}` deleted; new `src/elfrfdet/{features.py, models.py}`. `from elfrfdet.detector import ElfRfDetector` and `from elfrfdet.text256 import …` no longer work.
- Configuration is now Hydra YAML + `maldet.toml`. CLI is `maldet run train|evaluate|predict --config <yaml>`.
- Dockerfile expects build-time args (`MALDET_NAME`, `MALDET_VERSION`, `MALDET_FRAMEWORK`, `MALDET_MANIFEST_B64`, `GIT_COMMIT`) emitted as OCI image labels — required by lolday's build pipeline (image-label contract).

## [0.1.1] - 2026-04-21

Final v0 release on the `islab-malware-detector` framework. Deprecated.
