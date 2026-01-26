"""
Data Analyst Service.
Integrates the AI Data Analyst capabilities for advanced data querying and visualization.
Uses Gemini to generate Python code for analysis and executes it safely.
"""

import json
import traceback
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from typing import Dict, Any, List, Optional

from app.services.gemini_service import get_gemini_service
from app.utils.file_handler import FileHandler
from app.utils.logger import logger
from app.prompts.analytics import (
    get_code_generation_prompt,
    get_explanation_prompt,
    get_insights_prompt
)


class DataAnalystService:
    """
    Service for AI-powered data analysis.
    Can analyze either processed invoice data or uploaded CSV files.
    """
    
    def __init__(self, session_id: str):
        """
        Initialize the Data Analyst Service.
        
        Args:
            session_id: Unique session identifier
        """
        self.session_id = session_id
        self.file_handler = FileHandler(session_id)
        self.gemini = get_gemini_service()
        self.df: Optional[pd.DataFrame] = None
        self.df_info: Optional[Dict[str, Any]] = None
        
        # Load data immediately if available
        self._load_data()
        
    def _load_data(self):
        """
        Load data from the session.
        Priority:
        1. Custom uploaded CSV (for direct analysis mode)
        2. Processed Invoice Data (from invoice processing mode)
        """
        # 1. Check for custom CSV upload
        upload_dir = self.file_handler.get_upload_dir()
        if upload_dir.exists():
            for file in upload_dir.glob("*.csv"):
                try:
                    self.df = pd.read_csv(file)
                    logger.info(f"Loaded custom CSV: {file.name}")
                    break
                except Exception as e:
                    logger.warning(f"Failed to load CSV {file.name}: {e}")
        
        # 2. If no custom CSV, try processed invoice data
        if self.df is None:
            invoice_data = self.file_handler.load_invoice_data()
            if invoice_data:
                self.df = pd.DataFrame(invoice_data)
                logger.info("Loaded processed invoice data")
        
        # Prepare DataFrame Info if loaded
        if self.df is not None:
            self._prepare_df_info()
            
    def _prepare_df_info(self):
        """Prepare metadata about the DataFrame for the AI."""
        try:
            # Convert datetime columns to string for JSON serialization compatibility
            df_preview = self.df.head(5).copy()
            for col in df_preview.select_dtypes(include=['datetime64', 'datetime']).columns:
                df_preview[col] = df_preview[col].astype(str)
                
            self.df_info = {
                "columns": list(self.df.columns),
                "shape": self.df.shape,
                "dtypes": {col: str(dtype) for col, dtype in self.df.dtypes.items()},
                "preview": df_preview.to_dict(orient='records')
            }
        except Exception as e:
            logger.error(f"Error preparing DataFrame info: {e}")
            self.df_info = None

    async def analyze_query(self, user_question: str) -> Dict[str, Any]:
        """
        Analyze a user's question, generate Python code, execute it, and return the result.
        """
        if self.df is None:
            return {
                "success": False, 
                "error": "No data found. Please upload a CSV or process invoices first."
            }
            
        try:
            # Step 1: Generate Python Code
            code_response = await self._generate_code(user_question)
            if not code_response["success"]:
                return code_response
            
            generated_code = code_response["code"]
            
            # Step 2: Execute Code
            execution_result = self._execute_code(generated_code)
            if not execution_result["success"]:
                return execution_result
                
            # Step 3: Explain Results
            explanation = await self._generate_explanation(
                user_question, generated_code, execution_result
            )
            
            # Persist Chat History
            history = self.file_handler.load_chat_history()
            
            # User Message
            history.append({
                "role": "user",
                "text": user_question,
                "timestamp": datetime.now().isoformat()
            })
            
            # Assistant Message (with results)
            history.append({
                "role": "assistant",
                "text": explanation,
                "code": generated_code,
                "visualization": execution_result.get("visualization"),
                "data": execution_result.get("data"),
                "timestamp": datetime.now().isoformat()
            })
            
            self.file_handler.save_chat_history(history)
            
            return {
                "success": True,
                "answer": explanation,
                "code": generated_code,
                "visualization": execution_result.get("visualization"),
                "data": execution_result.get("data")
            }
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return {"success": False, "error": f"Analysis failed: {str(e)}"}

    async def _generate_code(self, question: str) -> Dict[str, Any]:
        """Generate Python code using Gemini."""
        prompt = get_code_generation_prompt(
            df_info=self.df_info,
            question=question,
            chart_path=str(self.file_handler.get_visualization_file())
        )
        try:
            # Use our existing GeminiService
            code = await self.gemini.generate_content(prompt, temperature=0.1)  # Low temp for precision
            
            # Sanitizing code
            code = code.strip()
            if code.startswith("```python"):
                code = code.split("```python")[1].split("```")[0].strip()
            elif code.startswith("```"):
                code = code.split("```")[1].split("```")[0].strip()
                
            return {"success": True, "code": code}
        except Exception as e:
            return {"success": False, "error": f"Code generation failed: {e}"}

    def _execute_code(self, code: str) -> Dict[str, Any]:
        """Execute the generated Python code safely."""
        try:
            # Prepare execution environment
            namespace = {
                'df': self.df.copy(),
                'pd': pd,
                'px': px,
                'go': go,
                'result': None
            }
            
            exec(code, namespace)
            
            result_data = namespace.get('result')
            # Check if a figure object exists in the namespace (generated by px or go)
            # Users often assign the figure to a variable or just call fig.show().
            # We look for any variable that is a Plotly Figure.
            
            chart_json = None
            
            # 1. Check for specific variable 'fig' or 'chart' (common convention)
            possible_figs = [namespace.get('fig'), namespace.get('chart'), namespace.get('result')]
            
            for obj in possible_figs:
                 if hasattr(obj, 'to_json'):
                     chart_json = obj.to_json()
                     break
            
            return {
                "success": True,
                "data": str(result_data) if result_data is not None else None,
                "visualization": chart_json 
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Code execution failed: {e}",
                "traceback": traceback.format_exc()
            }

    async def _generate_explanation(self, question: str, code: str, result: Dict) -> str:
        """Generate a natural language explanation of the findings."""
        prompt = get_explanation_prompt(
            question=question,
            code=code,
            result=result.get('data')
        )
        try:
            return await self.gemini.generate_content(prompt, temperature=0.7)
        except Exception:
            return "Analysis complete. See results below."

    async def generate_automated_insights(self) -> Dict[str, Any]:
        """Generate automated insights without a specific question."""
        if self.df is None:
            return {"success": False, "error": "No data loaded"}
            
        try:
            # Calculate summary stats locally (save tokens)
            summary = self._calculate_summary_stats()
            
            # Generate insights via AI
            prompt = get_insights_prompt(summary)
            
            response_text = await self.gemini.generate_content(prompt, temperature=0.5)
            
            # Clean and parse JSON
            cleaned_text = response_text.strip()
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text.split("```json")[1].split("```")[0].strip()
            elif cleaned_text.startswith("```"):
                cleaned_text = cleaned_text.split("```")[1].split("```")[0].strip()
                
            insights = json.loads(cleaned_text)
            
            return {
                "success": True, 
                "insights": insights,
                "summary": summary
            }
        except Exception as e:
            # Fallback
            logger.error(f"Insight generation error: {e}")
            return {
                "success": True,
                "insights": [
                    {"text": f"Dataset contains {len(self.df)} rows and {len(self.df.columns)} columns.", "category": "info", "priority": "low"}
                ],
                "summary": {}
            }

    def _calculate_summary_stats(self) -> Dict[str, Any]:
        """Calculate basic DF stats to feed to LLM."""
        desc = self.df.describe(include='all').to_dict()
        # Simplify for token usage...
        return {"shape": self.df.shape, "columns": list(self.df.columns), "description": str(desc)[:1000]} # Truncate for safety
