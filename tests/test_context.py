
# Ensure src is in sys.path for imports
# tests/test_context.py
import os
from uv_common_lib.logging.context import databricks_context, correlation_id


def test_correlation_id_is_uuid():
    cid = correlation_id()
    import uuid

    uuid.UUID(cid)  # raises if invalid


def test_databricks_context_uses_env(monkeypatch):
    monkeypatch.setenv("DATABRICKS_JOB_ID", "123")
    monkeypatch.setenv("DATABRICKS_RUN_ID", "456")
    monkeypatch.setenv("DATABRICKS_TASK_KEY", "ingest")
    ctx = databricks_context()
    assert ctx["dbx_job_id"] == "123"
    assert ctx["dbx_run_id"] == "456"
    assert ctx["dbx_task_key"] == "ingest"


def test_databricks_context_handles_no_spark():
    # If PySpark isn't present, function should not raise
    ctx = databricks_context()
    assert "spark_app_id" not in ctx or ctx["spark_app_id"] is None
