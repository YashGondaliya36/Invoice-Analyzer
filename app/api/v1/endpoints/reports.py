"""
Report Endpoints.
Handles analytics report generation operations.
"""

from fastapi import APIRouter, HTTPException, status

from app.models.schemas import ReportResponse, ErrorResponse
from app.services.report_generator import ReportGenerator
from app.utils.file_handler import FileHandler
from app.utils.logger import logger


router = APIRouter()


@router.post(
    "/generate/{session_id}",
    response_model=ReportResponse,
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    summary="Generate Analytics Report",
    description="Generate an AI-powered analytics report from uploaded invoices."
)
async def generate_report(session_id: str):
    """
    Generate an analytics report using Gemini AI.
    
    - **session_id**: Session ID from upload step
    - Returns a detailed markdown report with spending trends and insights
    """
    # Check if session exists
    if not FileHandler.session_exists(session_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found"
        )
    
    try:
        # Generate report
        generator = ReportGenerator(session_id)
        report_text = await generator.generate_report()
        
        # Update session metadata
        file_handler = FileHandler(session_id)
        metadata = file_handler.load_metadata()
        metadata["has_report"] = True
        file_handler.save_metadata(metadata)
        
        logger.info(f"Session {session_id}: Report generated successfully")
        
        return ReportResponse(
            success=True,
            session_id=session_id,
            report=report_text
        )
        
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Session {session_id}: Report generation error - {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Report generation failed: {str(e)}"
        )


@router.get(
    "/{session_id}",
    response_model=ReportResponse,
    responses={404: {"model": ErrorResponse}},
    summary="Get Saved Report",
    description="Retrieve a previously generated analytics report."
)
async def get_report(session_id: str):
    """
    Get a previously generated report.
    
    - **session_id**: Session ID
    - Returns the saved report text
    """
    if not FileHandler.session_exists(session_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found"
        )
    
    generator = ReportGenerator(session_id)
    report_text = generator.get_saved_report()
    
    if not report_text:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No report found. Please generate a report first."
        )
    
    return ReportResponse(
        success=True,
        session_id=session_id,
        report=report_text
    )
