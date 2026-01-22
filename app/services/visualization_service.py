"""
Visualization Service.
Generates chart data from processed invoice data.
Returns JSON-serializable data for frontend rendering.
"""

from typing import Any, Optional
import pandas as pd

from app.utils.logger import logger
from app.utils.file_handler import FileHandler


class VisualizationService:
    """
    Service for generating visualization data from invoice data.
    Returns Plotly-compatible JSON data instead of figure objects.
    """
    
    def __init__(self, session_id: str):
        """
        Initialize the visualization service.
        
        Args:
            session_id: Unique session identifier
        """
        self.session_id = session_id
        self.file_handler = FileHandler(session_id)
        self._df: Optional[pd.DataFrame] = None
        logger.info(f"Visualization service initialized for session: {session_id}")
    
    @property
    def df(self) -> pd.DataFrame:
        """Load and cache the dataframe from invoice data or uploaded CSV."""
        if self._df is None:
            # Priority 1: Check for uploaded CSV files (direct CSV upload mode)
            upload_dir = self.file_handler.get_upload_dir()
            if upload_dir.exists():
                for file in upload_dir.glob("*.csv"):
                    try:
                        self._df = pd.read_csv(file)
                        logger.info(f"Loaded CSV from uploads: {file.name}")
                        return self._df
                    except Exception as e:
                        logger.warning(f"Failed to load CSV {file.name}: {e}")
            
            # Priority 2: Load processed invoice data (invoice image mode)
            data = self.file_handler.load_invoice_data()
            if not data:
                raise FileNotFoundError("No data found. Please upload invoices or CSV first.")
            self._df = pd.DataFrame(data)
            logger.info("Loaded processed invoice data")
        return self._df
    
    def get_available_columns(self) -> list[str]:
        """Get list of available columns in the data."""
        return self.df.columns.tolist()
    
    def _find_column(self, possible_names: list[str]) -> Optional[str]:
        """Find a column matching any of the possible names."""
        for name in possible_names:
            matches = [col for col in self.df.columns if name.lower() in col.lower()]
            if matches:
                return matches[0]
        return None
    
    def generate_visualizations(self, selected_columns: list[str]) -> list[dict[str, Any]]:
        """
        Generate visualization data for selected columns.
        
        Args:
            selected_columns: List of column names to visualize
            
        Returns:
            List of chart data dictionaries
        """
        logger.info(f"Generating visualizations for columns: {selected_columns}")
        
        charts = []
        df_selected = self.df[selected_columns]
        
        # Identify column types
        date_col = self._find_column(['date', 'invoice date', 'bill date'])
        product_col = self._find_column(['product', 'item', 'description', 'product name'])
        amount_col = self._find_column(['amount', 'total', 'value'])
        quantity_col = self._find_column(['qty', 'quantity', 'units'])
        invoice_col = self._find_column(['invoice', 'invoice number', 'invoice no', 'bill number'])
        
        # Filter to only selected columns
        date_col = date_col if date_col in selected_columns else None
        product_col = product_col if product_col in selected_columns else None
        amount_col = amount_col if amount_col in selected_columns else None
        quantity_col = quantity_col if quantity_col in selected_columns else None
        invoice_col = invoice_col if invoice_col in selected_columns else None
        
        # Generate charts based on available columns
        if amount_col:
            charts.append(self._amount_boxplot(df_selected, amount_col))
        
        if quantity_col:
            charts.append(self._quantity_boxplot(df_selected, quantity_col))
        
        if product_col and amount_col:
            charts.append(self._product_sales_bar(df_selected, product_col, amount_col))
            charts.append(self._top_products_pareto(df_selected, product_col, amount_col))
        
        if product_col and quantity_col:
            charts.append(self._quantity_by_product(df_selected, product_col, quantity_col))
        
        if date_col and amount_col:
            charts.append(self._daily_sales_line(df_selected, date_col, amount_col))
            charts.append(self._monthly_revenue(df_selected, date_col, amount_col))
            charts.append(self._weekday_analysis(df_selected, date_col, amount_col))
        
        if invoice_col and date_col:
            charts.append(self._invoice_trends(df_selected, invoice_col, date_col))
        
        if invoice_col and product_col:
            charts.append(self._products_per_invoice(df_selected, invoice_col, product_col))
        
        # Filter out None values
        charts = [c for c in charts if c is not None]
        
        logger.info(f"Generated {len(charts)} charts")
        return charts
    
    def _amount_boxplot(self, df: pd.DataFrame, amount_col: str) -> dict[str, Any]:
        """Generate amount distribution boxplot data."""
        try:
            return {
                "chart_type": "box",
                "chart_name": "Amount Distribution",
                "data": {
                    "y": df[amount_col].tolist(),
                    "type": "box",
                    "name": "Amount",
                    "marker": {"color": "#636EFA"}
                },
                "layout": {
                    "title": "Amount Distribution",
                    "yaxis": {"title": amount_col},
                    "template": "plotly_white"
                }
            }
        except Exception as e:
            logger.error(f"Error creating amount boxplot: {e}")
            return None
    
    def _quantity_boxplot(self, df: pd.DataFrame, quantity_col: str) -> dict[str, Any]:
        """Generate quantity distribution boxplot data."""
        try:
            return {
                "chart_type": "box",
                "chart_name": "Quantity Distribution",
                "data": {
                    "x": df[quantity_col].tolist(),
                    "type": "box",
                    "name": "Quantity",
                    "marker": {"color": "#FF6347"}
                },
                "layout": {
                    "title": "Quantity Distribution",
                    "xaxis": {"title": quantity_col},
                    "template": "plotly_white"
                }
            }
        except Exception as e:
            logger.error(f"Error creating quantity boxplot: {e}")
            return None
    
    def _product_sales_bar(self, df: pd.DataFrame, product_col: str, amount_col: str) -> dict[str, Any]:
        """Generate sales by product bar chart data."""
        try:
            product_sales = df.groupby(product_col)[amount_col].sum().reset_index()
            product_sales = product_sales.sort_values(by=amount_col, ascending=True)
            
            return {
                "chart_type": "bar",
                "chart_name": "Sales by Product",
                "data": {
                    "x": product_sales[amount_col].tolist(),
                    "y": product_sales[product_col].tolist(),
                    "type": "bar",
                    "orientation": "h",
                    "marker": {
                        "color": product_sales[amount_col].tolist(),
                        "colorscale": "Viridis"
                    }
                },
                "layout": {
                    "title": "Sales by Product",
                    "xaxis": {"title": "Total Sales Amount"},
                    "yaxis": {"title": product_col},
                    "template": "plotly_white",
                    "height": max(400, len(product_sales) * 30)
                }
            }
        except Exception as e:
            logger.error(f"Error creating product sales bar: {e}")
            return None
    
    def _top_products_pareto(self, df: pd.DataFrame, product_col: str, amount_col: str) -> dict[str, Any]:
        """Generate top products pareto chart data."""
        try:
            product_sales = df.groupby(product_col)[amount_col].sum().sort_values(ascending=False).reset_index()
            top_10 = product_sales.head(10)
            cumulative_pct = (top_10[amount_col].cumsum() / product_sales[amount_col].sum() * 100).tolist()
            
            return {
                "chart_type": "bar+line",
                "chart_name": "Top 10 Products (Pareto)",
                "data": [
                    {
                        "x": top_10[product_col].tolist(),
                        "y": top_10[amount_col].tolist(),
                        "type": "bar",
                        "name": "Revenue",
                        "marker": {"color": "#636EFA"}
                    },
                    {
                        "x": top_10[product_col].tolist(),
                        "y": cumulative_pct,
                        "type": "scatter",
                        "mode": "lines+markers",
                        "name": "Cumulative %",
                        "yaxis": "y2",
                        "marker": {"color": "#EF553B"}
                    }
                ],
                "layout": {
                    "title": "Top 10 Products by Revenue (Pareto)",
                    "xaxis": {"title": "Product"},
                    "yaxis": {"title": "Revenue"},
                    "yaxis2": {
                        "title": "Cumulative %",
                        "overlaying": "y",
                        "side": "right",
                        "range": [0, 100]
                    },
                    "template": "plotly_white"
                }
            }
        except Exception as e:
            logger.error(f"Error creating pareto chart: {e}")
            return None
    
    def _quantity_by_product(self, df: pd.DataFrame, product_col: str, quantity_col: str) -> dict[str, Any]:
        """Generate quantity by product bar chart data."""
        try:
            qty_by_product = df.groupby(product_col)[quantity_col].sum().reset_index()
            qty_by_product = qty_by_product.sort_values(by=quantity_col, ascending=True)
            
            return {
                "chart_type": "bar",
                "chart_name": "Quantity by Product",
                "data": {
                    "x": qty_by_product[quantity_col].tolist(),
                    "y": qty_by_product[product_col].tolist(),
                    "type": "bar",
                    "orientation": "h",
                    "marker": {
                        "color": qty_by_product[quantity_col].tolist(),
                        "colorscale": "Cividis"
                    }
                },
                "layout": {
                    "title": "Quantity Sold by Product",
                    "xaxis": {"title": "Total Quantity"},
                    "yaxis": {"title": product_col},
                    "template": "plotly_white",
                    "height": max(400, len(qty_by_product) * 30)
                }
            }
        except Exception as e:
            logger.error(f"Error creating quantity by product: {e}")
            return None
    
    def _daily_sales_line(self, df: pd.DataFrame, date_col: str, amount_col: str) -> dict[str, Any]:
        """Generate daily sales line chart data."""
        try:
            df_copy = df.copy()
            df_copy[date_col] = pd.to_datetime(df_copy[date_col], format='mixed', dayfirst=True)
            daily_sales = df_copy.groupby(df_copy[date_col].dt.date)[amount_col].sum().reset_index()
            
            return {
                "chart_type": "line",
                "chart_name": "Daily Sales Trend",
                "data": {
                    "x": [str(d) for d in daily_sales[date_col].tolist()],
                    "y": daily_sales[amount_col].tolist(),
                    "type": "scatter",
                    "mode": "lines+markers",
                    "name": "Daily Sales",
                    "marker": {"color": "#636EFA"}
                },
                "layout": {
                    "title": "Daily Sales Analysis",
                    "xaxis": {"title": "Date"},
                    "yaxis": {"title": "Total Sales"},
                    "template": "plotly_white"
                }
            }
        except Exception as e:
            logger.error(f"Error creating daily sales line: {e}")
            return None
    
    def _monthly_revenue(self, df: pd.DataFrame, date_col: str, amount_col: str) -> dict[str, Any]:
        """Generate monthly revenue bar chart data."""
        try:
            df_copy = df.copy()
            df_copy[date_col] = pd.to_datetime(df_copy[date_col], format='mixed', dayfirst=True)
            monthly = df_copy.groupby(df_copy[date_col].dt.strftime('%Y-%m'))[amount_col].sum().reset_index()
            
            return {
                "chart_type": "bar",
                "chart_name": "Monthly Revenue",
                "data": {
                    "x": monthly[date_col].tolist(),
                    "y": monthly[amount_col].tolist(),
                    "type": "bar",
                    "marker": {
                        "color": monthly[amount_col].tolist(),
                        "colorscale": "Viridis"
                    }
                },
                "layout": {
                    "title": "Monthly Revenue Analysis",
                    "xaxis": {"title": "Month"},
                    "yaxis": {"title": "Total Revenue"},
                    "template": "plotly_white"
                }
            }
        except Exception as e:
            logger.error(f"Error creating monthly revenue: {e}")
            return None
    
    def _weekday_analysis(self, df: pd.DataFrame, date_col: str, amount_col: str) -> dict[str, Any]:
        """Generate weekday sales analysis data."""
        try:
            df_copy = df.copy()
            df_copy[date_col] = pd.to_datetime(df_copy[date_col], format='mixed', dayfirst=True)
            df_copy['weekday'] = df_copy[date_col].dt.day_name()
            weekday_sales = df_copy.groupby('weekday')[amount_col].sum().reset_index()
            
            # Order weekdays properly
            weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            weekday_sales['weekday'] = pd.Categorical(weekday_sales['weekday'], categories=weekday_order, ordered=True)
            weekday_sales = weekday_sales.sort_values('weekday')
            
            return {
                "chart_type": "bar",
                "chart_name": "Sales by Weekday",
                "data": {
                    "x": weekday_sales['weekday'].tolist(),
                    "y": weekday_sales[amount_col].tolist(),
                    "type": "bar",
                    "marker": {"color": "#00CC96"}
                },
                "layout": {
                    "title": "Sales by Day of Week",
                    "xaxis": {"title": "Day"},
                    "yaxis": {"title": "Total Sales"},
                    "template": "plotly_white"
                }
            }
        except Exception as e:
            logger.error(f"Error creating weekday analysis: {e}")
            return None
    
    def _invoice_trends(self, df: pd.DataFrame, invoice_col: str, date_col: str) -> dict[str, Any]:
        """Generate invoice count trends data."""
        try:
            df_copy = df.copy()
            df_copy[date_col] = pd.to_datetime(df_copy[date_col], format='mixed', dayfirst=True)
            daily_invoices = df_copy.groupby(df_copy[date_col].dt.date)[invoice_col].nunique().reset_index()
            
            return {
                "chart_type": "line",
                "chart_name": "Daily Invoice Count",
                "data": {
                    "x": [str(d) for d in daily_invoices[date_col].tolist()],
                    "y": daily_invoices[invoice_col].tolist(),
                    "type": "scatter",
                    "mode": "lines+markers",
                    "name": "Invoice Count",
                    "line": {"shape": "spline"},
                    "marker": {"color": "#FF69B4"}
                },
                "layout": {
                    "title": "Daily Invoice Count",
                    "xaxis": {"title": "Date"},
                    "yaxis": {"title": "Number of Invoices", "dtick": 1},
                    "template": "plotly_white"
                }
            }
        except Exception as e:
            logger.error(f"Error creating invoice trends: {e}")
            return None
    
    def _products_per_invoice(self, df: pd.DataFrame, invoice_col: str, product_col: str) -> dict[str, Any]:
        """Generate products per invoice chart data."""
        try:
            products_per = df.groupby(invoice_col)[product_col].nunique().reset_index()
            products_per.columns = [invoice_col, 'num_products']
            
            return {
                "chart_type": "bar",
                "chart_name": "Products per Invoice",
                "data": {
                    "x": products_per[invoice_col].tolist(),
                    "y": products_per['num_products'].tolist(),
                    "type": "bar",
                    "marker": {"color": "#20B2AA"}
                },
                "layout": {
                    "title": "Number of Products per Invoice",
                    "xaxis": {"title": "Invoice ID"},
                    "yaxis": {"title": "Products Count"},
                    "template": "plotly_white"
                }
            }
        except Exception as e:
            logger.error(f"Error creating products per invoice: {e}")
            return None
