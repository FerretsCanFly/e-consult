"""Environment configuration module for centralized environment variable management."""

import os
import logging

logger = logging.getLogger("config")


def load_environment_config() -> tuple[str, str, str]:
    """Laad configuratie uit environment variables."""
    database: str = os.getenv("MONGODB_DATABASE")
    collection_name: str = os.getenv("MONGODB_COLLECTION")
    search_index: str = os.getenv("MONGODB_SEARCH_INDEX")
    
    # Check of variabelen leeg zijn
    empty_vars = [name for name, value in [
        ("MONGODB_DATABASE", database),
        ("MONGODB_COLLECTION", collection_name),
        ("MONGODB_SEARCH_INDEX", search_index)
    ] if not value]
    
    if empty_vars:
        logger.warning(
            "De volgende variabelen zijn leeg in .env: %s. Huidige waarden: %s/%s (index: %s)",
            ", ".join(empty_vars),
            database,
            collection_name,
            search_index,
        )
    
    return database, collection_name, search_index


def get_azure_config() -> dict[str, str]:
    """Get Azure OpenAI configuration from environment variables."""
    config = {
        "endpoint": os.getenv("AZURE_ENDPOINT"),
        "model_name": os.getenv("AZURE_MODEL_NAME"),
        "deployment": os.getenv("AZURE_DEPLOYMENT"),
        "api_key": os.getenv("AZURE_API_KEY"),
        "api_version": os.getenv("AZURE_API_VERSION")
    }
    
    # Check for missing required variables
    missing_vars = [key for key, value in config.items() if not value]
    if missing_vars:
        logger.warning("Missing Azure configuration variables: %s", ", ".join(missing_vars))
    
    return config


def get_vector_search_config() -> dict[str, int]:
    """Get vector search configuration from environment variables."""
    config = {
        "num_candidates": int(os.getenv("VECTOR_SEARCH_NUM_CANDIDATES", "150")),
        "limit": int(os.getenv("VECTOR_SEARCH_LIMIT", "10"))
    }
    
    logger.info("Vector search config: %d candidates, %d limit", config["num_candidates"], config["limit"])
    return config


def validate_environment() -> bool:
    """Validate that all required environment variables are set."""
    required_vars = [
        "MONGODB_URI",
        "MONGODB_DATABASE", 
        "MONGODB_COLLECTION",
        "MONGODB_SEARCH_INDEX",
        "AZURE_ENDPOINT",
        "AZURE_MODEL_NAME",
        "AZURE_DEPLOYMENT",
        "AZURE_API_KEY",
        "AZURE_API_VERSION"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error("Missing required environment variables: %s", ", ".join(missing_vars))
        return False
    
    logger.info("✅ All required environment variables are set")
    return True
