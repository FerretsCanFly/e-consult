"""Pytest configuration and shared fixtures."""

import pytest
import sys
import os

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))


# Configure pytest-asyncio
pytest_plugins = ["pytest_asyncio"]


@pytest.fixture
def api_base_url():
    """Base URL for the API."""
    return "http://localhost:8000"


@pytest.fixture
def sample_search_request():
    """Sample search request data."""
    return {
        "query": "Wat kan ik doen tegen langdurige hoest?",
        "doctor_instructions": "Ik wil het antwoord in 1 zin."
    }


@pytest.fixture
def sample_search_response():
    """Sample search response data."""
    return {
        "success": True,
        "query": "Wat kan ik doen tegen langdurige hoest?",
        "results_count": 1,
        "results": [
            {
                "title": "Hoest - Thuisarts.nl",
                "url": "https://www.thuisarts.nl/hoest",
                "content": "Hoest is een natuurlijke reactie van het lichaam...",
                "score": 0.95
            }
        ],
        "summary": "Voor langdurige hoest kunt u het beste...",
        "doctor_instructions": "Ik wil het antwoord in 1 zin.",
        "error_message": None
    }


@pytest.fixture
async def async_app():
    """Async FastAPI app fixture for testing."""
    from src.api.endpoints import app
    return app
