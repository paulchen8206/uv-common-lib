
"""
Structured logging for Databricks applications.

LoggerAdapter that enriches logs with Databricks context and correlation ID, and merges structured fields.
"""

import logging
import sys
from .json_formatter import JsonFormatter
from .context import databricks_context, correlation_id


class StructuredLoggerAdapter(logging.LoggerAdapter):
    """
    LoggerAdapter that merges extra fields with Databricks context and correlation ID.
    Supports both nested (extra={"extra": {...}}) and flat (extra={...}) patterns.
    """


    def info(self, msg, *args, **kwargs):
        """Log an info message with merged extra fields."""
        return self._log_merged(logging.INFO, msg, args, **kwargs)


    def debug(self, msg, *args, **kwargs):
        """Log a debug message with merged extra fields."""
        return self._log_merged(logging.DEBUG, msg, args, **kwargs)


    def warning(self, msg, *args, **kwargs):
        """Log a warning message with merged extra fields."""
        return self._log_merged(logging.WARNING, msg, args, **kwargs)


    def error(self, msg, *args, **kwargs):
        """Log an error message with merged extra fields."""
        return self._log_merged(logging.ERROR, msg, args, **kwargs)


    def critical(self, msg, *args, **kwargs):
        """Log a critical message with merged extra fields."""
        return self._log_merged(logging.CRITICAL, msg, args, **kwargs)

    def _log_merged(self, level, msg, args, **kwargs):
        """
        Merge extra dicts from arguments with adapter defaults and log.
        Handles both nested extra={"extra": {...}} and flat extra={...} patterns.
        """
        if "extra" in kwargs:
            extra = kwargs["extra"]
            # Start with default extras from adapter
            merged_extra = dict(self.extra.get("extra", {}))
            if isinstance(extra, dict) and "extra" in extra:
                # Flatten nested extra if present (pattern: extra={"extra": {...}})
                merged_extra.update(extra["extra"])
            else:
                # Use flat pattern directly (pattern: extra={...})
                merged_extra.update(extra)
            kwargs["extra"] = {"extra": merged_extra}
        else:
            # No extra provided, use defaults only
            kwargs["extra"] = self.extra

        # Delegate to underlying logger with merged extras
        self.logger._log(level, msg, args, **kwargs)


def get_logger(name: str = "dbx") -> StructuredLoggerAdapter:
    """
    Get or create a structured logger with Databricks context enrichment.
    Returns a StructuredLoggerAdapter with context and correlation ID.
    """
    # Get or create the underlying logger
    logger = logging.getLogger(name)

    # Configure handler and formatter only on first call
    # This prevents duplicate handlers when get_logger is called multiple times
    # (common in Databricks notebooks)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        # Create stdout handler (Databricks captures stdout for logging)
        h = logging.StreamHandler(sys.stdout)
        # Format logs as JSON for easy parsing and structured analysis
        h.setFormatter(JsonFormatter(service="databricks-pipeline"))
        logger.addHandler(h)

    # Always return a new adapter instance (one per call)
    # with fresh correlation ID and current Databricks context
    # This allows different correlation IDs for different request flows
    return StructuredLoggerAdapter(
        logger,
        {
            "extra": {
                # Merge Databricks context (job ID, cluster ID, etc.)
                **databricks_context(),
                # Add unique correlation ID for request tracing
                "corr_id": correlation_id(),
            }
        },
    )