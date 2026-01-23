"""
AI Data Analyst Agent with Automated Insights
Uses Google Gemini to write and execute Python code for data analysis
"""

import os
import json
import traceback
from typing import Dict, Any, List
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent.parent / ".env")

# Configure Gemini
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in environment variables")

genai.configure(api_key=GOOGLE_API_KEY)


class DataAnalystAgent:
    """AI Agent that analyzes data by writing and executing Python code"""
    
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        self.conversation_history = []
        self.current_dataframe = None
        self.df_info = None
        
    def load_data(self, file_path: str) -> Dict[str, Any]:
        """Load CSV or Excel file"""
        try:
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext == '.csv':
                self.current_dataframe = pd.read_csv(file_path)
            elif file_ext in ['.xlsx', '.xls']:
                self.current_dataframe = pd.read_excel(file_path)
            else:
                return {"success": False, "error": "Unsupported file format"}
            
            # Convert datetime columns to strings for JSON serialization
            df_preview = self.current_dataframe.head(5).copy()
            for col in df_preview.select_dtypes(include=['datetime64', 'datetime']).columns:
                df_preview[col] = df_preview[col].astype(str)
            
            # Get dataframe info
            self.df_info = {
                "columns": list(self.current_dataframe.columns),
                "shape": self.current_dataframe.shape,
                "dtypes": {col: str(dtype) for col, dtype in self.current_dataframe.dtypes.items()},
                "preview": df_preview.to_dict(orient='records')
            }
            
            return {
                "success": True,
                "info": self.df_info,
                "message": f"Loaded {self.df_info['shape'][0]} rows and {self.df_info['shape'][1]} columns"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def analyze_query(self, user_question: str) -> Dict[str, Any]:
        """Analyze user's question and generate response"""
        
        if self.current_dataframe is None:
            return {
                "success": False,
                "error": "No data loaded. Please upload a file first."
            }
        
        try:
            # Step 1: Generate Python code using Gemini
            code_response = self._generate_code(user_question)
            
            if not code_response["success"]:
                return code_response
            
            generated_code = code_response["code"]
            
            # Step 2: Execute the code safely
            execution_result = self._execute_code(generated_code)
            
            if not execution_result["success"]:
                return execution_result
            
            # Step 3: Generate natural language explanation
            explanation = self._generate_explanation(
                user_question, 
                generated_code, 
                execution_result
            )
            
            return {
                "success": True,
                "answer": explanation,
                "code": generated_code,
                "visualization": execution_result.get("visualization"),
                "data": execution_result.get("data")
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Analysis failed: {str(e)}"
            }
    
    def _generate_code(self, question: str) -> Dict[str, Any]:
        """Generate Python code using Gemini"""
        
        prompt = f"""You are an expert data analyst. Generate Python code to answer this question about the dataset.

Dataset Information:
- Columns: {', '.join(self.df_info['columns'])}
- Shape: {self.df_info['shape'][0]} rows, {self.df_info['shape'][1]} columns
- Data types: {json.dumps(self.df_info['dtypes'], indent=2)}
- Preview (first 5 rows): {json.dumps(self.df_info['preview'], indent=2)}

User Question: {question}

CRITICAL RULES - FOLLOW STRICTLY:
1. Variable 'df' is ALREADY LOADED - DO NOT create or check for its existence
2. DO NOT use try-except blocks to check if 'df' exists
3. DO NOT create dummy/sample data or hardcoded DataFrames
4. NEVER use: try: df except NameError: ...
5. START your code directly using 'df' - it is guaranteed to exist
6. Use ONLY Plotly for visualizations (plotly.express or plotly.graph_objects)
7. For visualizations, save to 'outputs/chart.html' using fig.write_html()
8. Return results as a dictionary with key 'result'
9. DO NOT use matplotlib, seaborn, or any other plotting library
10. Use ALL rows from the dataframe - do not limit unless specifically asked

CORRECT EXAMPLE:
# Filter data directly - df already exists!
df_left = df[df['left'] == 1]
result = df_left['salary'].value_counts()

WRONG - NEVER DO THIS:
try:
    df
except NameError:
    df = pd.DataFrame([...])  # NEVER CREATE DUMMY DATA!

Generate ONLY executable Python code, no explanations or markdown.
"""

        try:
            response = self.model.generate_content(prompt)
            code = response.text.strip()
            
            # Clean up code (remove markdown if present)
            if code.startswith("```python"):
                code = code.split("```python")[1].split("```")[0].strip()
            elif code.startswith("```"):
                code = code.split("```")[1].split("```")[0].strip()
            
            return {"success": True, "code": code}
            
        except Exception as e:
            return {"success": False, "error": f"Code generation failed: {str(e)}"}
    
    def _execute_code(self, code: str) -> Dict[str, Any]:
        """Safely execute the generated Python code"""
        
        try:
            # Create a safe execution environment
            namespace = {
                'df': self.current_dataframe.copy(),
                'pd': pd,
                'px': px,
                'go': go,
                'result': None
            }
            
            # Execute the code
            exec(code, namespace)
            
            # Get the result
            result_data = namespace.get('result')
            
            # Check if visualization was created
            visualization_path = "outputs/chart.html"
            has_visualization = Path(visualization_path).exists()
            
            return {
                "success": True,
                "data": result_data,
                "visualization": visualization_path if has_visualization else None
            }
            
        except Exception as e:
            error_trace = traceback.format_exc()
            return {
                "success": False,
                "error": f"Code execution failed: {str(e)}",
                "traceback": error_trace
            }
    
    def _generate_explanation(self, question: str, code: str, execution_result: Dict) -> str:
        """Generate natural language explanation of the analysis"""
        
        prompt = f"""You are a data analyst explaining results to a non-technical user.

Original Question: {question}

Code Executed:
{code}

Result Data: {execution_result.get('data')}

Provide a clear, concise explanation of:
1. What the data shows
2. Key insights or findings
3. Any notable patterns or trends

Keep it conversational and easy to understand. Maximum 3-4 sentences.
"""

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            # Fallback explanation
            data = execution_result.get('data')
            if data:
                return f"Analysis complete. Result: {data}"
            return "Analysis completed successfully. Check the visualization for details."
    
    def generate_automated_insights(self) -> Dict[str, Any]:
        """Generate automated insights from data summary (minimal tokens)"""
        
        if self.current_dataframe is None:
            return {
                "success": False,
                "error": "No data loaded"
            }
        
        try:
            # Step 1: Calculate summary statistics locally (NO AI, NO TOKENS!)
            summary = self._calculate_summary_stats()
            
            # Step 2: Send ONLY summary to AI (minimal tokens ~300)
            insights = self._generate_insights_from_summary(summary)
            
            return {
                "success": True,
                "insights": insights,
                "summary": summary
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Insight generation failed: {str(e)}"
            }
    
    def _calculate_summary_stats(self) -> Dict[str, Any]:
        """Calculate summary statistics locally - NO AI tokens used"""
        
        df = self.current_dataframe
        summary = {
            "dataset_info": {
                "total_rows": len(df),
                "total_columns": len(df.columns),
                "columns": list(df.columns)
            },
            "numeric_columns": {},
            "categorical_columns": {},
            "missing_values": {},
            "correlations": {}
        }
        
        # Analyze numeric columns
        numeric_cols = df.select_dtypes(include=['number']).columns
        for col in numeric_cols:
            summary["numeric_columns"][col] = {
                "min": float(df[col].min()),
                "max": float(df[col].max()),
                "mean": float(df[col].mean()),
                "median": float(df[col].median()),
                "std": float(df[col].std()) if len(df) > 1 else 0,
                "unique_count": int(df[col].nunique())
            }
        
        # Analyze categorical columns (top 10 values only)
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        for col in categorical_cols:
            value_counts = df[col].value_counts().head(10)
            summary["categorical_columns"][col] = {
                "unique_count": int(df[col].nunique()),
                "top_values": {str(k): int(v) for k, v in value_counts.items()},
                "most_common": str(df[col].mode()[0]) if len(df[col].mode()) > 0 else None
            }
        
        # Missing values
        missing = df.isnull().sum()
        summary["missing_values"] = {
            col: int(count) for col, count in missing.items() if count > 0
        }
        
        # Correlations (only if numeric columns exist)
        if len(numeric_cols) > 1:
            corr_matrix = df[numeric_cols].corr()
            # Get strongest correlations (excluding diagonal)
            strong_corr = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    corr_val = corr_matrix.iloc[i, j]
                    if abs(corr_val) > 0.5:  # Only strong correlations
                        strong_corr.append({
                            "col1": corr_matrix.columns[i],
                            "col2": corr_matrix.columns[j],
                            "correlation": round(float(corr_val), 3)
                        })
            summary["correlations"] = strong_corr[:10]  # Top 10 only
        
        return summary
    
    def _generate_insights_from_summary(self, summary: Dict) -> List[Dict[str, str]]:
        """Generate insights from summary statistics using AI (minimal tokens)"""
        
        prompt = f"""You are a data analyst providing automated insights.

Analyze this dataset summary and provide 5-7 key insights:

Dataset Summary:
{json.dumps(summary, indent=2)}

For each insight, provide:
1. A clear, actionable finding
2. Category: "warning", "success", "info", or "neutral"
3. Priority: "high", "medium", "low"

Format as JSON array:
[
  {{"text": "X% of data has missing values in column Y - data quality issue", "category": "warning", "priority": "high"}},
  {{"text": "Strong correlation (0.85) between A and B suggests relationship", "category": "success", "priority": "medium"}}
]

RULES:
- Be specific with numbers
- Highlight data quality issues
- Point out interesting patterns
- Suggest areas to investigate
- Keep each insight to 1-2 sentences
- Maximum 7 insights total
"""

        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            
            # Clean JSON from markdown if present
            if text.startswith("```json"):
                text = text.split("```json")[1].split("```")[0].strip()
            elif text.startswith("```"):
                text = text.split("```")[1].split("```")[0].strip()
            
            insights = json.loads(text)
            return insights
            
        except Exception as e:
            # Fallback: Generate basic insights from summary
            insights = []
            
            # Data size insight
            total_rows = summary["dataset_info"]["total_rows"]
            insights.append({
                "text": f"Dataset contains {total_rows:,} rows and {summary['dataset_info']['total_columns']} columns",
                "category": "info",
                "priority": "low"
            })
            
            # Missing values insight
            if summary["missing_values"]:
                total_missing = sum(summary["missing_values"].values())
                insights.append({
                    "text": f"⚠️ Found {total_missing:,} missing values across {len(summary['missing_values'])} columns - data quality issue",
                    "category": "warning",
                    "priority": "high"
                })
            
            # Correlations insight
            if summary["correlations"]:
                top_corr = summary["correlations"][0]
                insights.append({
                    "text": f"Strong correlation ({top_corr['correlation']}) between {top_corr['col1']} and {top_corr['col2']}",
                    "category": "success",
                    "priority": "medium"
                })
            
            return insights
