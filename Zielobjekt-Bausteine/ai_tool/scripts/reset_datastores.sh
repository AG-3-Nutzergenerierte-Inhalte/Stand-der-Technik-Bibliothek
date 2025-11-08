#!/bin/bash
#
# reset_datastores.sh
#
# Safely clears the output and temporary directories in the GCS bucket.
#
# This script is intended for development and testing. It provides a way to
# reset the data stores to a clean state by deleting the contents of the
# output and temporary data prefixes in the specified GCS bucket.
#
# Usage:
#   ./scripts/reset_datastores.sh <BUCKET_NAME> <OUTPUT_PREFIX> [TEMP_PREFIX]
#

# --- Configuration ---
set -e

# --- Variables ---
if [ "$#" -lt 2 ]; then
    echo "Usage: $0 <BUCKET_NAME> <OUTPUT_PREFIX> [TEMP_PREFIX]"
    exit 1
fi

BUCKET_NAME="$1"
OUTPUT_PREFIX="$2"
TEMP_PREFIX="${3:-temp}" # Default to 'temp' if not provided

echo "--- GCS Datastore Reset ---"
echo "WARNING: This will permanently delete data from GCS."
echo "Bucket: gs://$BUCKET_NAME"
echo "Prefixes to be cleared: '$OUTPUT_PREFIX/' and '$TEMP_PREFIX/'"
echo "---------------------------------"

# --- User Confirmation ---
read -p "Are you sure you want to continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo "Operation cancelled."
    exit 1
fi

# --- Deletion ---
echo "Deleting contents of gs://$BUCKET_NAME/$OUTPUT_PREFIX/..."
gsutil -m rm -r "gs://$BUCKET_NAME/$OUTPUT_PREFIX/**" || echo "Output directory is already empty."


echo "Deleting contents of gs://$BUCKET_NAME/$TEMP_PREFIX/..."
gsutil -m rm -r "gs://$BUCKET_NAME/$TEMP_PREFIX/**" || echo "Temp directory is already empty."


echo "--- Datastore Reset Finished ---"
