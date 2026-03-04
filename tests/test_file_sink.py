# Ensure src is in sys.path for imports
# tests/test_file_sink.py
import json
import logging
from pathlib import Path
from uv_common_lib.logging.logger import get_logger
from uv_common_lib.logging.file_sink import add_volume_file_handler


def test_file_sink_writes_jsonl(tmp_path):
    base = get_logger("file.sink")
    add_volume_file_handler(base, str(tmp_path))
    base.info("file_line", extra={"extra": {"k": "v"}})

    files = list(tmp_path.glob("log_*.jsonl"))
    assert files, "Expected a rotated file to be created"
    content = files[0].read_text(encoding="utf-8").strip()
    j = json.loads(content)
    assert j["msg"] == "file_line"
    assert j["k"] == "v"