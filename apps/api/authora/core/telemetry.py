"""Telemetry layer - metrics, traces, logs."""

import os
from contextlib import contextmanager
from typing import Any, Generator


def is_telemetry_enabled() -> bool:
    """Check if telemetry is enabled."""
    return os.environ.get("TELEMETRY_ENABLED", "false").lower() == "true"


@contextmanager
def trace_span(name: str, attributes: dict[str, Any] | None = None) -> Generator[None, None, None]:
    """Context manager for trace span. No-op if telemetry disabled."""
    if not is_telemetry_enabled():
        yield
        return
    # Placeholder for OpenTelemetry span
    yield


def record_metric(name: str, value: float, tags: dict[str, str] | None = None) -> None:
    """Record metric. No-op if telemetry disabled."""
    if not is_telemetry_enabled():
        return
    # Placeholder for metrics backend
    pass
