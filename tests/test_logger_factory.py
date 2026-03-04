# Ensure src is in sys.path for imports
# tests/test_logger_factory.py
import json
import io
import logging
from uv_common_lib.logging.logger import get_logger


def test_get_logger_attaches_stdout_handler_and_context(monkeypatch):
    # Ensure no duplicate handlers on repeated calls (common in notebooks)
    log = get_logger("unit.logger")
    # Swap the first handler's stream for capture
    handler = log.logger.handlers[0]  # LoggerAdapter.logger
    assert isinstance(handler, logging.StreamHandler)

    s = io.StringIO()
    handler.stream = s

    log.info("test", extra={"extra": {"x": 1}})
    line = s.getvalue().strip()
    j = json.loads(line)
    assert j["msg"] == "test"
    assert "corr_id" in j
    # Context keys present (may be None if env not set)
    assert "dbx_job_id" in j and "dbx_run_id" in j


def test_no_duplicate_handlers_across_multiple_gets():
    a = get_logger("dup.logger")
    b = get_logger("dup.logger")
    assert id(a.logger.handlers[0]) == id(b.logger.handlers[0])