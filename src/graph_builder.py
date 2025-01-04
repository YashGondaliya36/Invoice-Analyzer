import plotly.express as px
import pandas as pd
import os
from IA_Logger import logger
from config.path_manager import path_manager

def find_column(df, possible_names):
    """
    Find a column in the dataframe that matches any of the possible names.
    """
    for name in possible_names:
        matches = [col for col in df.columns if name.lower() in col.lower()]
        if matches:
            return matches[0]
    return None

def plot_amount_boxplot(df, amount_col):
    """Create interactive amount distribution boxplot."""
    try:
        fig = px.box(df, y=amount_col, title='Amount Distribution', 
                     color_discrete_sequence=["#636EFA"])
        fig.update_layout(
            title_font_size=16,
            yaxis_title_font_size=14,
            showlegend=False,
            template='plotly_white'
        )
        return fig
    except Exception as e:
        logger.error(f"Error in amount boxplot: {e}")
        return None

def plot_quantity_boxplot(df, quantity_col):
    """Create interactive quantity distribution boxplot."""
    try:
        fig = px.box(df, x=quantity_col, title='Quantity Boxplot', 
                     color_discrete_sequence=["#FF6347"])
        fig.update_layout(
            title_font_size=16,
            xaxis_title_font_size=14,
            showlegend=False,
            template='plotly_white'
        )
        return fig
    except Exception as e:
        logger.error(f"Error in quantity boxplot: {e}")
        return None

def plot_product_sales(df, product_col, amount_col):
    """Create interactive barplot for sales by product."""
    try:
        product_sales = df.groupby(product_col)[amount_col].sum().reset_index()
        fig = px.bar(
            product_sales,
            x=amount_col,
            y=product_col,
            title='Sales by Product',
            orientation='h',
            color=amount_col,
            color_continuous_scale='Viridis'
        )
        fig.update_layout(
            xaxis_title='Total Sales Amount',
            height=max(600, len(product_sales) * 30),
            template='plotly_white'
        )
        return fig
    except Exception as e:
        logger.error(f"Error in barplot between product and amount: {e}")
        return None

def plot_quantity_analysis(df, product_col, quantity_col):
    """Create interactive barplot for quantity sold by product."""
    try:
        qty_by_product = df.groupby(product_col)[quantity_col].sum().reset_index()
        fig = px.bar(
            qty_by_product,
            x=quantity_col,
            y=product_col,
            title='Quantity Sold by Product',
            orientation='h',
            color=quantity_col,
            color_continuous_scale='Cividis'
        )
        fig.update_layout(
            xaxis_title='Total Quantity',
            height=max(600, len(qty_by_product) * 30),
            template='plotly_white'
        )
        return fig
    except Exception as e:
        logger.error(f"Error in barplot between product and quantity: {e}")
        return None

def plot_daily_sales(df, date_col, amount_col):
    """Create interactive line plot for daily sales analysis."""
    try:
        df[date_col] = pd.to_datetime(df[date_col], format='mixed', dayfirst=True)
        daily_sales = df.groupby(df[date_col].dt.date)[amount_col].sum().reset_index()
        fig = px.line(
            daily_sales,
            x=date_col,
            y=amount_col,
            title='Daily Sales Analysis',
            markers=True,
            line_shape='linear'
        )
        fig.update_layout(
            xaxis_title='Date',
            yaxis_title='Total Sales',
            template='plotly_white',
            plot_bgcolor='rgba(0,0,0,0.1)',
            font=dict(color="black")
        )
        return fig
    except Exception as e:
        logger.error(f"Error in lineplot for daily sales: {e}")
        return None

def plot_invoice_trends(df, invoice_col, date_col):
    """Create interactive analysis of invoice patterns over time."""
    try:
        df[date_col] = pd.to_datetime(df[date_col], format='mixed', dayfirst=True)
        daily_invoices = df.groupby(df[date_col].dt.date)[invoice_col].nunique().reset_index()
        
        fig = px.line(
            daily_invoices,
            x=date_col,
            y=invoice_col,
            title='Daily Invoice Count',
            markers=True,
            line_shape='spline',
            color_discrete_sequence=["#FF69B4"]
        )
        
        
        fig.update_layout(
            xaxis_title='Date',
            yaxis_title='Number of Invoices',
            template='plotly_white',
            yaxis=dict(
                tickmode='linear',  
                tick0=0,           
                dtick=1,           
                rangemode='nonnegative',  
                tickformat='d'     
            )
        )
        
        return fig
    except Exception as e:
        logger.error(f"Error in invoice trends plot: {e}")
        return None
    

def plot_invoice_products(df, invoice_col, product_col):
    """Create interactive analysis of products per invoice."""
    try:
        products_per_invoice = df.groupby(invoice_col)[product_col].nunique().reset_index()
        products_per_invoice.columns = [invoice_col, 'num_products']
        
        fig = px.bar(
            products_per_invoice,
            x=invoice_col,  
            y='num_products',  
            title='Number of Products per Invoice',
            labels={
                invoice_col: 'Invoice ID',  
                'num_products': 'Number of Products'  
            },
            color_discrete_sequence=["#20B2AA"]
        )

        fig.update_layout(
            xaxis_title='Invoice ID',
            yaxis_title='Products per Invoice',
            template='plotly_white',
            xaxis=dict(
                tickmode='linear',
                tick0=1,
                dtick=1,
                rangemode='nonnegative',
                tickformat='d'
            )
        )

        return fig
    except Exception as e:
        logger.error(f"Error in products per invoice plot: {e}")
        return None

