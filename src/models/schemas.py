"""Pydantic schemas for the FastAPI endpoints."""

from typing import List, Optional
from pydantic import BaseModel, Field

class SearchRequest(BaseModel):
    """Request schema for vector search endpoint."""
    query: str = Field(..., description="The search query/question", min_length=1, max_length=500)
    doctor_instructions: Optional[str] = Field(
        default="", 
        description="Optional instructions from doctor for response format",
        max_length=1000
    )

class SearchResult(BaseModel):
    """Schema for individual search result."""
    title: str = Field(..., description="Title of the content")
    url: str = Field(..., description="URL to the content")
    content: str = Field(..., description="Content preview or excerpt")

class ContentRelevancyOutput(BaseModel):
    """Structured output schema for content relevancy check."""
    relevant_content: List[SearchResult] = Field(..., description="List of relevant content items")

class LLMSummaryOutput(BaseModel):
    """Structured output schema for LLM summarization."""
    summary: str = Field(..., description="Main medical summary in patient-friendly language")
    sources_used: List[SearchResult] = Field(..., description="List of sources used for the summary")

class SearchResponse(BaseModel):
    """Response schema for vector search endpoint."""
    success: bool = Field(..., description="Whether the search was successful")
    query: str = Field(..., description="The original search query")
    doctor_instructions: Optional[str] = Field(None, description="Applied doctor instructions")
    error_message: Optional[str] = Field(None, description="Error message if search failed")
    llm_output: LLMSummaryOutput = Field(..., description="Structured LLM output with summary and sources")
    
    @classmethod
    def from_llm_output(cls, query: str, llm_output: LLMSummaryOutput, doctor_instructions: str = "") -> "SearchResponse":
        """Create SearchResponse from LLMSummaryOutput."""
        return cls(
            success=True,
            query=query,
            doctor_instructions=doctor_instructions,
            error_message=None,
            llm_output=llm_output
        )
    
    @classmethod
    def create_error_response(cls, query: str, error_message: str, doctor_instructions: str = "") -> "SearchResponse":
        """Create error response with empty LLM output."""
        return cls(
            success=False,
            query=query,
            doctor_instructions=doctor_instructions,
            error_message=error_message,
            llm_output=LLMSummaryOutput(
                summary="Er is een fout opgetreden bij het verwerken van je vraag.",
                sources_used=[]
            )
        )

class Settings(BaseModel):
    """Schema for application settings."""
    default_system_prompts: str = Field(
        default="",
        description="Default system prompts that are always included",
        max_length=2000
    )
    last_updated: Optional[str] = Field(None, description="Timestamp of last update")

class SettingsResponse(BaseModel):
    """Response schema for settings operations."""
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Response message")
    settings: Optional[Settings] = Field(None, description="Current settings if applicable")

