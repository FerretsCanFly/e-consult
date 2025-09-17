"""Base exception classes for the E-Consult Vector Search API."""


class BaseAPIException(Exception):
    """Base exception for all API-related errors."""
    
    def __init__(self, message: str, details: str = None):
        self.message = message
        self.details = details
        super().__init__(self.message)
    
    def __str__(self) -> str:
        if self.details:
            return f"{self.message}: {self.details}"
        return self.message


class VectorSearchError(BaseAPIException):
    """Base exception for vector search operations."""
    pass


class EncoderError(VectorSearchError):
    """Exception raised when encoder operations fail."""
    pass


class DatabaseError(VectorSearchError):
    """Exception raised when database operations fail."""
    pass


class ConfigurationError(VectorSearchError):
    """Exception raised when configuration is invalid."""
    pass


class LLMError(BaseAPIException):
    """Exception raised when LLM operations fail."""
    pass


class LLMRelevancyError(LLMError):
    """Exception raised when LLM relevancy check operations fail."""
    pass


class LLMSummaryError(LLMError):
    """Exception raised when LLM summary operations fail."""
    pass


class HeaderValidationError(BaseAPIException):
    """Exception raised when required headers are missing or invalid."""
    pass