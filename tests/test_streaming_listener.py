# Ensure src is in sys.path for imports
# tests/test_streaming_listener.py
import json
import io
import logging
import types
import pytest


def _capture_logger():
    logger = logging.getLogger("stream.listener.test")
    logger.handlers[:] = []
    logger.setLevel(logging.INFO)
    stream = io.StringIO()
    from uv_common_lib.logging.json_formatter import JsonFormatter

    h = logging.StreamHandler(stream)
    h.setFormatter(JsonFormatter(service="svc"))
    logger.addHandler(h)
    return logger, stream


def test_listener_emits_structured_events(monkeypatch):
    from uv_common_lib.logging.streaming_listener import JsonStreamingListener
    from uv_common_lib.logging.logger import StructuredLoggerAdapter

    logger, stream = _capture_logger()
    adapter = StructuredLoggerAdapter(logger, {"extra": {}})

    listener = JsonStreamingListener(adapter)

    # Fake events shape (dict-like for progress)
    Started = types.SimpleNamespace(id="id-1", runId="run-1", name="nm")
    listener.onQueryStarted(Started)

    progress = {
        "id": "id-1",
        "runId": "run-1",
        "name": "nm",
        "batchId": 7,
        "inputRowsPerSecond": 42.0,
        "processedRowsPerSecond": 41.0,
        "durationMs": {"triggerExecution": 1234},
    }
    Progress = types.SimpleNamespace(progress=progress)
    listener.onQueryProgress(Progress)

    Terminated = types.SimpleNamespace(id="id-1", runId="run-1", exception=None)
    listener.onQueryTerminated(Terminated)

    lines = [json.loads(l) for l in stream.getvalue().strip().splitlines()]
    kinds = [l["msg"] for l in lines]
    assert kinds == ["stream_started", "stream_progress", "stream_terminated"]
    assert lines[1]["batch_id"] == 7
    assert lines[1]["input_rows_per_sec"] == 42.0


@pytest.mark.skipif("pyspark" not in globals(), reason="PySpark not installed")
def test_listener_attach_if_spark_present():
    # Optional smoke test: ensure addListener doesn't raise if Spark present
    from pyspark.sql import SparkSession
    from uv_common_lib.logging.streaming_listener import JsonStreamingListener

    spark = SparkSession.builder.getOrCreate()
    logger, _ = _capture_logger()
    adapter = logging.LoggerAdapter(logger, {"extra": {}})
    spark.streams.addListener(JsonStreamingListener(adapter))