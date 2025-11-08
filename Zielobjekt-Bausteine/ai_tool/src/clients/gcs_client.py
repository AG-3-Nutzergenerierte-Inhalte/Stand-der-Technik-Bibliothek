# src/clients/gcs_client.py
import logging
import asyncio
from google.cloud import storage
from src.config import AppConfig

class GcsClient:
    """A client for all Google Cloud Storage interactions."""

    def __init__(self, config: AppConfig):
        """
        Initializes the GCS client.

        Args:
            config: The application configuration object.
        """
        self.config = config
        self.storage_client = storage.Client(project=config.gcp_project_id)
        # We derive the bucket name from the config, which should be set by an env var
        # that comes from the terraform output.
        if not config.bucket_name:
            raise ValueError("GCS Bucket name is not configured in the environment.")
        self.bucket = self.storage_client.bucket(config.bucket_name)
        logging.info(f"GCS Client initialized for bucket: gs://{self.bucket.name}")

    def list_files(self, prefix: str = None) -> list[storage.Blob]:
        """
        Lists all files from a given GCS prefix.

        Returns:
            A list of GCS blob objects.
        """
        list_prefix = prefix if prefix is not None else self.config.source_prefix
        logging.info(f"Listing files from prefix: {list_prefix}")
        blobs = self.storage_client.list_blobs(
            self.bucket.name, prefix=list_prefix
        )
        # Filter for common document types, ignore empty "directory" blobs
        files = [blob for blob in blobs if "." in blob.name]
        logging.info(f"Found {len(files)} source files to process.")
        return files

    def download_blob_as_bytes(self, blob: storage.Blob) -> bytes:
        """Downloads a blob from GCS into memory as bytes."""
        logging.debug(f"Downloading blob: {blob.name}")
        return blob.download_as_bytes()

    async def upload_from_string_async(self, content: str, destination_blob_name: str, content_type: str = 'application/json'):
        """Asynchronously uploads a string content to a specified blob in GCS."""
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
            None, self.upload_from_string, content, destination_blob_name, content_type
        )

    def upload_from_bytes(self, content: bytes, destination_blob_name: str, content_type: str = 'application/pdf'):
        """
        Synchronously uploads bytes content to a specified blob in GCS.

        Args:
            content: The bytes content to upload.
            destination_blob_name: The full path for the object in the bucket.
            content_type: The MIME type of the content.
        """
        logging.info(f"Uploading bytes content to gs://{self.bucket.name}/{destination_blob_name}")
        blob = self.bucket.blob(destination_blob_name)
        blob.upload_from_string(content, content_type=content_type) # upload_from_string can handle bytes

    async def upload_from_bytes_async(self, content: bytes, destination_blob_name: str, content_type: str = 'application/pdf'):
        """Asynchronously uploads bytes content to a specified blob in GCS."""
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self.upload_from_bytes, content, destination_blob_name, content_type)

    def upload_from_string(self, content: str, destination_blob_name: str, content_type: str = 'application/json'):
        """
        Synchronously uploads a string content to a specified blob in GCS.

        Args:
            content: The string content to upload.
            destination_blob_name: The full path for the object in the bucket.
            content_type: The MIME type of the content.
        """
        logging.info(f"Uploading string content to gs://{self.bucket.name}/{destination_blob_name}")
        blob = self.bucket.blob(destination_blob_name)
        blob.upload_from_string(content, content_type=content_type)
        logging.info(f"Upload complete for {destination_blob_name}.")

    async def read_json_async(self, blob_name: str) -> dict:
        """Asynchronously downloads and parses a JSON file from GCS."""
        loop = asyncio.get_running_loop()
        # Use asyncio.to_thread in Python 3.9+ for a cleaner syntax
        return await loop.run_in_executor(None, self.read_json, blob_name)

    def read_json(self, blob_name: str) -> dict:
        """Downloads and parses a JSON file from GCS."""
        import json
        logging.info(f"Attempting to read JSON from: gs://{self.bucket.name}/{blob_name}")
        blob = self.bucket.blob(blob_name)
        content = blob.download_as_text() # This raises NotFound if not present.
        return json.loads(content)

    def read_text_file(self, blob_name: str) -> str:
        """Downloads and returns the content of a text-based file from GCS."""
        logging.info(f"Attempting to read text from: gs://{self.bucket.name}/{blob_name}")
        blob = self.bucket.blob(blob_name)
        return blob.download_as_text()

    def blob_exists(self, blob_name: str) -> bool:
        """Checks if a blob exists in the GCS bucket."""
        logging.debug(f"Checking for existence of blob: gs://{self.bucket.name}/{blob_name}")
        blob = self.bucket.blob(blob_name)
        return blob.exists()

    def copy_blob(self, source_blob_name: str, destination_blob_name: str):
        """Copies a blob within the same bucket."""
        source_blob = self.bucket.blob(source_blob_name)
        self.bucket.copy_blob(source_blob, self.bucket, destination_blob_name)
        logging.info(f"Copied gs://{self.bucket.name}/{source_blob_name} to gs://{self.bucket.name}/{destination_blob_name}")

    async def copy_blob_async(self, source_blob_name: str, destination_blob_name: str):
        """Asynchronously copies a blob within the same bucket."""
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
            None, self.copy_blob, source_blob_name, destination_blob_name
        )