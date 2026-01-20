"""
File Handler Utility.
Manages file operations for session-based storage.
"""

import os
import json
import shutil
import uuid
from pathlib import Path
from typing import Optional
from datetime import datetime

import pandas as pd
import aiofiles

from app.config.settings import settings
from app.utils.logger import logger


class FileHandler:
    """
    Handles file operations for a specific session.
    Each session has its own isolated storage directory.
    """
    
    def __init__(self, session_id: Optional[str] = None):
        """
        Initialize file handler for a session.
        
        Args:
            session_id: Unique session identifier. If None, generates a new one.
        """
        self.session_id = session_id or str(uuid.uuid4())
        self.session_dir = settings.storage_dir / "sessions" / self.session_id
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Create session directories if they don't exist."""
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.get_upload_dir().mkdir(parents=True, exist_ok=True)
    
    def get_upload_dir(self) -> Path:
        """Get the upload directory for this session."""
        return self.session_dir / "uploads"
    
    def get_data_file(self) -> Path:
        """Get the path to the processed data CSV file."""
        return self.session_dir / "invoice_data.csv"
    
    def get_report_file(self) -> Path:
        """Get the path to the generated report file."""
        return self.session_dir / "report.md"
    
    def get_metadata_file(self) -> Path:
        """Get the path to the session metadata file."""
        return self.session_dir / "metadata.json"
    
    @staticmethod
    def generate_session_id() -> str:
        """Generate a new unique session ID."""
        return str(uuid.uuid4())
    
    async def save_upload_file(self, file_content: bytes, filename: str) -> Path:
        """
        Save an uploaded file asynchronously.
        
        Args:
            file_content: File content as bytes
            filename: Original filename
            
        Returns:
            Path to saved file
        """
        # Sanitize filename
        safe_filename = self._sanitize_filename(filename)
        file_path = self.get_upload_dir() / safe_filename
        
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_content)
        
        logger.info(f"Saved upload: {safe_filename} in session {self.session_id}")
        return file_path
    
    def save_upload_file_sync(self, file_content: bytes, filename: str) -> Path:
        """
        Save an uploaded file synchronously.
        
        Args:
            file_content: File content as bytes
            filename: Original filename
            
        Returns:
            Path to saved file
        """
        safe_filename = self._sanitize_filename(filename)
        file_path = self.get_upload_dir() / safe_filename
        
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        logger.info(f"Saved upload: {safe_filename} in session {self.session_id}")
        return file_path
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename to prevent path traversal attacks."""
        # Remove any path components
        filename = os.path.basename(filename)
        # Replace problematic characters
        for char in ['..', '/', '\\', '\0']:
            filename = filename.replace(char, '_')
        return filename
    
    def get_uploaded_files(self) -> list[str]:
        """Get list of uploaded filenames."""
        upload_dir = self.get_upload_dir()
        if not upload_dir.exists():
            return []
        return [f.name for f in upload_dir.iterdir() if f.is_file()]
    
    def save_invoice_data(self, data: list[dict]) -> Path:
        """
        Save processed invoice data to CSV.
        
        Args:
            data: List of invoice dictionaries
            
        Returns:
            Path to saved CSV file
        """
        file_path = self.get_data_file()
        df = pd.DataFrame(data)
        df.to_csv(file_path, index=False)
        
        logger.info(f"Saved invoice data: {len(data)} items to {file_path}")
        return file_path
    
    def load_invoice_data(self) -> list[dict]:
        """
        Load processed invoice data from CSV.
        
        Returns:
            List of invoice dictionaries
        """
        file_path = self.get_data_file()
        
        if not file_path.exists():
            logger.warning(f"Invoice data file not found: {file_path}")
            return []
        
        df = pd.read_csv(file_path)
        return df.to_dict(orient='records')
    
    def save_report(self, report_text: str) -> Path:
        """
        Save generated report to file.
        
        Args:
            report_text: Report content in markdown
            
        Returns:
            Path to saved report file
        """
        file_path = self.get_report_file()
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        logger.info(f"Saved report to {file_path}")
        return file_path
    
    def load_report(self) -> str:
        """
        Load generated report from file.
        
        Returns:
            Report content or empty string if not found
        """
        file_path = self.get_report_file()
        
        if not file_path.exists():
            logger.warning(f"Report file not found: {file_path}")
            return ""
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def save_metadata(self, metadata: dict):
        """Save session metadata."""
        metadata['updated_at'] = datetime.now().isoformat()
        if 'created_at' not in metadata:
            metadata['created_at'] = datetime.now().isoformat()
        
        file_path = self.get_metadata_file()
        with open(file_path, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def load_metadata(self) -> dict:
        """Load session metadata."""
        file_path = self.get_metadata_file()
        
        if not file_path.exists():
            return {}
        
        with open(file_path, 'r') as f:
            return json.load(f)
    
    def get_session_info(self) -> dict:
        """Get session information."""
        metadata = self.load_metadata()
        
        return {
            "session_id": self.session_id,
            "files_count": len(self.get_uploaded_files()),
            "has_processed_data": self.get_data_file().exists(),
            "has_report": self.get_report_file().exists(),
            "created_at": metadata.get('created_at'),
        }
    
    def cleanup(self):
        """Delete all session files and directory."""
        try:
            if self.session_dir.exists():
                shutil.rmtree(self.session_dir)
                logger.info(f"Cleaned up session: {self.session_id}")
        except Exception as e:
            logger.error(f"Error cleaning up session {self.session_id}: {e}")
            raise
    
    @classmethod
    def cleanup_session(cls, session_id: str):
        """Class method to cleanup a session by ID."""
        handler = cls(session_id)
        handler.cleanup()
    
    @classmethod
    def list_sessions(cls) -> list[str]:
        """List all active session IDs."""
        sessions_dir = settings.storage_dir / "sessions"
        if not sessions_dir.exists():
            return []
        return [d.name for d in sessions_dir.iterdir() if d.is_dir()]
    
    @classmethod
    def session_exists(cls, session_id: str) -> bool:
        """Check if a session exists."""
        session_dir = settings.storage_dir / "sessions" / session_id
        return session_dir.exists()
