import seaborn as sns
import matplotlib.pyplot as plt
import os
import pandas as pd
from IA_Logger import logger
from config.path_manager import path_manager


def ensure_folder_exists(folder_path):
    """
    Ensure the specified folder exists. Create it if it does not exist.
    
    Args:
        folder_path (str): The path of the folder to check/create.
    
    Returns:
        str: The folder path (created or existing).
    """
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        logger.info(f"Created folder: {folder_path}")
    return folder_path

def find_column(df, possible_names):
    """
    Find a column in the dataframe that matches any of the possible names.
    Returns the first matching column name or None if no match is found.
    """
    for name in possible_names:
        matches = [col for col in df.columns if name.lower() in col.lower()]
        if matches:
            return matches[0]
    return None

def plot_amount_boxplot(df, amount_col, save_dir, saved_plots):
    """Create and save the amount distribution boxplot."""
    try:
        sns.boxplot(y=df[amount_col], color="peachpuff", fliersize=4)
        plt.title('Amount Distribution', fontsize=14)
        plt.ylabel('Amount', fontsize=12)
        plt.tight_layout()
        plot_path = os.path.join(save_dir, '1.amount_boxplot.png')
        plt.savefig(plot_path)
        plt.close()
        saved_plots['1.amount_boxplot'] = plot_path
        logger.info(f"Successfully created amount boxplot: {plot_path}")
    except Exception as e:
        logger.error(f"Error in amount boxplot: {e}")


def plot_quantity_boxplot(df, quantity_col, save_dir, saved_plots):
    """Create and save the quantity distribution boxplot."""
    try:
        plt.figure()
        sns.boxplot(x=df[quantity_col], color='green')
        plt.title('Quantity Boxplot')
        plt.tight_layout()
        plot_path = os.path.join(save_dir, '2.quantity_boxplot.png')
        plt.savefig(plot_path)
        plt.close()
        saved_plots['2.quantity_boxplot'] = plot_path
        logger.info(f"Successfully created quantity boxplot: {plot_path}")
    except Exception as e:
        logger.error(f"Error in quantity boxplot: {e}")


def plot_product_sales(df, product_col, amount_col, save_dir, saved_plots):
    """Create and save a barplot for sales by product."""
    try:
        product_sales = df.groupby(product_col)[amount_col].sum().sort_values(ascending=True)
        plt.figure(figsize=(12, max(6, len(product_sales) * 0.3)))
        product_sales.plot(kind='barh', color=plt.cm.rainbow(range(len(product_sales))))
        plt.title('Sales by Product')
        plt.xlabel('Total Sales Amount')
        plt.tight_layout()
        plot_path = os.path.join(save_dir, '3.product_sales.png')
        plt.savefig(plot_path)
        plt.close()
        saved_plots['3.product_sales'] = plot_path
        logger.info(f"Successfully created barplot between product and amount: {plot_path}")
    except Exception as e:
        logger.error(f"Error in barplot between product and amount: {e}")


def plot_quantity_analysis(df, product_col, quantity_col, save_dir, saved_plots):
    """Create and save a barplot for quantity sold by product."""
    try:
        qty_by_product = df.groupby(product_col)[quantity_col].sum().sort_values(ascending=True)
        plt.figure(figsize=(12, max(6, len(qty_by_product) * 0.3)))
        qty_by_product.plot(kind='barh', color=sns.color_palette("rainbow", len(qty_by_product)))
        plt.title('Quantity Sold by Product')
        plt.xlabel('Total Quantity')
        plt.tight_layout()
        plot_path = os.path.join(save_dir, '4.quantity_analysis.png')
        plt.savefig(plot_path)
        plt.close()
        saved_plots['4.quantity_analysis'] = plot_path
        logger.info(f"Successfully created barplot between product and quantity: {plot_path}")
    except Exception as e:
        logger.error(f"Error in barplot between product and quantity: {e}")

def plot_daily_sales(df, date_col, amount_col, save_dir, saved_plots):
    """Create and save a line plot for daily sales analysis."""
    try:
        df[date_col] = pd.to_datetime(df[date_col], format='mixed', dayfirst=True)
        daily_sls = df.groupby(df[date_col].dt.date)[amount_col].sum().reset_index()
        plt.figure(figsize=(12, 6))
        plt.plot(daily_sls[date_col], daily_sls[amount_col], marker='o', color='deeppink')
        plt.title('Daily Sales Analysis')
        plt.xlabel('Date')
        plt.ylabel('Total Sales')
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.tight_layout()
        plot_path = os.path.join(save_dir, '5.daily_sales.png')
        plt.savefig(plot_path)
        plt.close()
        saved_plots['5.daily_sales'] = plot_path
        logger.info(f"Successfully created lineplot for daily sales: {plot_path}")
    except Exception as e:
        logger.error(f"Error in lineplot for daily sales: {e}")


def make_visualizations(selected_columns, save_dir=None):
    """
    Orchestrator to create and save visualizations for invoice data based on selected columns.
    """
    logger.info("Starting visualization generation")

    # Use path_manager to get paths and ensure directory exists
    save_dir = save_dir or path_manager.plotted_graphs
    ensure_folder_exists(save_dir)
    
    # Read the DataFrame from local storage
    try:
        df = pd.read_csv(path_manager.invoice_data)
    except Exception as e:
        logger.error(f"Error reading CSV file: {e}")
        return {}

    

    saved_plots = {}
    sns.set_style("whitegrid")
    plt.rcParams['figure.figsize'] = (12, 6)

    # Filter columns based on selection
    df_selected = df[selected_columns]

    # Identify column types based on selected columns
    date_col = find_column(df_selected, ['date', 'invoice date', 'bill date'])
    product_col = find_column(df_selected, ['product', 'item', 'description', 'product name'])
    amount_col = find_column(df_selected, ['amount', 'total', 'value'])
    quantity_col = find_column(df_selected, ['qty', 'quantity', 'units'])

    # Generate only plots for selected columns
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

    return saved_plots