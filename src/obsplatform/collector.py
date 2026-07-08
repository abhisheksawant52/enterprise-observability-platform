"""OpenTelemetry Collector configuration generation.

Builds an in-memory representation of a Collector configuration (receivers,
processors, exporters, and service pipelines) from application settings, and
renders it to YAML. The generated document mirrors ``deploy/otel-collector-
config.yaml`` and can be used to validate the two stay in sync.
"""

from __future__ import annotations

from typing import Any

from obsplatform.config import Settings
from obsplatform.pipelines import PipelineRegistry, default_registry


def build_collector_config(
    settings: Settings,
    registry: PipelineRegistry | None = None,
) -> dict[str, Any]:
    """Build an OpenTelemetry Collector configuration dictionary.

    Args:
        settings: Application settings supplying exporter endpoints.
        registry: Pipeline registry to render; defaults to
            :func:`obsplatform.pipelines.default_registry`.

    Returns:
        A nested dictionary matching the Collector config schema, with
        ``receivers``, ``processors``, ``exporters``, and ``service`` keys.
    """
    registry = registry or default_registry()

    receivers: dict[str, Any] = {
        "otlp": {
            "protocols": {
                "grpc": {"endpoint": "0.0.0.0:4317"},
                "http": {"endpoint": "0.0.0.0:4318"},
            }
        }
    }

    processors: dict[str, Any] = {
        "batch": {"timeout": "5s", "send_batch_size": 1024},
        "memory_limiter": {
            "check_interval": "1s",
            "limit_percentage": 80,
            "spike_limit_percentage": 25,
        },
    }

    exporters: dict[str, Any] = {
        "prometheus": {"endpoint": f"0.0.0.0:{settings.prometheus_port}"},
        "loki": {"endpoint": settings.loki_endpoint},
        "otlp/tempo": {
            "endpoint": settings.tempo_endpoint,
            "tls": {"insecure": True},
        },
    }

    service_pipelines = {
        signal.value: registry.get(signal).as_dict() for signal in registry.signals()
    }

    return {
        "receivers": receivers,
        "processors": processors,
        "exporters": exporters,
        "service": {
            "telemetry": {"logs": {"level": settings.log_level.lower()}},
            "pipelines": service_pipelines,
        },
    }


def render_collector_yaml(
    settings: Settings,
    registry: PipelineRegistry | None = None,
) -> str:
    """Render the collector configuration to a YAML string.

    Requires ``PyYAML``; it is a transitive dependency of the OpenTelemetry
    SDK and is therefore available at runtime.
    """
    import yaml

    config = build_collector_config(settings, registry)
    return yaml.safe_dump(config, sort_keys=False, default_flow_style=False)
