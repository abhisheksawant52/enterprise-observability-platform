"""FastAPI application exposing health, readiness, and metrics endpoints.

The app wires configuration, structured logging, and OpenTelemetry providers
on startup, and exposes a Prometheus scrape endpoint via ``prometheus_client``.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, generate_latest

from obsplatform import __version__
from obsplatform.config import Settings, get_settings
from obsplatform.logging_config import configure_logging, get_logger
from obsplatform.telemetry import configure_metrics, configure_tracing

REQUESTS = Counter(
    "obsplatform_requests_total",
    "Total HTTP requests received, labelled by endpoint.",
    ["endpoint"],
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Initialise logging and telemetry providers on startup."""
    settings: Settings = app.state.settings
    logger = configure_logging(settings.log_level)
    configure_tracing(settings)
    configure_metrics(settings)
    logger.info(
        "startup",
        service=settings.service_name,
        env=settings.env,
        version=__version__,
    )
    yield
    get_logger().info("shutdown", service=settings.service_name)


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create and configure the FastAPI application instance.

    Args:
        settings: Optional settings override; loaded from the environment
            when omitted.

    Returns:
        A configured :class:`fastapi.FastAPI` application.
    """
    settings = settings or get_settings()
    app = FastAPI(
        title="Enterprise Observability Platform",
        version=__version__,
        lifespan=lifespan,
    )
    app.state.settings = settings

    @app.get("/health", tags=["ops"])
    def health() -> dict[str, str]:
        """Liveness probe; always returns ``ok`` when the process is up."""
        REQUESTS.labels(endpoint="/health").inc()
        return {"status": "ok", "version": __version__}

    @app.get("/ready", tags=["ops"])
    def ready() -> dict[str, str]:
        """Readiness probe; reports whether the service can accept traffic."""
        REQUESTS.labels(endpoint="/ready").inc()
        return {"status": "ready", "service": settings.service_name}

    @app.get("/metrics", tags=["ops"])
    def metrics() -> Response:
        """Expose Prometheus metrics in the text exposition format."""
        return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

    return app


app = create_app()


def run() -> None:
    """Console-script entrypoint: serve the app with uvicorn."""
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "obsplatform.main:app",
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    run()
