"""
Main API Router for Version 1.
Aggregates all endpoint routers.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import invoices, reports, visualizations, sessions


# Create main API router
api_router = APIRouter()


# Health check endpoint
@api_router.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint to verify API is running.
    """
    return {
        "status": "healthy",
        "message": "Invoice Analyzer API is running"
    }


# Include endpoint routers
api_router.include_router(
    invoices.router,
    prefix="/invoices",
    tags=["Invoices"]
)

api_router.include_router(
    reports.router,
    prefix="/reports",
    tags=["Reports"]
)

api_router.include_router(
    visualizations.router,
    prefix="/visualizations",
    tags=["Visualizations"]
)

api_router.include_router(
    sessions.router,
    prefix="/sessions",
    tags=["Sessions"]
)
