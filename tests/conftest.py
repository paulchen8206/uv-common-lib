
# tests/conftest.py
import os
import json
import logging
import pytest


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    # Remove Databricks env vars unless a test sets them
    for k in [
        "DATABRICKS_JOB_ID",
        "DATABRICKS_RUN_ID",
        "DATABRICKS_TASK_KEY",
        "DATABRICKS_WORKSPACE_URL",
        "DATABRICKS_CLUSTER_ID",
        "DATABRICKS_NOTEBOOK_PATH",
    ]:
        monkeypatch.delenv(k, raising=False)
    yield


@pytest.fixture
def caplog_json(caplog):
    # Configure pytest logging capture for validation of JSON lines
    caplog.set_level(logging.INFO)
    return caplog


@pytest.fixture
def parse_json_lines():
    def _parse(records):
        parsed = []
        for r in records:
            try:
                parsed.append(json.loads(r.message))
            except json.JSONDecodeError:
                parsed.append({"_raw": r.message})
        return parsed

    return _parse
