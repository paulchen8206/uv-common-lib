
# Ensure src is in sys.path for imports
# tests/test_json_formatter.py
import json
import logging
import uuid
import pytest
from pydantic import ValidationError
from uv_common_lib.logging.json_formatter import JsonFormatter
from uv_common_lib.logging.models import build_log_event_payload


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


def test_json_formatter_serializes_uuid_with_pydantic():
    logger = logging.getLogger("t-json-uuid")
    logger.handlers[:] = []
    logger.setLevel(logging.INFO)

    import io

    s = io.StringIO()
    h = logging.StreamHandler(s)
    h.setFormatter(JsonFormatter(service="svc"))
    logger.addHandler(h)

    uid = uuid.uuid4()
    logger.info("with-uuid", extra={"extra": {"event_id": uid}})

    j = json.loads(s.getvalue().strip())
    assert j["msg"] == "with-uuid"
    assert j["event_id"] == str(uid)


def test_build_log_event_payload_rejects_invalid_level():
    with pytest.raises(ValidationError):
        build_log_event_payload(
            created=0.0,
            level="TRACE",
            logger="t-json-invalid-level",
            service="svc",
            message="bad-level",
            extras=None,
            exc_type=None,
            exc=None,
        )


def test_build_log_event_payload_accepts_standard_level():
    out = build_log_event_payload(
        created=0.0,
        level="INFO",
        logger="t-json-valid-level",
        service="svc",
        message="ok-level",
        extras=None,
        exc_type=None,
        exc=None,
    )
    j = json.loads(out)
    assert j["level"] == "INFO"
