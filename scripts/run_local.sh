#!/bin/bash
#
# run_local.sh
#
# Executes the OSCAL generation pipeline locally for development purposes.
#
# This script sets environment variables to simulate the Cloud Run environment
# and runs the main Python application. It enables TEST mode by default to
# prevent accidental execution against production resources and to provide
# verbose logging.
#

# --- Configuration ---
# Set the script to exit immediately if any command fails.
set -e

echo "--- Starting Local Pipeline Execution ---"

# --- Environment Setup ---
# Set environment variables for local run.
# In a real scenario, you might use a .env file and `source` it here.
export GCP_PROJECT_ID="local-dev-project"
export BUCKET_NAME="local-dev-bucket"
export AI_ENDPOINT_ID="local-dev-endpoint"
export SOURCE_PREFIX="input"
export OUTPUT_PREFIX="output"
export TEST="true"
export OVERWRITE_TEMP_FILES="true"

echo "Environment Variables:"
echo "GCP_PROJECT_ID: $GCP_PROJECT_ID"
echo "BUCKET_NAME: $BUCKET_NAME"
echo "TEST: $TEST"
echo "---------------------------------------"

# --- Execution ---
# Run the main Python application.
python3 src/main.py

echo "--- Local Pipeline Execution Finished ---"
