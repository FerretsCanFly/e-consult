"""Custom exceptions package for the E-Consult Vector Search API."""

from .base import (
    BaseAPIException,
    VectorSearchError,
    EncoderError,
    DatabaseError,
    ConfigurationError,
    LLMError
)

__all__ = [
    "BaseAPIException",
    "VectorSearchError", 
    "EncoderError",
    "DatabaseError",
    "ConfigurationError",
    "LLMError"
]
