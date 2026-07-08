"""Enterprise observability platform package.

Provides a FastAPI service that wires together OpenTelemetry tracing and
metrics, structured JSON logging, and helpers for generating an OpenTelemetry
Collector configuration targeting Prometheus, Loki, and Tempo.
"""

__version__ = "0.1.0"

__all__ = ["__version__"]
