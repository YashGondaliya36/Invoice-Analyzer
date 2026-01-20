"""
Invoice Endpoints.
Handles invoice upload and processing operations.
"""

from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException, status

from app.models.schemas import (
    UploadResponse,
    ProcessingResponse,
    InvoiceDataResponse,
    ErrorResponse,
)
from app.services.invoice_processor import InvoiceProcessor
from app.utils.file_handler import FileHandler
from app.utils.logger import logger
from app.config.settings import settings


router = APIRouter()


@router.post(
    "/upload",
    response_model=UploadResponse,
    responses={400: {"model": ErrorResponse}},
    summary="Upload Invoice Images",
    description="Upload multiple invoice images for processing. Returns a session ID for subsequent operations."
)
async def upload_invoices(
    files: List[UploadFile] = File(..., description="Invoice image files (JPG, JPEG, PNG)")
):
    """
    Upload invoice images to start a new processing session.
    
    - **files**: List of invoice image files
    - Returns a session_id to use for processing and other operations
    """
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No files provided"
        )
    
    # Validate file types
    allowed_extensions = set(settings.allowed_extensions)
    uploaded_files = []
    
    for file in files:
        # Get file extension
        ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
        
        if ext not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File '{file.filename}' has unsupported extension. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Check file size
        content = await file.read()
        if len(content) > settings.max_upload_size_mb * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File '{file.filename}' exceeds maximum size of {settings.max_upload_size_mb}MB"
            )
        
        # Reset file position for later reading
        await file.seek(0)
        uploaded_files.append((file.filename, content))
    
    # Create new session
    file_handler = FileHandler()
    session_id = file_handler.session_id
    
    # Save files
    saved_filenames = []
    for filename, content in uploaded_files:
        await file_handler.save_upload_file(content, filename)
        saved_filenames.append(filename)
    
    # Save session metadata
    file_handler.save_metadata({
        "status": "uploaded",
        "file_count": len(saved_filenames),
    })
    
    logger.info(f"Session {session_id}: Uploaded {len(saved_filenames)} files")
    
    return UploadResponse(
        success=True,
        session_id=session_id,
        file_count=len(saved_filenames),
        files=saved_filenames,
        message=f"{len(saved_filenames)} file(s) uploaded successfully"
    )


@router.post(
    "/process/{session_id}",
    response_model=ProcessingResponse,
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    summary="Process Uploaded Invoices",
    description="Process uploaded invoice images using AI to extract structured data."
)
async def process_invoices(session_id: str):
    """
    Process uploaded invoices using Gemini AI.
    
    - **session_id**: Session ID from upload step
    - Returns extracted invoice data as structured JSON
    """
    # Check if session exists
    if not FileHandler.session_exists(session_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found"
        )
    
    try:
        # Process invoices
        processor = InvoiceProcessor(session_id)
        data = await processor.process_invoices()
        
        # Update session metadata
        file_handler = FileHandler(session_id)
        file_handler.save_metadata({
            "status": "processed",
            "items_count": len(data),
        })
        
        logger.info(f"Session {session_id}: Processed {len(data)} invoice items")
        
        return ProcessingResponse(
            success=True,
            session_id=session_id,
            status="completed",
            total_items=len(data),
            data=data
        )
        
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Session {session_id}: Processing error - {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Processing failed: {str(e)}"
        )


@router.get(
    "/{session_id}",
    response_model=InvoiceDataResponse,
    responses={404: {"model": ErrorResponse}},
    summary="Get Processed Invoice Data",
    description="Retrieve previously processed invoice data for a session."
)
async def get_invoice_data(session_id: str):
    """
    Get processed invoice data for a session.
    
    - **session_id**: Session ID
    - Returns the extracted invoice data
    """
    if not FileHandler.session_exists(session_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found"
        )
    
    file_handler = FileHandler(session_id)
    data = file_handler.load_invoice_data()
    
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No processed data found. Please process invoices first."
        )
    
    return InvoiceDataResponse(
        success=True,
        session_id=session_id,
        total_items=len(data),
        data=data
    )
