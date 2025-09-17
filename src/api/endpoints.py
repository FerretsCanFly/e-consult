"""FastAPI endpoints for vector search functionality."""

import logging
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from ..models.schemas import SearchRequest, SearchResponse, LLMSummaryOutput, Settings, SettingsResponse
from ..config import load_environment_config
from ..config.database import db_manager
from ..config.settings_manager import load_settings, update_default_system_prompts, reset_settings
from ..core.vector_search import (
    perform_async_vector_search
)
from ..core.azure_llm import (
    check_async_content_relevancy,
    summarize_async_with_llm
)
from ..core.encoder_manager import encoder_manager
from ..exceptions import (
    VectorSearchError,
    EncoderError,
    DatabaseError,
    ConfigurationError
)
from .actuator import router as actuator_router
from ..config.eureka_config import get_eureka_config, init_eureka_client

logger = logging.getLogger("api")


def handle_vector_search_errors(error: Exception) -> HTTPException:
    """Handle vector search errors and return appropriate HTTP exceptions.
    
    This function centralizes error handling logic and follows python-rules:
    - Early returns for error conditions
    - Avoid deeply nested if statements
    - Consistent error response format
    """
    if isinstance(error, asyncio.TimeoutError):
        logger.error("Vector search operation timed out")
        return HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Search operation timed out"
        )
    
    if isinstance(error, asyncio.CancelledError):
        logger.info("Search operation was cancelled")
        return HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Search operation was cancelled"
        )
    
    if isinstance(error, VectorSearchError):
        logger.error("Vector search failed: %s", error)
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(error)
        )
    
    if isinstance(error, EncoderError):
        logger.error("Encoder error during search: %s", error)
        return HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(error)
        )
    
    if isinstance(error, DatabaseError):
        logger.error("Database error during search: %s", error)
        return HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(error)
        )
    
    if isinstance(error, ConfigurationError):
        logger.error("Configuration error during search: %s", error)
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(error)
        )
    
    # Fallback for unexpected errors
    logger.error("Unexpected error during vector search: %s", error)
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Internal server error during vector search"
    )


