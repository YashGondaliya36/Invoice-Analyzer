import plotly.express as px
import pandas as pd
import os
from IA_Logger import logger
from config.path_manager import path_manager

def ensure_folder_exists(folder_path):
    """
    Ensure the specified folder exists. Create it if it does not exist.
    """
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        logger.info(f"Created folder: {folder_path}")
    return folder_path

def find_column(df, possible_names):
    """
    Find a column in the dataframe that matches any of the possible names.
    """
    for name in possible_names:
        matches = [col for col in df.columns if name.lower() in col.lower()]
        if matches:
            return matches[0]
    return None

def plot_amount_boxplot(df, amount_col, save_dir, saved_plots):
    """Create and save the amount distribution boxplot."""
    try:
        fig = px.box(df, y=amount_col, title='Amount Distribution', 
                     color_discrete_sequence=["#636EFA"])
        fig.update_layout(
            title_font_size=16,
            yaxis_title_font_size=14,
            showlegend=False,
            template='plotly_white'
        )
        plot_path = os.path.join(save_dir, '1.amount_boxplot.png')
        fig.write_image(plot_path)
        saved_plots['1.amount_boxplot'] = plot_path
        logger.info(f"Successfully created amount boxplot: {plot_path}")
    except Exception as e:
        logger.error(f"Error in amount boxplot: {e}")

def plot_quantity_boxplot(df, quantity_col, save_dir, saved_plots):
    """Create and save the quantity distribution boxplot."""
    try:
        fig = px.box(df, x=quantity_col, title='Quantity Boxplot', 
                     color_discrete_sequence=["#FF6347"])
        fig.update_layout(
            title_font_size=16,
            xaxis_title_font_size=14,
            showlegend=False,
            template='plotly_white'
        )
        plot_path = os.path.join(save_dir, '2.quantity_boxplot.png')
        fig.write_image(plot_path)
        saved_plots['2.quantity_boxplot'] = plot_path
        logger.info(f"Successfully created quantity boxplot: {plot_path}")
    except Exception as e:
        logger.error(f"Error in quantity boxplot: {e}")

def plot_product_sales(df, product_col, amount_col, save_dir, saved_plots):
    """Create and save a barplot for sales by product."""
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
        plot_path = os.path.join(save_dir, '3.product_sales.png')
        fig.write_image(plot_path)
        saved_plots['3.product_sales'] = plot_path
        logger.info(f"Successfully created barplot between product and amount: {plot_path}")
    except Exception as e:
        logger.error(f"Error in barplot between product and amount: {e}")

def plot_quantity_analysis(df, product_col, quantity_col, save_dir, saved_plots):
    """Create and save a barplot for quantity sold by product."""
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
        plot_path = os.path.join(save_dir, '4.quantity_analysis.png')
        fig.write_image(plot_path)
        saved_plots['4.quantity_analysis'] = plot_path
        logger.info(f"Successfully created barplot between product and quantity: {plot_path}")
    except Exception as e:
        logger.error(f"Error in barplot between product and quantity: {e}")

def plot_daily_sales(df, date_col, amount_col, save_dir, saved_plots):
    """Create and save a line plot for daily sales analysis."""
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
        plot_path = os.path.join(save_dir, '5.daily_sales.png')
        fig.write_image(plot_path)
        saved_plots['5.daily_sales'] = plot_path
        logger.info(f"Successfully created lineplot for daily sales: {plot_path}")
    except Exception as e:
        logger.error(f"Error in lineplot for daily sales: {e}")

def plot_invoice_trends(df, invoice_col, date_col, save_dir, saved_plots):
    """Create and save analysis of invoice patterns over time."""
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
            template='plotly_white'
        )
        plot_path = os.path.join(save_dir, '6.invoice_trends.png')
        fig.write_image(plot_path)
        saved_plots['6.invoice_trends'] = plot_path
        logger.info(f"Successfully created invoice trends plot: {plot_path}")
    except Exception as e:
        logger.error(f"Error in invoice trends plot: {e}")

