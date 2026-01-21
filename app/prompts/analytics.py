"""
Analytics Prompts.
Contains prompts for generic analytics, reporting, and AI code generation.
"""
import json
from typing import Dict, Any

# ==========================================
# Report Generation
# ==========================================

REPORT_GENERATION_PROMPT = """
You are a financial analyst tasked with reviewing a dataset of invoices. 
Based on the provided invoice images, create a detailed and structured report covering the following aspects:

## Spending Trends:
- Summarize the overall spending patterns, including total spending, average spending per invoice, and spending fluctuations over time.
- Highlight the top spending periods (e.g., months, quarters, or years).
- Identify categories, vendors, or clients contributing the most to spending.

## Key Performance Indicators (KPIs):
- Analyze the total number of invoices and the average number of items per invoice.
- Highlight high-value invoices (e.g., those exceeding a specific threshold).
- Report on vendor/client contributions to spending or revenue.

## Product or Service Usage Insights:
- Identify the most frequently purchased products or services and their revenue contributions.
- Highlight any underutilized or low-demand products/services.
- Note trends in product/service usage (e.g., increasing or decreasing demand).
- Rank the top product/service categories based on sales volume or revenue.

## Actionable Insights:
- Provide recommendations for optimizing spending, improving product/service utilization, or addressing any identified issues.

## Additional Instructions:
- Format the report with clear sections and bullet points for readability.
- Use quantitative metrics and percentages wherever possible.
- Ensure insights are actionable and backed by data trends.
- Use markdown formatting for headers and lists.
"""


# ==========================================
# Data Analyst Agent
# ==========================================

def get_code_generation_prompt(df_info: Dict[str, Any], question: str, chart_path: str) -> str:
    """
    Generate prompt for Python code generation.
    """
    return f"""You are an expert data analyst. Generate Python code to answer this question about the dataset.

Dataset Information:
- Columns: {', '.join(df_info.get('columns', []))}
- Shape: {df_info.get('shape', 'Unknown')}
- Data types: {json.dumps(df_info.get('dtypes', {}), indent=2)}
- Preview: {json.dumps(df_info.get('preview', []), indent=2)}

User Question: {question}

CRITICAL RULES:
1. 'df' is ALREADY LOADED. DO NOT create sample data.
2. Use 'df' directly.
3. Use ONLY plotly.express (as px) or plotly.graph_objects (as go) for plotting.
4. Save charts to '{chart_path}' using fig.write_html().
   Example: fig.write_html('{chart_path.replace("\\", "\\\\")}')
5. Assign final answer/data to variable 'result'.
6. Return purely executable Python code. No markdown.
"""


def get_explanation_prompt(question: str, code: str, result: Any) -> str:
    """
    Generate prompt for explaining the analysis results.
    """
    return f"""Explain these analysis results to a user.
Question: {question}
Code:
{code}
Result: {result}

Keep it concise, insightful, and easy to understand (max 3 sentences).
"""


def get_insights_prompt(summary: Dict[str, Any]) -> str:
    """
    Generate prompt for automated insights.
    """
    return f"""Analyze this dataset summary and provide 5 key insights.
Summary: {json.dumps(summary, indent=2)}

Format as JSON list of objects with keys: "text" (insight), "category" (info/warning/success), "priority" (high/medium/low).
"""
