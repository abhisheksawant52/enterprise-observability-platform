"""Application configuration.

Settings are loaded from environment variables (prefixed with ``OBS_``) and an
optional ``.env`` file. See ``.env.example`` for the full list of supported
variables.
"""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration for the observability platform service.

    Attributes:
        service_name: Logical name reported to OpenTelemetry and used as the
            ``service.name`` resource attribute.
        env: Deployment environment label (e.g. ``dev``, ``staging``, ``prod``).
        log_level: Root logging level (e.g. ``INFO``, ``DEBUG``).
        host: Interface the HTTP server binds to.
        port: Port the HTTP server listens on.
        otlp_endpoint: OTLP gRPC endpoint of the OpenTelemetry Collector.
        prometheus_port: Port exposing the Prometheus scrape endpoint.
        loki_endpoint: Loki push API endpoint used by the collector.
        tempo_endpoint: Tempo OTLP endpoint used by the collector.
    """

    model_config = SettingsConfigDict(
        env_prefix="OBS_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    service_name: str = "observability-platform"
    env: str = "dev"
    log_level: str = "INFO"

    host: str = "0.0.0.0"
    port: int = 8000

    otlp_endpoint: str = "http://otel-collector:4317"
    prometheus_port: int = 9464
    loki_endpoint: str = "http://loki:3100/loki/api/v1/push"
    tempo_endpoint: str = "http://tempo:4317"


def get_settings() -> Settings:
    """Return a freshly loaded :class:`Settings` instance."""
    return Settings()
