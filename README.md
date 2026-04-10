# uv-common-lib

Common structured logging utilities for Databricks and PySpark workloads.

## Features

- Structured log adapters with contextual enrichment
- JSON formatting for log aggregation pipelines
- Pydantic-backed payload validation and serialization
- Strict log-level validation (`DEBUG|INFO|WARNING|ERROR|CRITICAL|NOTSET`)
- File sink helpers for JSONL output
- Streaming listener utilities for Spark workloads

## Requirements

- `uv` 0.8+
- Python 3.11+

## Quick Start

Sync the project with the development dependencies:

```sh
uv sync --group dev
```

Run the example script:

```sh
uv run python example_logging_usage.py
```

Run the test suite:

```sh
uv run pytest
```

Run optional formatter performance benchmarks:

```sh
RUN_PERF=1 uv run pytest -m performance
```

By default, performance tests are skipped in normal `uv run pytest` runs.

If you want to run the optional PySpark test path locally, install the extra group first:

```sh
uv sync --group dev --group spark
uv run pytest
```

## Example

```python
from uv_common_lib.logging.file_sink import add_volume_file_handler
from uv_common_lib.logging.logger import get_logger

logger = get_logger("example_app")
add_volume_file_handler(logger, "/tmp/logs")
logger.info(
    "This is a structured log message",
    extra={"extra": {"user": "alice", "action": "demo"}},
)
```

## Development Workflow

Install or refresh the local environment:

```sh
uv sync --group dev
```

Bump the package version:

```sh
uv version --bump patch
```

Build source and wheel distributions:

```sh
uv build
```

Upload to PyPI without adding project-specific release tooling to the environment:

```sh
uv tool run --from twine twine upload dist/*
```

Upload build artifacts to S3:

```sh
uv tool run --from awscli aws s3 cp dist/ s3://<your-bucket>/uv-common-lib/ --recursive
```

## Project Layout

- `src/uv_common_lib/`: package source
- `src/uv_common_lib/logging/`: logging helpers and adapters
- `tests/`: test suite
- `example_logging_usage.py`: runnable example
- `pyproject.toml`: package metadata and `uv` configuration

## Notes

- The default development setup only installs the core test dependencies.
- The `spark` dependency group is optional because the Spark-specific test is already guarded when PySpark is unavailable.
- `uv run` uses the project environment directly, so no manual virtual environment activation or `PYTHONPATH` setup is required.

## Pydantic Validation

- Log events are validated through Pydantic models before serialization.
- Standard log levels are enforced and invalid levels are rejected.
- Databricks context fields are normalized through a typed context model.
