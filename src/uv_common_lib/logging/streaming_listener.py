
"""
PySpark structured streaming listener for JSON logging.

Listens to PySpark streaming query lifecycle events (start, progress, termination)
and logs them as structured JSON for analytics and monitoring.
"""

from pyspark.sql.streaming import StreamingQueryListener


class JsonStreamingListener(StreamingQueryListener):
    """
    Listen to PySpark streaming query events and log them as structured JSON.

    - stream_started: Fired when a query begins execution
    - stream_progress: Fired after each micro-batch completes
    - stream_terminated: Fired when a query stops (normally or due to error)

    Attributes:
        log: Logger instance (StructuredLoggerAdapter or compatible)
    """

    def __init__(self, logger):
        """Initialize the streaming listener with a logger."""
        super().__init__()
        self.log = logger

    def onQueryStarted(self, event):
        """Log when a streaming query starts (query id, run id, name)."""
        self.log.info(
            "stream_started",
            extra={
                # Unique identifier for this streaming query
                "stream_id": event.id,
                # Run identifier (tracks execution attempts)
                "run_id": event.runId,
                # User-defined query name or None
                "name": event.name,
            },
        )

    def onQueryProgress(self, event):
        """Log streaming query progress (batch id, throughput, durations, state)."""
        # Extract progress dict for easier field access
        p = event.progress
        self.log.info(
            "stream_progress",
            extra={
                # Query identifiers
                "stream_id": p["id"],
                "run_id": p["runId"],
                "name": p["name"],
                # Current micro-batch information
                "batch_id": p["batchId"],
                # Throughput metrics (rows per second)
                "input_rows_per_sec": p.get("inputRowsPerSecond"),
                "processed_rows_per_sec": p.get("processedRowsPerSecond"),
                # Timing breakdown (trigger, query, getOffset, etc.)
                "duration_ms": p.get("durationMs", {}),
                # Metrics from stateful operations (aggregations, joins)
                "state_operators": p.get("stateOperators", []),
            },
        )

    def onQueryTerminated(self, event):
        """Log when a streaming query terminates (id, run id, exception if any)."""
        self.log.warning(
            "stream_terminated",
            extra={
                # Query identifiers
                "id": event.id,
                "run_id": getattr(event, "runId", None),
                # Exception if termination was due to error
                "exception": event.exception,
            },
        )