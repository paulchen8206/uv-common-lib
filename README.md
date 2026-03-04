# uv-common-lib

A modern Python package providing common utilities. Package name: `uv-common-lib`.

---

## Table of Contents

1. [Features](#features)
2. [Quick Start](#quick-start)
3. [Example Usage](#example-usage)
4. [Testing](#testing)
5. [Development, Build, and Distribution](#development-build-and-distribution)
6. [Project Structure](#project-structure)
7. [Notes & Troubleshooting](#notes-&-troubleshooting)

---

## Features

- Structured logging for Databricks and PySpark
- JSON log formatting and file sink utilities
- Context and correlation ID helpers

---


## End-to-End Quick Start

### 1. Install Python (Recommended: 3.13)

This project supports Python 3.13 (or 3.12 if available). Install with Homebrew:

```sh
brew install python@3.11
```

### 2. Create and Activate a Virtual Environment


```sh
/opt/homebrew/bin/python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt  # Install all required dependencies
```

On Windows:
```sh
.venv\Scripts\activate
```

### 3. Install the Package (from Source or Wheel)

If developing locally:
```sh
pip install -e ./
```

Or, after building a wheel (see below):
```sh
pip install dist/uv_common_lib-<version>-py3-none-any.whl
```


### 5. Run Example Usage

```sh
python example_logging_usage.py
```

### 6. Run Tests

```sh
pip install pytest
PYTHONPATH=src pytest
```

### 7. Build the Package

```sh
pip install build
python -m build
```

### 8. Distribute or Upload

To upload to PyPI:
```sh
pip install twine
twine upload dist/*
```

To upload to S3:
```sh
aws s3 cp dist/ s3://<your-bucket>/uv-common-lib/ --recursive
```

---

## Example Usage

Import and use in your Python code:

```python
from uv_common_lib import hello
print(hello())
```

### Logging Utilities Example

The `uv_common_lib.logging` submodule provides structured logging utilities for Databricks and PySpark environments:

- **StructuredLoggerAdapter**: Logger that enriches logs with Databricks context and correlation IDs.
- **JsonFormatter**: Formats logs as JSON for ingestion and analysis.
- **add_volume_file_handler**: Write logs to Databricks Volumes as JSON lines.
- **JsonStreamingListener**: PySpark StreamingQueryListener for logging streaming events as JSON.
- **correlation_id, databricks_context**: Utilities for context and traceability.

```python
from uv_common_lib.logging.logger import get_logger
from uv_common_lib.logging.file_sink import add_volume_file_handler
from uv_common_lib.logging.context import correlation_id, databricks_context

logger = get_logger("my_app")
add_volume_file_handler(logger, "/tmp/logs")
logger.info("Event happened", extra={"correlation_id": correlation_id()})
```

---

## Testing

This project uses `pytest` for testing. To run all tests (ensure the src directory is on PYTHONPATH):

```sh
uv pip install --upgrade pytest
# or
pip install --upgrade pytest
pip install pyspark  # Required for streaming_listener tests
PYTHONPATH=src pytest
```

Tests are located in the `tests/` directory and cover core logging, formatting, and context utilities.

---

## Development, Build, and Distribution

### Development

- Edit or add modules in `src/uv_common_lib/` as needed.
- Update `pyproject.toml` for dependencies, version, and metadata.
- Optionally, add or update tests and documentation.
**Versioning:** This project uses [bump2version](https://github.com/c4urself/bump2version) to manage the version in `pyproject.toml`.

#### Bump2version Steps

1. Make sure bump2version is installed:
  ```sh
  pip install bump2version
  ```
2. To bump the version, run one of:
  ```sh
  bump2version patch   # for bugfix releases (e.g., 0.1.1 → 0.1.2)
  bump2version minor   # for feature releases (e.g., 0.1.1 → 0.2.0)
  bump2version major   # for breaking changes (e.g., 0.1.1 → 1.0.0)
  ```
3. bump2version will:
  - Update the version in `pyproject.toml` and other configured files
  - Commit the change
  - Create a git tag for the new version
4. Push the commit and tag to your remote repository:
  ```sh
  git push && git push --tags
  ```

### Build a Wheel (.whl) File

Install build tools (if not already installed):

```sh
uv pip install --upgrade build
# or
pip install --upgrade build
```

Build the package:

```sh
python -m build
```

Find `.whl` and `.tar.gz` in the `dist/` directory.

### Distribute the Package

To upload to PyPI (requires an account and API token):

```sh
uv pip install --upgrade twine
# or
pip install --upgrade twine
twine upload dist/*
```

For private/internal distribution, share the `.whl` file directly or host it on a private PyPI server.

### Use the Library (Install the Wheel)

Install the built wheel in another project or environment:

```sh
pip install dist/uv_common_lib-<version>-py3-none-any.whl
```

Replace `<version>` with the version from `pyproject.toml`.

### Publish Artifacts to S3

To upload the built wheel or tar.gz to an S3 bucket (requires AWS CLI):

```sh
# Example: upload all artifacts in dist/ to S3
aws s3 cp dist/ s3://<your-bucket>/uv-common-lib/ --recursive
```

Replace `<your-bucket>` with your S3 bucket name. Artifacts can then be installed directly using pip:

```sh
pip install "s3://<your-bucket>/uv-common-lib/uv_common_lib-<version>-py3-none-any.whl"
```

---

## Project Structure

- Source code: `src/uv_common_lib/`
- Example function: `hello()` in `src/uv_common_lib/__init__.py`
- Logging utilities: `src/uv_common_lib/logging/`
  - `logger.py`: StructuredLoggerAdapter
  - `file_sink.py`: add_volume_file_handler
  - `json_formatter.py`: JsonFormatter
  - `context.py`: correlation_id, databricks_context
  - `streaming_listener.py`: JsonStreamingListener
- Config: `pyproject.toml`

---

## Notes & Troubleshooting

- If you see `python3.12 not found`, use Python 3.13 as shown above.
- Always activate your venv before installing or running anything.
- For Databricks or PySpark, ensure your cluster/environment matches your local Python version.
- For issues with dependencies, check `pyproject.toml` and `requirements.txt`.

---

## Logging Design Pattern

The logging system in `uv-common-lib` is based on the Adapter and Enrichment design patterns for structured, context-rich logging. Key principles:

- **Adapter Pattern:**
  - `StructuredLoggerAdapter` extends Python's `LoggerAdapter` to merge contextual information (Databricks job, cluster, notebook, correlation ID) into every log record.
  - Supports both flat and nested `extra` dicts for flexible structured logging.

- **Context Enrichment:**
  - Each logger instance automatically injects Databricks context and a unique correlation ID for traceability.
  - Context is refreshed per logger instance, supporting multi-request and distributed tracing.

- **Singleton Handler Initialization:**
  - The underlying logger is configured with a JSON formatter and stream handler only once, preventing duplicate logs in notebook environments.

- **Usage Pattern:**
  - Always use `get_logger(name)` to obtain a logger. This ensures context and handler setup is correct.
  - Log with structured fields using the `extra` argument:
    ```python
    logger = get_logger("my_app")
    logger.info("event", extra={"user": "alice", "action": "demo"})
    ```

- **Extensibility:**
  - Additional context or handlers can be added by extending the adapter or configuring the logger as needed.

**Benefits:**
- Consistent, structured, and context-rich logs for analytics and debugging
- Easy integration with Databricks, PySpark, and distributed systems
- Flexible for both local and cloud environments

---

## Release Notes


### v0.1.1 (Unreleased)
- Added bump2version configuration for automated version management.
- Added pyspark as a required dependency for streaming_listener tests.

### v0.1.0 (2026-03-04)
- Initial release of `uv-common-lib`.
- Structured logging utilities for Databricks and PySpark.
- JSON log formatting and file sink utilities.
- Context and correlation ID helpers.
- Example usage and tests included.

---

## Disclaimer & Announcement

**This library is provided as-is, without warranty of any kind. The authors and contributors are not responsible for any issues, damages, or losses resulting from the use of this code in production environments. Use at your own risk.**
