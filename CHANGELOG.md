# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-07-08

### Added

- `obsplatform` FastAPI service exposing `/health`, `/ready`, and `/metrics`
  (Prometheus exposition format).
- OpenTelemetry tracing and metrics provider setup with OTLP exporters
  (`obsplatform.telemetry`).
- Structured JSON logging via structlog (`obsplatform.logging_config`).
- `OBS_`-prefixed settings via pydantic-settings (`obsplatform.config`) with a
  documented `.env.example`.
- Telemetry pipeline model and registry (`obsplatform.pipelines`) plus an
  OpenTelemetry Collector config generator (`obsplatform.collector`).
- Deployment assets: OTel Collector config, Prometheus scrape config, Grafana
  datasource provisioning, a Helm chart, and plain Kubernetes manifests.
- Multi-stage, non-root Dockerfile with a `/health` healthcheck.
- Test suite covering the HTTP endpoints and collector configuration.
- Documentation (README with architecture diagram, `docs/architecture.md`),
  CI pipeline, pre-commit hooks, and open-source project files.