def plot_monthly_revenue_trend(df, date_col, amount_col):
    try:
        df[date_col] = pd.to_datetime(df[date_col], format='mixed', dayfirst=True)
        monthly_revenue = df.groupby(df[date_col].dt.strftime('%Y-%m'))[amount_col].sum().reset_index()
        
        fig = px.bar(
            monthly_revenue,
            x=date_col,
            y=amount_col,
            title='Monthly Revenue Analysis',
            color=amount_col,
            color_continuous_scale='Viridis'
        )
        fig.update_layout(
            xaxis_title='Month',
            yaxis_title='Total Revenue',
            template='plotly_white',
            yaxis=dict(rangemode='nonnegative')
        )
        return fig
    except Exception as e:
        logger.error(f"Error in monthly revenue trend: {e}")
        return None

def plot_top_products_pareto(df, product_col, amount_col):
    try:
        product_sales = df.groupby(product_col)[amount_col].sum().sort_values(ascending=False).reset_index()
        product_sales['cumulative_percentage'] = (product_sales[amount_col].cumsum() / product_sales[amount_col].sum() * 100)
        
        fig = px.bar(
            product_sales.head(10),
            x=product_col,
            y=amount_col,
            title='Top 10 Products by Revenue with Pareto Line',
            color=amount_col,
            color_continuous_scale='Viridis'
        )
        
        fig.add_scatter(
            x=product_sales.head(10)[product_col],
            y=product_sales.head(10)['cumulative_percentage'],
            mode='lines+markers',
            name='Cumulative %',
            yaxis='y2'
        )
        
        fig.update_layout(
            xaxis_title='Product',
            yaxis_title='Revenue',
            yaxis2=dict(
                title='Cumulative Percentage',
                overlaying='y',
                side='right',
                range=[0, 100]
            ),
            template='plotly_white',
            showlegend=True
        )
        return fig
    except Exception as e:
        logger.error(f"Error in top products pareto: {e}")
        return None

def plot_weekday_analysis(df, date_col, amount_col):
    try:
        df[date_col] = pd.to_datetime(df[date_col], format='mixed', dayfirst=True)
        df['weekday'] = df[date_col].dt.day_name()
        weekday_sales = df.groupby('weekday')[amount_col].agg(['sum']).reset_index()
        weekday_sales.columns = ['weekday', 'total_sales']
        
        fig = px.bar(
            weekday_sales,
            x='weekday',
            y='total_sales',
            title='Sales by Weekday',
            barmode='group'
        )
        
        fig.update_layout(
            xaxis_title='Day of Week',
            yaxis_title='Value',
            template='plotly_white',
            yaxis=dict(rangemode='nonnegative'),
            showlegend=True
        )
        return fig
    except Exception as e:
        logger.error(f"Error in weekday analysis: {e}")
        return None


def make_visualizations(selected_columns):
    """
    Create interactive visualizations for invoice data based on selected columns.
    Returns a dictionary of Plotly figures.
    """
    logger.info("Starting visualization generation")
    
    try:
        df = pd.read_csv(path_manager.invoice_data)
    except Exception as e:
        logger.error(f"Error reading CSV file: {e}")
        return {}

    plots = {}
    df_selected = df[selected_columns]

    # Column identification
    date_col = find_column(df_selected, ['date', 'invoice date', 'bill date'])
    product_col = find_column(df_selected, ['product', 'item', 'description', 'product name'])
    amount_col = find_column(df_selected, ['amount', 'total', 'value'])
    quantity_col = find_column(df_selected, ['qty', 'quantity', 'units'])
    invoice_col = find_column(df_selected, ['invoice', 'invoice number', 'invoice no', 'bill number'])

    # Generate plots
    if amount_col and amount_col in selected_columns:
        plots['amount_boxplot'] = plot_amount_boxplot(df_selected, amount_col)
    
    if quantity_col and quantity_col in selected_columns:
        plots['quantity_boxplot'] = plot_quantity_boxplot(df_selected, quantity_col)
    
    if product_col and amount_col and all(col in selected_columns for col in [product_col, amount_col]):
        plots['product_sales'] = plot_product_sales(df_selected, product_col, amount_col)
        plots['top_products_pareto'] = plot_top_products_pareto(df_selected, product_col, amount_col)
    
    if product_col and quantity_col and all(col in selected_columns for col in [product_col, quantity_col]):
        plots['quantity_analysis'] = plot_quantity_analysis(df_selected, product_col, quantity_col)
    
    if date_col and amount_col and all(col in selected_columns for col in [date_col, amount_col]):
        plots['daily_sales'] = plot_daily_sales(df_selected, date_col, amount_col)
        plots['monthly_revenue'] = plot_monthly_revenue_trend(df_selected, date_col, amount_col)
        plots['weekday_analysis'] = plot_weekday_analysis(df_selected, date_col, amount_col)
    
    if invoice_col and date_col and all(col in selected_columns for col in [invoice_col, date_col]):
        plots['invoice_trends'] = plot_invoice_trends(df_selected, invoice_col, date_col)
        
    if invoice_col and product_col and all(col in selected_columns for col in [invoice_col, product_col]):
        plots['invoice_products'] = plot_invoice_products(df_selected, invoice_col, product_col)
        

    return plots