"""Telemetry pipeline descriptions and a small registry.

These dataclasses model the three signal pipelines (metrics, logs, traces)
that the platform operates. The :class:`PipelineRegistry` provides a typed,
serialisable view used by the collector configuration and documentation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Signal(str, Enum):
    """The three observability signal types."""

    METRICS = "metrics"
    LOGS = "logs"
    TRACES = "traces"


@dataclass(frozen=True, slots=True)
class Pipeline:
    """A single telemetry pipeline.

    Attributes:
        signal: The signal type this pipeline processes.
        receivers: Names of collector receivers feeding the pipeline.
        processors: Names of collector processors applied in order.
        exporters: Names of collector exporters the pipeline fans out to.
    """

    signal: Signal
    receivers: list[str]
    processors: list[str]
    exporters: list[str]

    def as_dict(self) -> dict[str, list[str]]:
        """Return the pipeline as a collector-style mapping."""
        return {
            "receivers": list(self.receivers),
            "processors": list(self.processors),
            "exporters": list(self.exporters),
        }


@dataclass(slots=True)
class PipelineRegistry:
    """Registry mapping each :class:`Signal` to its :class:`Pipeline`."""

    pipelines: dict[Signal, Pipeline] = field(default_factory=dict)

    def register(self, pipeline: Pipeline) -> None:
        """Register (or replace) a pipeline for its signal."""
        self.pipelines[pipeline.signal] = pipeline

    def get(self, signal: Signal) -> Pipeline:
        """Return the pipeline registered for ``signal``."""
        return self.pipelines[signal]

    def signals(self) -> list[Signal]:
        """Return the registered signals in a stable order."""
        return [s for s in Signal if s in self.pipelines]


def default_registry() -> PipelineRegistry:
    """Build the platform's default metrics/logs/traces pipeline registry."""
    registry = PipelineRegistry()
    registry.register(
        Pipeline(
            signal=Signal.TRACES,
            receivers=["otlp"],
            processors=["memory_limiter", "batch"],
            exporters=["otlp/tempo"],
        )
    )
    registry.register(
        Pipeline(
            signal=Signal.METRICS,
            receivers=["otlp"],
            processors=["memory_limiter", "batch"],
            exporters=["prometheus"],
        )
    )
    registry.register(
        Pipeline(
            signal=Signal.LOGS,
            receivers=["otlp"],
            processors=["memory_limiter", "batch"],
            exporters=["loki"],
        )
    )
    return registry