def plot_invoice_amount_distribution(df, invoice_col, amount_col, save_dir, saved_plots):
    """Create and save distribution of invoice amounts."""
    try:
        invoice_amounts = df.groupby(invoice_col)[amount_col].sum().reset_index()
        fig = px.histogram(
            invoice_amounts,
            x=amount_col,
            title='Distribution of Invoice Amounts',
            nbins=30,
            color_discrete_sequence=["#32CD32"]
        )
        fig.update_layout(
            xaxis_title='Invoice Amount',
            yaxis_title='Count',
            template='plotly_white'
        )
        plot_path = os.path.join(save_dir, '7.invoice_amount_dist.png')
        fig.write_image(plot_path)
        saved_plots['7.invoice_amount_dist'] = plot_path
        logger.info(f"Successfully created invoice amount distribution plot: {plot_path}")
    except Exception as e:
        logger.error(f"Error in invoice amount distribution plot: {e}")

def plot_invoice_products(df, invoice_col, product_col, save_dir, saved_plots):
    """Create and save analysis of products per invoice."""
    try:
        products_per_invoice = df.groupby(invoice_col)[product_col].nunique().reset_index()
        fig = px.histogram(
            products_per_invoice,
            x=product_col,
            title='Number of Products per Invoice',
            labels={product_col: 'Number of Products'},
            color_discrete_sequence=["#20B2AA"]
        )
        fig.update_layout(
            xaxis_title='Products per Invoice',
            yaxis_title='Number of Invoices',
            template='plotly_white'
        )
        plot_path = os.path.join(save_dir, '8.products_per_invoice.png')
        fig.write_image(plot_path)
        saved_plots['8.products_per_invoice'] = plot_path
        logger.info(f"Successfully created products per invoice plot: {plot_path}")
    except Exception as e:
        logger.error(f"Error in products per invoice plot: {e}")

def make_visualizations(selected_columns, save_dir=None):
    """
    Orchestrator to create and save visualizations for invoice data based on selected columns.
    """
    logger.info("Starting visualization generation")
    
    save_dir = save_dir or path_manager.plotted_graphs
    ensure_folder_exists(save_dir)
    
    try:
        df = pd.read_csv(path_manager.invoice_data)
    except Exception as e:
        logger.error(f"Error reading CSV file: {e}")
        return {}

    saved_plots = {}
    df_selected = df[selected_columns]

    # Column identification
    date_col = find_column(df_selected, ['date', 'invoice date', 'bill date'])
    product_col = find_column(df_selected, ['product', 'item', 'description', 'product name'])
    amount_col = find_column(df_selected, ['amount', 'total', 'value'])
    quantity_col = find_column(df_selected, ['qty', 'quantity', 'units'])
    invoice_col = find_column(df_selected, ['invoice', 'invoice number', 'invoice no','bill number'])

    # Original plots
    if amount_col and amount_col in selected_columns:
        plot_amount_boxplot(df_selected, amount_col, save_dir, saved_plots)
    if quantity_col and quantity_col in selected_columns:
        plot_quantity_boxplot(df_selected, quantity_col, save_dir, saved_plots)
    if product_col and amount_col and all(col in selected_columns for col in [product_col, amount_col]):
        plot_product_sales(df_selected, product_col, amount_col, save_dir, saved_plots)
    if product_col and quantity_col and all(col in selected_columns for col in [product_col, quantity_col]):
        plot_quantity_analysis(df_selected, product_col, quantity_col, save_dir, saved_plots)
    if date_col and amount_col and all(col in selected_columns for col in [date_col, amount_col]):
        plot_daily_sales(df_selected, date_col, amount_col, save_dir, saved_plots)
    if invoice_col and date_col and all(col in selected_columns for col in [invoice_col, date_col]):
        plot_invoice_trends(df_selected, invoice_col, date_col, save_dir, saved_plots)
    if invoice_col and amount_col and all(col in selected_columns for col in [invoice_col, amount_col]):
        plot_invoice_amount_distribution(df_selected, invoice_col, amount_col, save_dir, saved_plots)
    if invoice_col and product_col and all(col in selected_columns for col in [invoice_col, product_col]):
        plot_invoice_products(df_selected, invoice_col, product_col, save_dir, saved_plots)

    return saved_plots