def handle_llm_operation_errors(error: Exception) -> HTTPException:
    """Handle LLM operation errors and return appropriate HTTP exceptions.
    
    This function centralizes LLM error handling logic following python-rules.
    """
    if isinstance(error, asyncio.TimeoutError):
        logger.error("LLM operations timed out")
        return HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="LLM operations timed out - please try again"
        )
    
    if isinstance(error, asyncio.CancelledError):
        logger.info("LLM operations were cancelled")
        return HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM operations were cancelled"
        )
    
    # Fallback for unexpected LLM errors
    logger.error("Unexpected error during LLM operations: %s", error)
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Internal server error during LLM operations"
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan with graceful shutdown."""
    # Startup
    logger.info("🚀 Starting E-Consult Vector Search API...")
    
    # Initialize encoder at startup
    try:
        await encoder_manager.get_encoder()
        logger.info("✅ Encoder initialized at startup")
    except Exception as e:
        logger.error("❌ Failed to initialize encoder: %s", e)
    
    # Initialize and register with Eureka server
    try:
        # Initialize Eureka in disabled mode
        init_eureka_client(port=8000, enabled=False)
        logger.info("🔧 Eureka client initialized in disabled mode")
    except Exception as e:
        logger.error("❌ Failed to register with Eureka: %s", e)
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down E-Consult Vector Search API...")
    
    # Unregister from Eureka server
    try:
        eureka_config = get_eureka_config()
        await eureka_config.unregister_from_eureka()
        logger.info("✅ Unregistered from Eureka server")
    except Exception as e:
        logger.error("❌ Failed to unregister from Eureka: %s", e)
    
    await db_manager.close_connections()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="E-Consult Vector Search API",
        description="API for medical content vector search with LLM enhancement",
        version="1.0.0",
        lifespan=lifespan
    )
    
    # Add CORS middleware for frontend integration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure this properly for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Mount static files for frontend assets
    app.mount("/static", StaticFiles(directory="frontend"), name="static")
    
    # Include actuator endpoints
    app.include_router(actuator_router)
    
    return app


# Initialize FastAPI app
app = create_app()


@app.get("/")
async def root():
    """Serve the main frontend page."""
    return FileResponse("frontend/index.html")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "vector-search-api"}


@app.get("/api/settings")
async def get_settings() -> SettingsResponse:
    """Get current application settings."""
    logger.info("Settings requested")
    try:
        settings = load_settings()
        return SettingsResponse(
            success=True,
            message="Settings retrieved successfully",
            settings=settings
        )
    except Exception as e:
        logger.error("Failed to get settings: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve settings"
        )

@app.post("/api/settings")
async def update_settings(settings: Settings) -> SettingsResponse:
    """Update application settings."""
    logger.info("Settings update requested")
    try:
        if update_default_system_prompts(settings.default_system_prompts):
            return SettingsResponse(
                success=True,
                message="Settings updated successfully",
                settings=load_settings()
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save settings"
            )
    except Exception as e:
        logger.error("Failed to update settings: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update settings"
        )

@app.delete("/api/settings")
async def reset_application_settings() -> SettingsResponse:
    """Reset application settings to defaults."""
    logger.info("Settings reset requested")
    try:
        if reset_settings():
            return SettingsResponse(
                success=True,
                message="Settings reset to defaults successfully",
                settings=load_settings()
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to reset settings"
            )
    except Exception as e:
        logger.error("Failed to reset settings: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset settings"
        )

@app.post("/api/search", response_model=SearchResponse)
async def vector_search(request: SearchRequest):
    """
    Perform async vector search with LLM enhancement for better performance.
    
    This endpoint:
    1. Performs async vector similarity search in MongoDB
    2. Filters results for relevance using async LLM
    3. Generates AI summary of relevant content using async LLM
    4. Returns structured response with results and summary
    
    Performance improvements:
    - Async MongoDB operations with connection pooling
    - Cached encoder (no reloading per request)
    - Parallel LLM calls
    - Non-blocking I/O operations
    """
    logger.info("Processing async search request: %s", request.query)
    
    # Load environment configuration
    database, collection_name, search_index = load_environment_config()
    
    # Get collection from connection pool
    try:
        client = await db_manager.get_async_client()
        collection = client[database][collection_name]
    except Exception as e:
        logger.error("Database connection failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Failed to connect to MongoDB"
        )
    
    # Perform vector search (encoder wordt automatisch gecached)
    logger.info("Executing async vector search...")
    try:
        raw_results = await asyncio.wait_for(
            perform_async_vector_search(collection, request.query, search_index),
            timeout=30.0  # 30 second timeout for search
        )
    except Exception as e:
        # Centralized error handling
        raise handle_vector_search_errors(e)
    
    if not raw_results:
        return SearchResponse.from_llm_output(
            query=request.query,
            doctor_instructions=request.doctor_instructions
        )
    
    # Check content relevancy and generate summary
    logger.info("Checking content relevancy and generating summary...")
    try:
        # Eerst relevancy check
        relevant_results = await asyncio.wait_for(
            check_async_content_relevancy(
                request.query, 
                raw_results, 
                request.doctor_instructions
            ),
            timeout=30.0
        )
        
        # Check of er relevante resultaten zijn
        if not relevant_results:
            logger.info("Geen relevante content gevonden voor query: %s", request.query)
            return SearchResponse.create_error_response(
                query=request.query,
                error_message="Geen relevante medische informatie gevonden voor je vraag. Probeer je vraag anders te formuleren of neem contact op met je huisarts.",
                doctor_instructions=request.doctor_instructions
            )
        
        # Dan summary met alleen relevante resultaten
        llm_output = await asyncio.wait_for(
            summarize_async_with_llm(
                request.query, 
                relevant_results,  # Alleen relevante resultaten voor summary
                request.doctor_instructions
            ),
            timeout=60.0
        )
    except Exception as e:
        # Centralized LLM error handling
        raise handle_llm_operation_errors(e)
    
    # Clean data flow: use LLM output directly
    return SearchResponse.from_llm_output(
        query=request.query,
        llm_output=llm_output,
        doctor_instructions=request.doctor_instructions
    )


@app.get("/api/performance")
async def get_performance_info():
    """Get performance information about the API."""
    return {
        "async_endpoint": "/api/search",
        "search_history_endpoint": "/api/search/history",
        "performance_improvements": [
            "Cached encoder (no reloading per request)",
            "Database connection pooling",
            "Async MongoDB operations",
            "Parallel LLM calls"
        ],
        "expected_performance_gain": "80-90% faster for encoder and database operations",
        "timeouts": {
            "vector_search": "30 seconds",
            "llm_operations": "60 seconds"
        }
    }


@app.get("/api/search/history")
async def get_search_history():
    """Get search history (placeholder for future implementation)."""
    return {"message": "Search history endpoint - not yet implemented"}
