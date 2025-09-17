#!/usr/bin/env python3
"""Script to run the FastAPI server."""

import uvicorn
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("server")

if __name__ == "__main__":
    # Application port
    PORT = 8000
    
    logger.info("🚀 Starting E-Consult Vector Search API Server...")
    logger.info(f"📡 Eureka registration will happen during FastAPI startup")
    
    # Run the FastAPI server
    uvicorn.run(
        "src.api.endpoints:app",
        host="0.0.0.0",
        port=PORT,
        reload=True,  # Enable auto-reload during development
        log_level="info",
        reload_dirs=["src"],  # Only watch src directory
        reload_excludes=["*.pyc", "__pycache__", "tests"],  # Exclude test files from reload
        access_log=True,
        use_colors=True
    )
