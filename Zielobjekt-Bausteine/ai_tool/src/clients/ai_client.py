# src/clients/ai_client.py
import logging
import json
import asyncio
import time
import datetime
from typing import List, Dict, Any, Optional

from google.cloud import aiplatform
from google.api_core import exceptions as api_core_exceptions
from jsonschema import validate, ValidationError
from vertexai.generative_models import GenerativeModel, GenerationConfig, Part

from src.config import AppConfig
from src.constants import GROUND_TRUTH_MODEL

MAX_RETRIES = 5
PROMPT_CONFIG_PATH = "assets/json/prompt_config.json"


class AiClient:
    """A client for all Vertex AI model interactions, using the aiplatform SDK."""

    def __init__(self, config: AppConfig):
        self.config = config
        
        with open(PROMPT_CONFIG_PATH, 'r', encoding='utf-8') as f:
            prompt_config = json.load(f)
        
        base_system_message = prompt_config.get("system_message", "")
        if not base_system_message:
            logging.warning("System message is empty. AI calls will not have a predefined persona.")

        # Append the current date to the system prompt
        current_date = datetime.date.today().strftime("%Y-%m-%d")
        self.system_message = f"{base_system_message}\n\nImportant: Today's date is {current_date}."

        # aiplatform.init(project=config.gcp_project_id, location=config.region)
        aiplatform.init(project=config.gcp_project_id, location="global")
        
        # Default model instance
        self.generative_model = GenerativeModel(
            GROUND_TRUTH_MODEL, system_instruction=self.system_message
        )
        
        # Cache for alternative model instances
        self._model_cache = {GROUND_TRUTH_MODEL: self.generative_model}
        
        self.semaphore = asyncio.Semaphore(config.max_concurrent_ai_requests)

        logging.info(f"Vertex AI Client instantiated for project '{config.gcp_project_id}' in region '{config.region}'.")
        logging.info(f"System Message Context includes today's date: {current_date}")

    def _get_model_instance(self, model_name: str) -> GenerativeModel:
        """
        Get or create a GenerativeModel instance for the specified model.
        
        Args:
            model_name: The model name (e.g., 'gemini-2.5-pro', 'gemini-2.5-flash')
            
        Returns:
            GenerativeModel instance for the specified model
        """
        if model_name not in self._model_cache:
            logging.info(f"Creating new model instance for '{model_name}'")
            self._model_cache[model_name] = GenerativeModel(
                model_name, system_instruction=self.system_message
            )
        return self._model_cache[model_name]

    async def generate_json_response_single_attempt(
        self, 
        prompt: str, 
        json_schema: Dict[str, Any], 
        gcs_uris: List[str] = None, 
        request_context_log: str = "Generic AI Request",
        model_override: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Single attempt JSON generation - used for model fallback scenarios.
        Fails fast on JSON errors rather than retrying 5 times.
        """
        # Same logic as generate_json_response but without the retry loop
        # Just one attempt and fail immediately on JSON parsing errors
        try:
            schema_for_api = json.loads(json.dumps(json_schema))
            schema_for_api.pop("$schema", None)
        except Exception as e:
            logging.error(f"Failed to process JSON schema before API call: {e}")
            raise ValueError("Invalid JSON schema provided.") from e

        gen_config = GenerationConfig(
            response_mime_type="application/json",
            response_schema=schema_for_api,
            max_output_tokens=65535,
            temperature=0.2,
        )

        model_to_use = model_override if model_override else GROUND_TRUTH_MODEL
        generative_model = self._get_model_instance(model_to_use)

        contents = [prompt]
        if gcs_uris:
            for uri in gcs_uris:
                contents.append(Part.from_uri(uri, mime_type="application/pdf"))

        logging.info(f"[{request_context_log}] Single attempt with model '{model_to_use}'...")
        response = await generative_model.generate_content_async(
            contents=contents,
            generation_config=gen_config,
        )

        if not response.candidates:
            raise ValueError("The model response contained no candidates.")

        finish_reason = response.candidates[0].finish_reason.name
        if finish_reason not in ["STOP", "MAX_TOKENS"]:
            raise ValueError(f"Model finished with non-OK reason: '{finish_reason}'")

        try:
            response_json = json.loads(response.text)
        except json.JSONDecodeError as e:
            # Clean JSON error without the full traceback
            raise ValueError(f"Failed to parse model response as JSON: {str(e).split(':')[0]}")
        
        logging.info(f"[{request_context_log}] Successfully generated JSON response.")
        return response_json

    async def generate_json_response(
        self, 
        prompt: str, 
        json_schema: Dict[str, Any], 
        gcs_uris: List[str] = None, 
        request_context_log: str = "Generic AI Request",
        model_override: Optional[str] = None,
        max_retries: int = None
    ) -> Dict[str, Any]:
        """
        Generates a JSON response from the AI model, enforcing a specific schema and
        optionally providing GCS files as context. Implements an async retry loop
        with exponential backoff and connection limiting.

        Args:
            prompt: The text prompt for the model.
            json_schema: The JSON schema to enforce on the model's output.
            gcs_uris: A list of 'gs://...' URIs pointing to PDF files for context.
            request_context_log: A string to identify the request source in logs.
            model_override: Optional model name to use instead of the default.
            max_retries: Optional override for the number of retries (defaults to MAX_RETRIES).

        Returns:
            The parsed JSON response from the model.
        """
        retries = max_retries if max_retries is not None else MAX_RETRIES
        try:
            schema_for_api = json.loads(json.dumps(json_schema))
            schema_for_api.pop("$schema", None)
        except Exception as e:
            logging.error(f"Failed to process JSON schema before API call: {e}")
            raise ValueError("Invalid JSON schema provided.") from e

        gen_config = GenerationConfig(
            response_mime_type="application/json",
            response_schema=schema_for_api,
            max_output_tokens=65535,

            
            temperature=0.2,
        )

        # Select the appropriate model
        model_to_use = model_override if model_override else GROUND_TRUTH_MODEL
        generative_model = self._get_model_instance(model_to_use)

        # Build the content list. The system message is now handled by the model constructor.
        contents = [prompt]
        if gcs_uris:
            for uri in gcs_uris:
                contents.append(Part.from_uri(uri, mime_type="application/pdf"))
            if self.config.is_test_mode:
                logging.info(f"Attaching {len(gcs_uris)} GCS files to the prompt.")

        async with self.semaphore:
            for attempt in range(retries):
                try:
                    logging.info(f"[{request_context_log}] Attempt {attempt + 1}/{retries}: Calling Gemini model '{model_to_use}'...")
                    response = await generative_model.generate_content_async(
                        contents=contents,
                        generation_config=gen_config,
                    )

                    if not response.candidates:
                        raise ValueError("The model response contained no candidates.")

                    finish_reason = response.candidates[0].finish_reason.name
                    if finish_reason not in ["STOP", "MAX_TOKENS"]:
                        raise ValueError(f"Model finished with non-OK reason: '{finish_reason}'")

                    try:
                        response_json = json.loads(response.text)
                    except json.JSONDecodeError as e:
                        # Clean JSON error without the full traceback
                        raise ValueError(f"Failed to parse model response as JSON: {str(e).split(':')[0]}")
                    
                    logging.info(f"[{request_context_log}] Successfully generated and parsed JSON response on attempt {attempt + 1}.")
                    return response_json

                except (api_core_exceptions.GoogleAPICallError, Exception) as e:
                    wait_time = 2 ** attempt
                    if attempt == retries - 1:
                        logging.critical(f"[{request_context_log}] AI generation failed after all {retries} retries.", exc_info=True)
                        raise

                    if isinstance(e, api_core_exceptions.GoogleAPICallError):
                        logging.warning(f"[{request_context_log}] Generation attempt {attempt + 1} failed with Google API Error (Code: {e.code}): {e.message}. Retrying in {wait_time}s...")
                    else:
                        # Clean up JSON error messages to be more readable
                        error_msg = str(e)
                        if "Unterminated string" in error_msg or "json.decoder.JSONDecodeError" in error_msg:
                            logging.warning(f"[{request_context_log}] Attempt {attempt + 1} failed: JSON parsing error. Retrying in {wait_time}s...")
                        else:
                            logging.warning(f"[{request_context_log}] Attempt {attempt + 1} failed: {error_msg}. Retrying in {wait_time}s...")

                    await asyncio.sleep(wait_time)

        raise RuntimeError("AI generation failed unexpectedly after exhausting all retries.")

    async def generate_validated_json_response(
        self, 
        prompt: str, 
        json_schema: Dict[str, Any], 
        gcs_uris: List[str] = None, 
        request_context_log: str = "Generic AI Request",
        model_override: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generates and validates a JSON response from the AI model.
        
        Raises:
            ValidationError: If the response doesn't match the provided schema
            
        Returns:
            The validated JSON response from the model
        """
        try:
            result = await self.generate_json_response(prompt, json_schema, gcs_uris, request_context_log, model_override)
            validate(instance=result, schema=json_schema)
            return result
        except ValidationError as e:
            # Clean validation error message
            clean_msg = e.message.split('\n')[0] if '\n' in e.message else e.message
            logging.error(f"[{request_context_log}] Schema validation failed: {clean_msg}")
            raise ValidationError(f"Response validation failed: {clean_msg}")