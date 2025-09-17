"""Azure OpenAI LLM integration for content relevancy and summarization (Async only)."""

import logging
import os
from openai import AsyncAzureOpenAI
from src.models.schemas import LLMSummaryOutput, ContentRelevancyOutput, SearchResult
from src.exceptions.base import LLMRelevancyError, LLMSummaryError
from src.config.prompt_manager import (
    load_all_prompts,
    get_system_prompt,
    get_user_template,
    validate_and_sanitize_input,
)
from src.config.settings_manager import get_default_system_prompts

logger = logging.getLogger("azure_llm")

# Load prompts at module level
_prompts_cache = load_all_prompts()

def _combine_system_prompts(base_prompt: str) -> str:
    """Combine base system prompt with default system prompts from settings."""
    default_prompts = get_default_system_prompts()
    
    if not default_prompts:
        return base_prompt
    
    # Combine base prompt with default prompts
    combined_prompt = f"{base_prompt}\n\n{default_prompts}"
    return combined_prompt

# =============================================================================
# ASYNCHRONOUS FUNCTIONS
# =============================================================================


async def get_async_azure_client() -> AsyncAzureOpenAI:
    """Initialiseer en geef een async Azure OpenAI client terug."""
    endpoint: str = os.getenv("AZURE_ENDPOINT")
    model_name: str = os.getenv("AZURE_MODEL_NAME")
    deployment: str = os.getenv("AZURE_DEPLOYMENT")
    subscription_key: str = os.getenv("AZURE_API_KEY")
    api_version: str = os.getenv("AZURE_API_VERSION")
    helicone_api_key: str = os.getenv("HELICONE_API_KEY")

    client = AsyncAzureOpenAI(
        api_version=api_version,
        azure_endpoint="https://oai.hconeai.com/",
        api_key=subscription_key,
        default_headers={
            "Helicone-Auth": f"Bearer {helicone_api_key}",
            "Helicone-OpenAI-Api-Base": endpoint,
            "Helicone-Model-Override": model_name,
            "api-key": subscription_key,
        },
    )

    logger.info("Async Azure OpenAI client geïnitialiseerd voor model: %s", deployment)
    return client


async def check_async_content_relevancy(
    question: str, search_results: list, doctor_instructions: str = ""
) -> list[SearchResult]:
    """Controleer welke content relevant is voor de vraag (async)."""
    if not search_results:
        logger.warning("No search results provided for relevancy check")
        return []

    try:
        client = await get_async_azure_client()

        # Get prompts from cache
        system_prompt = get_system_prompt(_prompts_cache, "relevancy_check")
        user_template = get_user_template(_prompts_cache, "relevancy_check")

        # Combine with default system prompts
        system_prompt = _combine_system_prompts(system_prompt)

        # Sanitize inputs to prevent prompt injection
        sanitized_question = validate_and_sanitize_input(question)
        sanitized_doctor_instructions = validate_and_sanitize_input(doctor_instructions)

        # Build doctor instructions placeholder
        doctor_instructions_placeholder = ""
        if sanitized_doctor_instructions:
            doctor_instructions_placeholder = (
                f"Extra instructies van de huisarts: {sanitized_doctor_instructions}"
            )

        # Format user prompt with sanitized inputs
        relevancy_prompt = user_template.format(
            question=sanitized_question,
            doctor_instructions_placeholder=doctor_instructions_placeholder,
        )

        # Add content items (also sanitize content)
        for i, result in enumerate(search_results):
            content_preview: str = result.get("content", "")
            if content_preview:
                # Sanitize content to prevent injection through search results
                sanitized_content = validate_and_sanitize_input(
                    content_preview, max_length=5000
                )
                relevancy_prompt += f"\n{i+1}. {sanitized_content}..."

        # Async API call
        response = await client.chat.completions.parse(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": relevancy_prompt},
            ],
            response_format=ContentRelevancyOutput,
            max_tokens=1000,
            temperature=0.1,
            top_p=1.0,
            model=os.getenv("AZURE_MODEL_NAME"),
        )

        return response.choices[0].message.parsed.relevant_content

    except Exception as e:
        logger.error("Fout bij async relevancy check: %s", e)
        raise LLMRelevancyError(f"Content relevancy check mislukt: {e}") from e


async def summarize_async_with_llm(
    question: str, relevant_content: list[SearchResult], doctor_instructions: str = ""
) -> LLMSummaryOutput:
    """Genereer een samenvatting van de vraag en relevante content (async)."""
    if not relevant_content:
        logger.warning("No relevant content provided for summarization")
        raise LLMSummaryError("No relevant content to summarize")

    try:
        client = await get_async_azure_client()

        # Sanitize inputs to prevent prompt injection
        sanitized_question = validate_and_sanitize_input(question)
        sanitized_doctor_instructions = validate_and_sanitize_input(doctor_instructions)

        # Build context from relevant content (sanitize content)
        context_items = []
        for i, result in enumerate(relevant_content, 1):
            sanitized_title = validate_and_sanitize_input(result.title, max_length=200)
            sanitized_content = validate_and_sanitize_input(
                result.content, max_length=3000
            )
            context_items.append(
                f"{i}. {sanitized_title}\n   URL: {result.url}\n   Inhoud: {sanitized_content}"
            )

        context = "Relevante informatie gevonden:\n\n" + "\n\n".join(context_items)

        # Get prompts from cache
        system_prompt = get_system_prompt(_prompts_cache, "summarization")
        user_template = get_user_template(_prompts_cache, "summarization")

        # Combine with default system prompts
        system_prompt = _combine_system_prompts(system_prompt)

        # Add doctor instructions to system prompt if provided (sanitized)
        if sanitized_doctor_instructions:
            system_prompt = f"{system_prompt}\n\nExtra huisarts informatie: {sanitized_doctor_instructions}"

        # Format user prompt with sanitized inputs
        user_prompt = user_template.format(question=sanitized_question, context=context)

        # Async API call
        response = await client.chat.completions.parse(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format=LLMSummaryOutput,
            max_tokens=2000,
            temperature=0.1,
            top_p=1.0,
            model=os.getenv("AZURE_MODEL_NAME"),
        )

        logger.info(
            "Async LLM samenvatting gegenereerd (%d tokens)",
            response.usage.total_tokens,
        )
        return response.choices[0].message.parsed

    except Exception as e:
        logger.error("Fout bij genereren async samenvatting: %s", e)
        raise LLMSummaryError(f"LLM samenvatting mislukt: {e}") from e


def reload_prompts() -> None:
    """Reload prompts from disk (useful for development)."""
    global _prompts_cache
    from src.config.prompt_manager import load_all_prompts

    _prompts_cache = load_all_prompts()
    logger.info("Prompts reloaded successfully")
