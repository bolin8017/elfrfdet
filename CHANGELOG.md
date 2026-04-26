# Changelog

## [2.0.0] - 2026-04-26

### Breaking

- Full rewrite on top of [maldet 1.0](https://pypi.org/project/maldet/).
- Removed: v0 `BaseDetector` ABC, `ElfRfDetectorConfig` pydantic model, per-detector `elfrfdet` CLI.
- Configuration is now Hydra YAML + `maldet.toml`. CLI is `maldet run train|evaluate|predict --config <yaml>`.
- Dockerfile expects build-time args (`MALDET_NAME`, `MALDET_VERSION`, `MALDET_FRAMEWORK`, `MALDET_MANIFEST_B64`, `GIT_COMMIT`) emitted as OCI image labels — required by lolday Phase 11c's pipeline.

## [0.1.1] - 2026-(prior)

Final v0 release on the `islab-malware-detector` framework. Deprecated.
