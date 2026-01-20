"""
Session Endpoints.
Handles session management operations.
"""

from fastapi import APIRouter, HTTPException, status

from app.models.schemas import SessionResponse, SessionListResponse, MessageResponse, ErrorResponse
from app.utils.file_handler import FileHandler
from app.utils.logger import logger


router = APIRouter()


@router.get(
    "/",
    response_model=SessionListResponse,
    summary="List All Sessions",
    description="List all active sessions."
)
async def list_sessions():
    """
    Get a list of all active sessions.
    
    - Returns list of session IDs with their details
    """
    session_ids = FileHandler.list_sessions()
    
    sessions = []
    for sid in session_ids:
        try:
            file_handler = FileHandler(sid)
            info = file_handler.get_session_info()
            sessions.append(SessionResponse(
                session_id=sid,
                status="active",
                message="Session active",
                files_count=info.get("files_count"),
                has_processed_data=info.get("has_processed_data"),
                has_report=info.get("has_report"),
                created_at=info.get("created_at")
            ))
        except Exception as e:
            logger.warning(f"Error getting info for session {sid}: {e}")
    
    return SessionListResponse(
        success=True,
        total_sessions=len(sessions),
        sessions=sessions
    )


@router.get(
    "/{session_id}",
    response_model=SessionResponse,
    responses={404: {"model": ErrorResponse}},
    summary="Get Session Info",
    description="Get detailed information about a specific session."
)
async def get_session(session_id: str):
    """
    Get information about a specific session.
    
    - **session_id**: Session ID
    - Returns session details including file count and processing status
    """
    if not FileHandler.session_exists(session_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found"
        )
    
    file_handler = FileHandler(session_id)
    info = file_handler.get_session_info()
    
    return SessionResponse(
        success=True,
        session_id=session_id,
        status="active",
        message="Session found",
        files_count=info.get("files_count"),
        has_processed_data=info.get("has_processed_data"),
        has_report=info.get("has_report"),
        created_at=info.get("created_at")
    )


@router.delete(
    "/{session_id}",
    response_model=MessageResponse,
    responses={404: {"model": ErrorResponse}},
    summary="Delete Session",
    description="Delete a session and all its associated files."
)
async def delete_session(session_id: str):
    """
    Delete a session and clean up all associated files.
    
    - **session_id**: Session ID to delete
    - Returns success confirmation
    """
    if not FileHandler.session_exists(session_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found"
        )
    
    try:
        FileHandler.cleanup_session(session_id)
        logger.info(f"Session {session_id}: Deleted successfully")
        
        return MessageResponse(
            success=True,
            message=f"Session '{session_id}' deleted successfully"
        )
        
    except Exception as e:
        logger.error(f"Session {session_id}: Deletion error - {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete session: {str(e)}"
        )


@router.delete(
    "/",
    response_model=MessageResponse,
    summary="Delete All Sessions",
    description="Delete all sessions and their associated files."
)
async def delete_all_sessions():
    """
    Delete all sessions and clean up all files.
    
    - Returns success confirmation with count of deleted sessions
    """
    session_ids = FileHandler.list_sessions()
    deleted_count = 0
    
    for sid in session_ids:
        try:
            FileHandler.cleanup_session(sid)
            deleted_count += 1
        except Exception as e:
            logger.warning(f"Failed to delete session {sid}: {e}")
    
    logger.info(f"Deleted {deleted_count} sessions")
    
    return MessageResponse(
        success=True,
        message=f"Deleted {deleted_count} session(s)"
    )
