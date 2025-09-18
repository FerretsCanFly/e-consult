"""Azure App Service entry point."""
import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(__file__))

# Import the FastAPI app
from src.api.endpoints import app

# This is needed for Azure App Service
application = app

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
