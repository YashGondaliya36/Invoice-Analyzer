"""
DataWiz AI - AI-Powered Data Analyst
FastAPI Backend Server
"""

import os
import uuid
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from pydantic import BaseModel
import aiofiles

from ai_agent import DataAnalystAgent

# Initialize FastAPI app
app = FastAPI(title="DataWiz AI", description="AI-Powered Data Analyst")

# Setup directories
BASE_DIR = Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

# Ensure directories exist
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/outputs", StaticFiles(directory=OUTPUT_DIR), name="outputs")

# Setup templates
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Initialize AI Agent
agent = DataAnalystAgent()

# Track current session
current_file = None


class QuestionRequest(BaseModel):
    """Request model for asking questions"""
    question: str


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main page"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload CSV or Excel file"""
    global current_file
    
    try:
        # Validate file type
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ['.csv', '.xlsx', '.xls']:
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Please upload CSV or Excel file."
            )
        
        # Generate unique filename
        file_id = str(uuid.uuid4())[:8]
        filename = f"{file_id}_{file.filename}"
        file_path = UPLOAD_DIR / filename
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        # Load data with AI agent
        result = agent.load_data(str(file_path))
        
        if not result["success"]:
            # Clean up file if loading failed
            file_path.unlink(missing_ok=True)
            raise HTTPException(status_code=400, detail=result["error"])
        
        current_file = str(file_path)
        
        return {
            "success": True,
            "filename": file.filename,
            "info": result["info"],
            "message": result["message"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ask")
async def ask_question(request: QuestionRequest):
    """Ask a question about the data"""
    
    if current_file is None:
        raise HTTPException(
            status_code=400,
            detail="No file uploaded. Please upload a file first."
        )
    
    try:
        # Analyze the question
        result = agent.analyze_query(request.question)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "success": True,
            "answer": result["answer"],
            "code": result["code"],
            "visualization": result.get("visualization"),
            "data": result.get("data")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/chart")
async def get_chart():
    """Get the latest generated chart"""
    chart_path = OUTPUT_DIR / "chart.html"
    
    if not chart_path.exists():
        raise HTTPException(status_code=404, detail="No chart available")
    
    return FileResponse(chart_path)


@app.get("/api/insights")
async def get_insights():
    """Generate automated insights from data"""
    
    if current_file is None:
        raise HTTPException(
            status_code=400,
            detail="No file uploaded. Please upload a file first."
        )
    
    try:
        # Generate insights
        result = agent.generate_automated_insights()
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "success": True,
            "insights": result["insights"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/reset")
async def reset_session():
    """Reset the current session"""
    global current_file, agent
    
    try:
        # Clear uploaded files
        for file in UPLOAD_DIR.glob("*"):
            if file.is_file() and file.name != ".gitkeep":
                file.unlink()
        
        # Clear output charts
        for file in OUTPUT_DIR.glob("*"):
            if file.is_file() and file.name != ".gitkeep":
                file.unlink()
        
        # Reinitialize agent
        agent = DataAnalystAgent()
        current_file = None
        
        return {"success": True, "message": "Session reset successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting DataWiz AI Server...")
    print("📊 Access the app at: http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
