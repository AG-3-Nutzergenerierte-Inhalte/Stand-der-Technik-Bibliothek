"""
Manages the import of environment variables for the application.

This module retrieves configuration settings from the environment, providing
a single source of truth for all configurable parameters. It includes type
casting and default values to ensure robustness.
"""

import os
from typing import Optional

# --- GCP Configuration ---
GCP_PROJECT_ID: Optional[str] = os.environ.get("GCP_PROJECT_ID")
BUCKET_NAME: Optional[str] = os.environ.get("BUCKET_NAME")
AI_ENDPOINT_ID: Optional[str] = os.environ.get("AI_ENDPOINT_ID")

# --- GCS Data Configuration ---
SOURCE_PREFIX: Optional[str] = os.environ.get("SOURCE_PREFIX")
OUTPUT_PREFIX: Optional[str] = os.environ.get("OUTPUT_PREFIX")

# --- Operational Flags ---
# Note: Environment variables are strings. Convert to boolean.
TEST_MODE_str = os.environ.get("TEST", "false").lower()
TEST: bool = TEST_MODE_str == "true"

OVERWRITE_TEMP_FILES_str = os.environ.get("OVERWRITE_TEMP_FILES", "false").lower()
OVERWRITE_TEMP_FILES: bool = OVERWRITE_TEMP_FILES_str == "true"

# --- Validation ---
# A simple validation check to ensure critical variables are set in a non-test environment.
if not TEST:
    required_vars = {
        "GCP_PROJECT_ID": GCP_PROJECT_ID,
        "BUCKET_NAME": BUCKET_NAME,
        "AI_ENDPOINT_ID": AI_ENDPOINT_ID,
        "SOURCE_PREFIX": SOURCE_PREFIX,
        "OUTPUT_PREFIX": OUTPUT_PREFIX,
    }
    missing_vars = [key for key, value in required_vars.items() if value is None]
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
