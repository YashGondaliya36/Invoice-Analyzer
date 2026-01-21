"""
Analytics API Endpoints.
Handles CSV upload, AI queries, and automated insights.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, status
from fastapi.responses import FileResponse

from app.services.data_analyst import DataAnalystService
from app.utils.file_handler import FileHandler
from app.utils.logger import logger
from app.models.schemas import (
    UploadResponse, 
    AnalyticsQueryRequest, 
    AnalyticsResponse, 
    InsightResponse,
    ErrorResponse
)

router = APIRouter()

@router.post(
    "/upload-csv",
    response_model=UploadResponse,
    summary="Upload CSV for Analysis",
    description="Upload a CSV file directly for analysis (bypassing invoice processing)."
)
async def upload_csv(
    file: UploadFile = File(..., description="CSV file")
):
    """
    Upload a CSV file to start a new analysis session.
    """
    if not file.filename.endswith('.csv'):
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only .csv files are supported."
        )

    # Create new session
    file_handler = FileHandler()
    session_id = file_handler.session_id
    
    # Save file
    content = await file.read()
    await file_handler.save_upload_file(content, file.filename)
    
    # Init service to validate load
    try:
        service = DataAnalystService(session_id)
        if service.df is None:
             raise HTTPException(status_code=400, detail="Failed to load CSV data.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading CSV: {e}")
        
    return UploadResponse(
        success=True,
        session_id=session_id,
        file_count=1,
        files=[file.filename],
        message="CSV uploaded successfully. Ready for analysis."
    )

@router.post(
    "/ask/{session_id}",
    response_model=AnalyticsResponse,
    summary="Ask Question about Data",
    description="Ask a natural language question. Generates Python code and visualization."
)
async def ask_question(session_id: str, request: AnalyticsQueryRequest):
    """
    Ask a question about the data in the session.
    """
    if not FileHandler.session_exists(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
        
    service = DataAnalystService(session_id)
    result = await service.analyze_query(request.question)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error", "Unknown error"))
        
    return AnalyticsResponse(
        success=True,
        answer=result["answer"],
        code=result["code"],
        data=result.get("data"),
        visualization=result.get("visualization")
    )

@router.get(
    "/insights/{session_id}",
    response_model=InsightResponse,
    summary="Get Automated Insights",
    description="Generate automated insights from the dataset."
)
async def get_insights(session_id: str):
    """
    Generate automated insights for the session data.
    """
    if not FileHandler.session_exists(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
        
    service = DataAnalystService(session_id)
    result = await service.generate_automated_insights()
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error", "Unknown error"))
        
    return InsightResponse(
        success=True,
        insights=result["insights"],
        summary=result.get("summary")
    )

@router.get(
    "/chart/{session_id}",
    response_class=FileResponse,
    summary="Get Generated Chart",
    description="Download/View the latest generated chart HTML."
)
async def get_chart(session_id: str):
    """
    Retrieve the generated chart HTML file.
    """
    if not FileHandler.session_exists(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
        
    file_handler = FileHandler(session_id)
    chart_path = file_handler.get_visualization_file()
    
    if not chart_path.exists():
        raise HTTPException(status_code=404, detail="No chart found for this session.")
        
    return FileResponse(chart_path)
