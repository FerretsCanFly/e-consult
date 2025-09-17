"""Tests for header validation functionality."""

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from src.api.endpoints import app
from src.api.header_validation import (
    validate_required_headers, 
    HeaderValidationContext,
    PP_IDENTITY_HEADER_NAME,
    PP_CLUSTER_HEADER_NAME
)


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


class TestHeaderValidation:
    """Test header validation functionality."""
    
    def test_validate_headers_with_required_header(self, client):
        """Test that validation passes with required header."""
        headers = {PP_IDENTITY_HEADER_NAME: "test-user"}
        
        # Test with a simple API endpoint that doesn't require database
        response = client.get("/actuator/health", headers=headers)
        assert response.status_code == 200
    
    def test_validate_headers_with_all_headers(self, client):
        """Test that validation passes with all headers."""
        headers = {
            PP_IDENTITY_HEADER_NAME: "test-user",
            PP_CLUSTER_HEADER_NAME: "test-cluster"
        }
        
        response = client.get("/actuator/health", headers=headers)
        assert response.status_code == 200
    
    def test_validate_headers_missing_identity_header(self, client):
        """Test that validation fails when identity header is missing."""
        # Test an endpoint that requires header validation
        response = client.get("/api/settings")
        assert response.status_code == 401
        assert "user identity should be present" in response.json()["detail"]
    
    def test_validate_headers_empty_identity_header(self, client):
        """Test that validation fails when identity header is empty."""
        headers = {PP_IDENTITY_HEADER_NAME: ""}
        
        response = client.get("/api/settings", headers=headers)
        assert response.status_code == 401
    
    def test_api_search_with_valid_headers(self, client):
        """Test that API search endpoint works with valid headers."""
        headers = {
            PP_IDENTITY_HEADER_NAME: "test-user",
            PP_CLUSTER_HEADER_NAME: "test-cluster"
        }
        
        search_data = {
            "query": "test query",
            "doctor_instructions": "test instructions"
        }
        
        # This will fail due to missing database config, but should pass header validation
        response = client.post("/api/search", json=search_data, headers=headers)
        # Should not be 401 (header validation error)
        assert response.status_code != 401
    
    def test_api_search_without_headers(self, client):
        """Test that API search endpoint fails without headers."""
        search_data = {
            "query": "test query",
            "doctor_instructions": "test instructions"
        }
        
        response = client.post("/api/search", json=search_data)
        assert response.status_code == 401
        assert "user identity should be present" in response.json()["detail"]
    
    def test_actuator_endpoints_no_validation(self, client):
        """Test that actuator endpoints work without header validation."""
        # Health endpoint should work without headers
        response = client.get("/actuator/health")
        assert response.status_code == 200
        assert response.json() == {"status": "UP"}
        
        # Info endpoint should work without headers  
        response = client.get("/actuator/info")
        assert response.status_code == 200
        assert response.json() == {"app": {"name": "python-ai-service", "version": "1.0.0"}}


class TestHeaderValidationContext:
    """Test HeaderValidationContext class."""
    
    def test_context_creation_with_all_data(self):
        """Test creating context with all data."""
        context = HeaderValidationContext("user123", "cluster456")
        assert context.user_identity == "user123"
        assert context.cluster_id == "cluster456"
    
    def test_context_creation_without_cluster(self):
        """Test creating context without cluster."""
        context = HeaderValidationContext("user123")
        assert context.user_identity == "user123"
        assert context.cluster_id is None
    
    def test_context_string_representation(self):
        """Test string representation of context."""
        context = HeaderValidationContext("user123", "cluster456")
        str_repr = str(context)
        assert "user123" in str_repr
        assert "cluster456" in str_repr
