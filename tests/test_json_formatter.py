
# Ensure src is in sys.path for imports
# tests/test_json_formatter.py
import json
import logging
from uv_common_lib.logging.json_formatter import JsonFormatter


def test_json_formatter_emits_valid_json():
    logger = logging.getLogger("t-json")
    logger.handlers[:] = []
    logger.setLevel(logging.INFO)

    h = logging.StreamHandler()
    h.setFormatter(JsonFormatter(service="svc"))
    logger.addHandler(h)

    # Capture via memory stream
    import io

    stream = io.StringIO()
    h.stream = stream

    logger.info("hello world", extra={"extra": {"k": "v"}})
    out = stream.getvalue().strip()
    as_json = json.loads(out)

    assert as_json["msg"] == "hello world"
    assert as_json["service"] == "svc"
    assert as_json["k"] == "v"
    assert "ts" in as_json and "level" in as_json and "logger" in as_json


def test_json_formatter_includes_exception_trace():
    logger = logging.getLogger("t-json-ex")
    logger.handlers[:] = []
    logger.setLevel(logging.INFO)
    import io

    s = io.StringIO()
    h = logging.StreamHandler(s)
    h.setFormatter(JsonFormatter())
    logger.addHandler(h)

    try:
        1 / 0
    except Exception:
        logger.exception("boom")

    j = json.loads(s.getvalue().strip())
    assert j["msg"] == "boom"
    assert j["level"] == "ERROR"
    assert "exc" in j and "ZeroDivisionError" in j["exc_type"]
