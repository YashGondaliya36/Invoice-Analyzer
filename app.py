import os
from PIL import Image
import streamlit as st
import pandas as pd
from src.analytics_report import process_and_generate_brief_report
from src.dataframe_builder import process_invoices_and_store_data
from src.graph_builder import make_visualizations
from IA_Logger import logger

# Set up a 'local database' folder
if not os.path.exists('local_database'):
    os.makedirs('local_database')

# Streamlit UI
st.title("Invoice Analyzer")
st.write("Upload multiple JPG files to analyze invoices.")

# File uploader for multiple files
uploaded_files = st.file_uploader("Choose JPG files", type=["jpg"], accept_multiple_files=True)

# Store all images first
saved_file_paths = []

if uploaded_files:
    try:
        for uploaded_file in uploaded_files:
            # Read the image
            img = Image.open(uploaded_file)
            
            # Save the image in the 'local database' folder
            file_path = os.path.join('local_database', uploaded_file.name)
            img.save(file_path)
            saved_file_paths.append(file_path)

        # Show a success message
        st.success(f"{len(uploaded_files)} file(s) uploaded and saved successfully.")
    
    except Exception as e:
        st.error(f"Error during file upload: {e}")
        logger.error(f"Error during file upload: {e}")

# Process the saved images and generate CSV
if st.button("Process Images"):
    with st.spinner("Processing images..."):
        try:
            result = process_invoices_and_store_data()
            st.success("Processing complete!")
        except Exception as e:
            st.error(f"Error during processing: {e}")
            logger.error(f"Error during processing: {e}")

dataframe_file  = os.path.join("local_database","invoice_data.csv")

if os.path.exists(dataframe_file):
    # Move the dataframe loading outside the button
    try:
        df = pd.read_csv(dataframe_file)
    
        # Show column selection in sidebar first
        selected_columns = st.sidebar.multiselect(
            "Select columns for analysis:",
            options=df.columns.tolist()
        )

        if st.button("Show dataframe"):
            st.write("Complete Dataframe:")
            st.dataframe(df)

        # Display selected columns if any are chosen
        if selected_columns:
            st.write("Selected Columns Data:")
            st.dataframe(df[selected_columns])
            
            plot = make_visualizations(selected_columns=selected_columns)
    
    except Exception as e:
        st.error(f"Error loading CSV or processing data: {e}")
        logger.error(f"Error loading CSV or processing data: {e}")
else:
    st.write("No Dataframe generated yet.")

def format_title(text):
    """Convert plot filename to display title"""
    return text.replace('.png', '').replace('_', ' ').title()

def load_image(image_path):
    """Safely load an image file"""
    try:
        return Image.open(image_path)
    except Exception as e:
        logger.error(f"Error loading image {image_path}: {e}")
        return None

# Add this where you want to display the plots
plots_dir = os.path.join("local_database", "plots")

if os.path.exists(plots_dir):
    st.write("## Analytics Dashboard")

    # Get all plot files
    plot_files = [f for f in os.listdir(plots_dir) if f.endswith('.png')]
    
    if plot_files:
        col1, col2 = st.columns(2)
        
        for idx, plot_file in enumerate(plot_files):
            plot_path = os.path.join(plots_dir, plot_file)
            
            # Load image using PIL first
            img = load_image(plot_path)
            
            if img:
                with col1 if idx % 2 == 0 else col2:
                    st.write(f"### {format_title(plot_file)}")
                    st.image(img)
            else:
                st.error(f"Could not load {plot_file}")
    else:
        st.write("No plots found in the plots directory.")
else:
    st.write("Plots directory not found.")

if st.button("Generate Report"):
    try:
        report = process_and_generate_brief_report()
        st.success(f"Report generated")
    except Exception as e:
        st.error(f"Error generating the report: {e}")
        logger.error(f"Error generating the report: {e}")

report_file = os.path.join('local_database', 'generated_report.txt')

if os.path.exists(report_file):
    if st.button("Show Report"):
        try:
            with open(report_file, 'r') as file:
                report = file.read()
            st.write("Generated Report:")
            st.markdown(report)  # Display the report in text format
        except Exception as e:
            st.error(f"Error reading the report file: {e}")
            logger.error(f"Error reading the report file: {e}")
    else:
        st.write("No report generated yet.")
