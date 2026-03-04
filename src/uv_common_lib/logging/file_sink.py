

"""
File sink handler for writing JSON logs to Databricks Volumes.

Adds file-based logging to structured logger instances, writing JSON log lines to timestamped files.
"""

import logging
import datetime
import os
from .json_formatter import JsonFormatter


def add_volume_file_handler(base_logger: logging.Logger, volume_dir: str) -> None:
    """
    Add a file handler to write JSON logs to a Databricks Volume.
    Creates a timestamped JSON Lines file in the given directory and attaches it to the logger.

    Example:
        from databricks_custom_logging import get_logger
        from databricks_custom_logging.file_sink import add_volume_file_handler
        logger = get_logger("myapp")
        add_volume_file_handler(logger, "/Volumes/main/default/logs")
        logger.info("event", extra={"extra": {"status": "complete"}})
        # JSON log line written to /Volumes/main/default/logs/log_*.jsonl
    """
    # Create the directory if it doesn't exist
    # Use exist_ok=True to avoid errors if directory already exists
    os.makedirs(volume_dir, exist_ok=True)

    # Generate timestamp in UTC for consistent file naming across timezones
    ts = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%S")

    # Construct full file path
    file_path = os.path.join(volume_dir, f"log_{ts}.jsonl")

    # Create file handler that writes to the specified path
    # UTF-8 encoding to support international characters and Unicode
    fh = logging.FileHandler(file_path, encoding="utf-8")

    # Use JSON formatter to output structured logs
    fh.setFormatter(JsonFormatter())

    # Add handler to the underlying logger
    # Note: base_logger is a LoggerAdapter, so we access .logger to get the Logger
    base_logger.logger.addHandler(fh)
