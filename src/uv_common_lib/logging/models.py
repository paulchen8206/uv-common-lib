"""
Pydantic models for structured logging payloads.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, field_serializer


class DatabricksContextModel(BaseModel):
    """Normalized Databricks runtime context fields."""

    model_config = ConfigDict(extra="forbid")

    dbx_job_id: str | None = None
    dbx_run_id: str | None = None
    dbx_task_key: str | None = None
    dbx_workspace_url: str | None = None
    dbx_cluster_id: str | None = None
    dbx_notebook_path: str | None = None
    spark_app_id: str | None = None


class LogEventModel(BaseModel):
    """Validated structured log payload with flexible user-defined fields."""

    model_config = ConfigDict(extra="allow")

    ts: datetime
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "NOTSET"]
    logger: str
    service: str
    msg: str
    exc_type: str | None = None
    exc: str | None = None

    @field_serializer("ts")
    def _serialize_ts(self, ts: datetime) -> str:
        return ts.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")


def build_log_event_payload(*, created: float, level: str, logger: str, service: str, message: str, extras: dict[str, Any] | None, exc_type: str | None, exc: str | None) -> str:
    """Build and serialize a validated log event JSON string."""
    payload: dict[str, Any] = {
        "ts": datetime.fromtimestamp(created, tz=timezone.utc),
        "level": level,
        "logger": logger,
        "service": service,
        "msg": message,
    }

    if extras:
        payload.update(extras)

    if exc_type:
        payload["exc_type"] = exc_type
    if exc:
        payload["exc"] = exc

    event = LogEventModel.model_validate(payload)
    return event.model_dump_json()
