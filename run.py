"""
Uvicorn Runner Script.
Use this to start the FastAPI server.

Usage:
    python run.py
    
Or directly with uvicorn:
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
"""

import uvicorn
from app.config.settings import settings


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )
