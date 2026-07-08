"""OpenTelemetry tracer and meter provider setup.

The functions here build and register OpenTelemetry ``TracerProvider`` and
``MeterProvider`` instances wired to OTLP exporters. No network connection is
established at construction time; exporters connect lazily when spans and
metrics are flushed, so these helpers are safe to call in tests.
"""

from __future__ import annotations

from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from obsplatform.config import Settings


def build_resource(settings: Settings) -> Resource:
    """Create an OpenTelemetry resource describing this service."""
    return Resource.create(
        {
            "service.name": settings.service_name,
            "deployment.environment": settings.env,
        }
    )


def configure_tracing(settings: Settings) -> TracerProvider:
    """Configure and register a global tracer provider.

    Args:
        settings: Application settings holding the OTLP endpoint.

    Returns:
        The registered :class:`TracerProvider`.
    """
    provider = TracerProvider(resource=build_resource(settings))
    exporter = OTLPSpanExporter(endpoint=settings.otlp_endpoint, insecure=True)
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    return provider


def configure_metrics(settings: Settings) -> MeterProvider:
    """Configure and register a global meter provider.

    Args:
        settings: Application settings holding the OTLP endpoint.

    Returns:
        The registered :class:`MeterProvider`.
    """
    exporter = OTLPMetricExporter(endpoint=settings.otlp_endpoint, insecure=True)
    reader = PeriodicExportingMetricReader(exporter)
    provider = MeterProvider(resource=build_resource(settings), metric_readers=[reader])
    metrics.set_meter_provider(provider)
    return provider
