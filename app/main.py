"""
FastAPI Application Entry Point.
Invoice Analyzer - AI-powered invoice processing API.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import settings
from app.api.v1.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    print(f"🚀 Starting {settings.app_name} v{settings.app_version}")
    print(f"📁 Storage directory: {settings.storage_dir.absolute()}")
    print(f"🤖 Gemini Model: {settings.gemini_model}")
    
    yield
    
    # Shutdown
    print("👋 Shutting down Invoice Analyzer API...")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    ## 📊 Invoice Analyzer API
    
    A powerful API for processing invoices using Google's Gemini AI.
    
    ### Features:
    - **Upload** multiple invoice images
    - **Extract** structured data using AI
    - **Generate** analytics reports
    - **Visualize** spending trends
    
    ### Authentication:
    Currently open API. Authentication will be added in future versions.
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(api_router, prefix="/api/v1")


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint - API information.
    """
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/api/v1/health"
    }
