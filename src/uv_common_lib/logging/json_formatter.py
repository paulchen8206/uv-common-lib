"""
JSON log formatting for structured logging output.

Formatter that converts LogRecords to JSON with support for structured field enrichment and exception formatting.
"""
import traceback
from logging import Formatter, LogRecord

from .models import build_log_event_payload


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
        extras = None

        # Merge any structured extras from LoggerAdapter
        # These are key-value fields attached to the LogRecord
        if hasattr(record, "extra") and isinstance(record.extra, dict):
            extras = dict(record.extra)

        # Flatten nested extra dict if present
        # This handles the pattern: extra={"extra": {"field": "value"}}
        # Converting it to: {"field": "value"} at top level
        if isinstance(extras, dict) and "extra" in extras and isinstance(extras["extra"], dict):
            flattened = dict(extras)
            flattened.update(flattened.pop("extra"))
            extras = flattened

        exc_type = None
        exc = None

        # Add exception information if this is an exception record
        if record.exc_info:
            exc_type = str(record.exc_info[0].__name__)
            exc = "".join(traceback.format_exception(*record.exc_info))

        return build_log_event_payload(
            created=record.created,
            level=record.levelname,
            logger=record.name,
            service=self.service,
            message=record.getMessage(),
            extras=extras,
            exc_type=exc_type,
            exc=exc,
        )