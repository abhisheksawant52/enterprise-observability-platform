"""Tests for the OpenTelemetry Collector configuration builder."""

from obsplatform.collector import build_collector_config
from obsplatform.config import Settings
from obsplatform.pipelines import Signal, default_registry


def test_collector_has_otlp_receiver() -> None:
    config = build_collector_config(Settings())
    assert "otlp" in config["receivers"]
    protocols = config["receivers"]["otlp"]["protocols"]
    assert "grpc" in protocols
    assert "http" in protocols


def test_collector_has_expected_exporters() -> None:
    config = build_collector_config(Settings())
    exporters = config["exporters"]
    assert "prometheus" in exporters
    assert "loki" in exporters
    assert "otlp/tempo" in exporters


def test_collector_pipelines_cover_all_signals() -> None:
    config = build_collector_config(Settings())
    pipelines = config["service"]["pipelines"]
    for signal in Signal:
        assert signal.value in pipelines
    assert config["service"]["pipelines"]["traces"]["exporters"] == ["otlp/tempo"]


def test_exporter_endpoints_follow_settings() -> None:
    settings = Settings(tempo_endpoint="http://tempo.example:4317")
    config = build_collector_config(settings, default_registry())
    assert config["exporters"]["otlp/tempo"]["endpoint"] == "http://tempo.example:4317"
