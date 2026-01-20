"""
Visualization Endpoints.
Handles chart data generation operations.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Query

from app.models.schemas import VisualizationResponse, ErrorResponse
from app.services.visualization_service import VisualizationService
from app.utils.file_handler import FileHandler
from app.utils.logger import logger


router = APIRouter()


@router.get(
    "/columns/{session_id}",
    summary="Get Available Columns",
    description="Get list of available data columns for visualization."
)
async def get_available_columns(session_id: str):
    """
    Get available columns that can be used for visualizations.
    
    - **session_id**: Session ID
    - Returns list of column names from processed invoice data
    """
    if not FileHandler.session_exists(session_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found"
        )
    
    try:
        viz_service = VisualizationService(session_id)
        columns = viz_service.get_available_columns()
        
        return {
            "success": True,
            "session_id": session_id,
            "columns": columns
        }
        
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No processed data found. Please process invoices first."
        )


@router.get(
    "/{session_id}",
    response_model=VisualizationResponse,
    responses={404: {"model": ErrorResponse}, 400: {"model": ErrorResponse}},
    summary="Generate Visualizations",
    description="Generate chart data based on selected columns."
)
async def get_visualizations(
    session_id: str,
    columns: Optional[List[str]] = Query(
        default=None,
        description="Columns to include in visualization. If not provided, uses all columns."
    )
):
    """
    Generate visualization data for the processed invoice data.
    
    - **session_id**: Session ID
    - **columns**: Optional list of columns to visualize (query params)
    - Returns Plotly-compatible chart data
    """
    if not FileHandler.session_exists(session_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found"
        )
    
    try:
        viz_service = VisualizationService(session_id)
        available_columns = viz_service.get_available_columns()
        
        # Use all columns if none specified
        if columns is None or len(columns) == 0:
            selected_columns = available_columns
        else:
            # Validate selected columns
            invalid_columns = [c for c in columns if c not in available_columns]
            if invalid_columns:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid columns: {invalid_columns}. Available: {available_columns}"
                )
            selected_columns = columns
        
        # Generate visualizations
        charts = viz_service.generate_visualizations(selected_columns)
        
        logger.info(f"Session {session_id}: Generated {len(charts)} visualizations")
        
        return VisualizationResponse(
            success=True,
            session_id=session_id,
            available_columns=available_columns,
            selected_columns=selected_columns,
            charts=charts,
            total_charts=len(charts)
        )
        
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No processed data found. Please process invoices first."
        )
    except Exception as e:
        logger.error(f"Session {session_id}: Visualization error - {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Visualization generation failed: {str(e)}"
        )
