# databricks_custom_logging/json_formatter.py

"""
JSON log formatting for structured logging output.

Formatter that converts LogRecords to JSON with support for structured field enrichment and exception formatting.
"""
import json
import time
import traceback
from logging import Formatter, LogRecord


class JsonFormatter(Formatter):
    """
    Formats log records as JSON with structured field support.
    Adds ISO timestamp, log level, logger name, service, message, and any extra fields.
    Flattens nested 'extra' dicts and formats exception info if present.
    """

    def __init__(self, service: str = "databricks-pipeline"):
        """Initialize the JSON formatter with a service name."""
        super().__init__()
        self.service = service

    def format(self, record: LogRecord) -> str:
        """Format a LogRecord as a JSON string with all structured fields."""
        # Build base JSON object with standard fields
        base = {
            # ISO format timestamp
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(record.created)),
            "level": record.levelname,
            "logger": record.name,
            "service": self.service,
            "msg": record.getMessage(),
        }

        # Merge any structured extras from LoggerAdapter
        # These are key-value fields attached to the LogRecord
        if hasattr(record, "extra") and isinstance(record.extra, dict):
            base.update(record.extra)

        # Flatten nested extra dict if present
        # This handles the pattern: extra={"extra": {"field": "value"}}
        # Converting it to: {"field": "value"} at top level
        if "extra" in base and isinstance(base["extra"], dict):
            base.update(base.pop("extra"))

        # Add exception information if this is an exception record
        if record.exc_info:
            base["exc_type"] = str(record.exc_info[0].__name__)
            # Include full traceback as formatted string
            base["exc"] = "".join(traceback.format_exception(*record.exc_info))

        # Convert to JSON and return
        return json.dumps(base, ensure_ascii=False)