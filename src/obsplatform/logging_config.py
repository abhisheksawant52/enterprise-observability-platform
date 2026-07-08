"""Structured logging configuration.

Configures both the standard library ``logging`` module and ``structlog`` so
that all log records are emitted as JSON, making them straightforward to ship
to Loki via the OpenTelemetry Collector.
"""

from __future__ import annotations

import logging
import sys

import structlog


def configure_logging(level: str = "INFO") -> structlog.stdlib.BoundLogger:
    """Configure JSON structured logging.

    Args:
        level: Root log level name (e.g. ``"INFO"``, ``"DEBUG"``).

    Returns:
        A configured, bound structlog logger ready for use.
    """
    log_level = getattr(logging, level.upper(), logging.INFO)

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )

    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    return structlog.get_logger()


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Return a bound structlog logger, optionally namespaced by ``name``."""
    if name:
        return structlog.get_logger(name)
    return structlog.get_logger()
