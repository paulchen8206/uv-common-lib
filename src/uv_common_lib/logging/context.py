

"""
Databricks runtime context extraction and correlation tracking utilities.

Captures Databricks job, cluster, and notebook context from environment variables and Spark session.
"""

import os
import uuid
from typing import Dict, Optional

from .models import DatabricksContextModel


def correlation_id() -> str:
    """
    Generate a unique correlation ID (UUID string) for tracing requests/flows.
    """
    return str(uuid.uuid4())


def databricks_context() -> Dict[str, Optional[str]]:
    """
    Extract Databricks runtime context from environment and Spark session.
    Returns a dict with job, cluster, notebook, and Spark app info if available.
    """
    # Extract context from Databricks environment variables
    # available when running in Databricks Jobs or Notebooks
    ctx = {
        "dbx_job_id": os.getenv("DATABRICKS_JOB_ID"),
        "dbx_run_id": os.getenv("DATABRICKS_RUN_ID"),
        "dbx_task_key": os.getenv("DATABRICKS_TASK_KEY"),
        "dbx_workspace_url": os.getenv("DATABRICKS_WORKSPACE_URL"),
        "dbx_cluster_id": os.getenv("DATABRICKS_CLUSTER_ID"),
        "dbx_notebook_path": os.getenv("DATABRICKS_NOTEBOOK_PATH"),
    }

    # Try to get Spark application ID if Spark session is active
    # This works in both notebook and job contexts with Spark
    try:
        from pyspark.sql import SparkSession

        spark = SparkSession.getActiveSession()
        if spark is not None and spark.sparkContext is not None:
            ctx["spark_app_id"] = spark.sparkContext.applicationId
    except Exception:
        # Spark not available or no active session - skip app ID
        pass

    context_model = DatabricksContextModel.model_validate(ctx)
    return context_model.model_dump()
