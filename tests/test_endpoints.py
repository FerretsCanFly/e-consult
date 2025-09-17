"""Pytest tests for the FastAPI endpoints."""

import pytest
from typing import Dict, Any


class TestAPIModels:
    """Test class for API data models."""
    
    def test_search_request_model(self):
        """Test SearchRequest model validation."""
        from src.models.schemas import SearchRequest
        
        # Valid request
        valid_request = SearchRequest(
            query="Test query",
            doctor_instructions="Test instructions"
        )
        assert valid_request.query == "Test query"
        assert valid_request.doctor_instructions == "Test instructions"
        
        # Test with default doctor_instructions
        request_without_instructions = SearchRequest(query="Test query")
        assert request_without_instructions.doctor_instructions == ""
    
    def test_search_result_model(self):
        """Test SearchResult model validation."""
        from src.models.schemas import SearchResult
        
        result = SearchResult(
            title="Test Title",
            url="https://example.com",
            content="Test content"
        )
        assert result.title == "Test Title"
        assert result.url == "https://example.com"
        assert result.content == "Test content"
    
    def test_search_response_model(self):
        """Test SearchResponse model validation."""
        from src.models.schemas import SearchResponse, SearchResult
        
        results = [
            SearchResult(
                title="Test Title",
                url="https://example.com",
                content="Test content"
            )
        ]
        
        response = SearchResponse(
            success=True,
            query="Test query",
            results_count=1,
            results=results,
            summary="Test summary",
            doctor_instructions="Test instructions"
        )
        
        assert response.success is True
        assert response.results_count == 1
        assert len(response.results) == 1
        assert response.summary == "Test summary"
