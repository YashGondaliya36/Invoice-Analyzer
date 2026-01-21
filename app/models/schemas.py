"""
Pydantic Schemas for Invoice Analyzer API.
Defines request/response models for all endpoints.
"""

from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field


# ===========================================
# Common Response Models
# ===========================================

class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., example="healthy")
    message: str = Field(..., example="Invoice Analyzer API is running")


class ErrorResponse(BaseModel):
    """Standard error response."""
    success: bool = Field(default=False)
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(default=None, description="Detailed error info")


class MessageResponse(BaseModel):
    """Generic message response."""
    success: bool = Field(default=True)
    message: str = Field(..., description="Response message")


# ===========================================
# Invoice Data Models
# ===========================================

class InvoiceItem(BaseModel):
    """
    Single invoice line item extracted from invoice image.
    Matches the structure returned by Gemini AI.
    """
    invoice_no: str = Field(..., alias="Invoice No", description="Invoice number/reference")
    product_name: str = Field(..., alias="Product Name", description="Product or service name")
    qty: int = Field(..., alias="Qty", description="Quantity")
    amount: float = Field(..., alias="Amount", description="Amount value")
    date: str = Field(..., alias="Date", description="Invoice date (DD-MM-YY format)")
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "Invoice No": "INV001",
                "Product Name": "Steel Pipe 6mm",
                "Qty": 25,
                "Amount": 3593.10,
                "Date": "15-01-25"
            }
        }


class InvoiceDataResponse(BaseModel):
    """Response containing extracted invoice data."""
    success: bool = Field(default=True)
    session_id: str = Field(..., description="Session identifier")
    total_items: int = Field(..., description="Total invoice items extracted")
    data: list[InvoiceItem] = Field(..., description="List of invoice items")


# ===========================================
# Upload Models
# ===========================================

class UploadResponse(BaseModel):
    """Response after uploading invoice images."""
    success: bool = Field(default=True)
    session_id: str = Field(..., description="Unique session ID for this upload batch")
    file_count: int = Field(..., description="Number of files uploaded")
    files: list[str] = Field(..., description="List of uploaded filenames")
    message: str = Field(..., description="Status message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "file_count": 3,
                "files": ["invoice1.jpg", "invoice2.jpg", "invoice3.jpg"],
                "message": "3 file(s) uploaded successfully"
            }
        }


# ===========================================
# Processing Models
# ===========================================

class ProcessingRequest(BaseModel):
    """Optional request body for processing customization."""
    extract_all_fields: bool = Field(
        default=True, 
        description="Extract all available fields from invoices"
    )


class ProcessingResponse(BaseModel):
    """Response after processing invoice images."""
    success: bool = Field(default=True)
    session_id: str = Field(..., description="Session identifier")
    status: str = Field(..., description="Processing status")
    total_items: int = Field(..., description="Total items extracted")
    data: list[dict[str, Any]] = Field(..., description="Extracted invoice data")
    processed_at: datetime = Field(
        default_factory=datetime.now, 
        description="Processing timestamp"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "status": "completed",
                "total_items": 15,
                "data": [
                    {"Invoice No": "INV001", "Product Name": "Steel Pipe", "Qty": 10, "Amount": 5000.00, "Date": "15-01-25"}
                ],
                "processed_at": "2025-01-20T21:30:00"
            }
        }


# ===========================================
# Report Models
# ===========================================

class ReportResponse(BaseModel):
    """Response containing generated analytics report."""
    success: bool = Field(default=True)
    session_id: str = Field(..., description="Session identifier")
    report: str = Field(..., description="Generated analytics report text")
    generated_at: datetime = Field(
        default_factory=datetime.now, 
        description="Report generation timestamp"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "report": "## Spending Trends\n\n- Total spending: ₹50,000\n- Average per invoice: ₹5,000\n...",
                "generated_at": "2025-01-20T21:35:00"
            }
        }


# ===========================================
# Visualization Models
# ===========================================

class ChartData(BaseModel):
    """Single chart data structure."""
    chart_type: str = Field(..., description="Type of chart (bar, line, pie, etc.)")
    chart_name: str = Field(..., description="Display name for the chart")
    data: dict[str, Any] = Field(..., description="Plotly-compatible chart data")
    layout: Optional[dict[str, Any]] = Field(
        default=None, 
        description="Plotly layout configuration"
    )


class VisualizationRequest(BaseModel):
    """Request for generating visualizations."""
    columns: list[str] = Field(..., description="Columns to include in visualization")
    
    class Config:
        json_schema_extra = {
            "example": {
                "columns": ["Amount", "Date", "Product Name"]
            }
        }


class VisualizationResponse(BaseModel):
    """Response containing visualization data."""
    success: bool = Field(default=True)
    session_id: str = Field(..., description="Session identifier")
    available_columns: list[str] = Field(..., description="Available columns in data")
    selected_columns: list[str] = Field(..., description="Columns used for visualization")
    charts: list[ChartData] = Field(..., description="List of generated charts")
    total_charts: int = Field(..., description="Number of charts generated")


# ===========================================
# Analytics Models
# ===========================================

class AnalyticsQueryRequest(BaseModel):
    """Request to ask a question to the AI Data Analyst."""
    question: str = Field(..., description="Natural language question about the data")

class AnalyticsResponse(BaseModel):
    """Response from AI Data Analyst."""
    success: bool = Field(default=True)
    answer: str = Field(..., description="Natural language explanation")
    code: Optional[str] = Field(None, description="Generated Python code")
    data: Optional[str] = Field(None, description="Result data (if any)")
    visualization: Optional[str] = Field(None, description="URL/Path to generated chart HTML")

class InsightItem(BaseModel):
    """Single insight item."""
    text: str
    category: str  # info, warning, success, neutral
    priority: str  # high, medium, low

class InsightResponse(BaseModel):
    """Response containing automated insights."""
    success: bool = Field(default=True)
    insights: list[InsightItem]
    summary: Optional[dict[str, Any]] = None


# ===========================================
# Session Models
# ===========================================

class SessionResponse(BaseModel):
    """Response for session operations."""
    success: bool = Field(default=True)
    session_id: str = Field(..., description="Session identifier")
    status: str = Field(..., description="Session status")
    message: str = Field(..., description="Status message")
    created_at: Optional[datetime] = Field(default=None, description="Session creation time")
    files_count: Optional[int] = Field(default=None, description="Number of files in session")
    has_processed_data: Optional[bool] = Field(default=None, description="Whether data has been processed")
    has_report: Optional[bool] = Field(default=None, description="Whether report has been generated")


class SessionListResponse(BaseModel):
    """Response containing list of active sessions."""
    success: bool = Field(default=True)
    total_sessions: int = Field(..., description="Total number of active sessions")
    sessions: list[SessionResponse] = Field(..., description="List of session details")
