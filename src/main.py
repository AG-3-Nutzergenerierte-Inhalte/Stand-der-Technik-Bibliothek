"""
Main entry point for the OSCAL generation pipeline.

This script initializes the application's configuration and logging, then
starts the main processing pipeline. It is designed to be executed as the
entry point for the GCP Cloud Run job.
"""

import logging

from src.pipeline import processing
from src.utils.logger import setup_logging


def main() -> None:
    """
    Orchestrates the OSCAL generation pipeline.

    This function executes the main steps of the pipeline:
    1. Initializes logging.
    2. (TODO) Loads the curated crosswalk and source data.
    3. (TODO) Processes the data to generate OSCAL component definitions.
    4. (TODO) Serializes and saves the resulting artifacts.
    """
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("Starting OSCAL generation pipeline...")

    # --- Placeholder for pipeline execution ---
    # In the future, this will call the main processing function.
    processing.run_pipeline()

    logger.info("OSCAL generation pipeline finished successfully.")


if __name__ == "__main__":
    main()
