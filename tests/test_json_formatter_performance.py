import json
import logging
import os
import time

import pytest

from uv_common_lib.logging.json_formatter import JsonFormatter


pytestmark = pytest.mark.performance


@pytest.mark.skipif(os.getenv("RUN_PERF") != "1", reason="Set RUN_PERF=1 to run performance benchmarks")
def test_json_formatter_throughput_baseline():
    logger = logging.getLogger("t-json-perf")
    logger.handlers[:] = []
    logger.setLevel(logging.INFO)

    import io

    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(JsonFormatter(service="perf-svc"))
    logger.addHandler(handler)

    n = 5000
    start = time.perf_counter()
    for i in range(n):
        logger.info(
            "perf-message",
            extra={"extra": {"sequence": i, "kind": "benchmark"}},
        )
    elapsed = time.perf_counter() - start

    lines = [line for line in stream.getvalue().splitlines() if line.strip()]
    assert len(lines) == n

    sample = json.loads(lines[-1])
    assert sample["msg"] == "perf-message"
    assert sample["service"] == "perf-svc"

    per_log_ms = (elapsed / n) * 1000
    # Broad ceiling to catch pathological regressions while staying CI-friendly.
    assert per_log_ms < 1.5, f"Formatter is too slow: {per_log_ms:.3f} ms/log"
