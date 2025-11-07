"""
Defines application-wide constants.

This module centralizes all static, non-configurable values used across the
application. This improves maintainability by providing a single, authoritative
source for these constants.
"""

# --- File Paths ---
# Defines the location for storing prompts and schemas, relative to the project root.
ASSETS_DIR = "assets"
JSON_DIR = "json"
PROMPT_CONFIG_FILENAME = "prompt_config.json"

# --- API Configuration ---
# Constants for external API interactions, such as retry logic parameters.
API_MAX_RETRIES = 5
API_RETRY_BACKOFF_FACTOR = 2
API_RETRY_JITTER = 0.5  # 50% jitter

# --- Logging ---
LOG_LEVEL_TEST = "INFO"
LOG_LEVEL_PRODUCTION = "INFO"
THIRD_PARTY_LOG_LEVEL_PRODUCTION = "WARNING"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# --- OSCAL Metadata ---
# Default values and namespaces for OSCAL artifact generation.
OSCAL_VERSION = "1.1.3"
OSCAL_NAMESPACE = "http://csrc.nist.gov/ns/oscal/1.0"
