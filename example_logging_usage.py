# Example: Using uv-common-lib logging from installed wheel

from uv_common_lib.logging.logger import get_logger
from uv_common_lib.logging.file_sink import add_volume_file_handler

# Create a structured logger
logger = get_logger("example_app")

# Optionally, add a file handler to write logs to a directory (e.g., /tmp/logs)
add_volume_file_handler(logger, "/tmp/logs")

# Log an event with extra fields
logger.info("This is a structured log message", extra={"extra": {"user": "alice", "action": "demo"}})

print("Log message sent. Check /tmp/logs for output.")
