import os
from PIL import Image
import streamlit as st
from src.dataframe_builder import process_invoices_and_store_data
from src.analytics_report import process_and_generate_brief_report
from IA_Logger import logger
from config.path_manager import path_manager


# Page configuration
st.set_page_config(
    page_title="Insight Invoices",
    page_icon="🌟",
    layout="wide"
)
# Set up a 'local database' folder
if not os.path.exists('local_database'):
    os.makedirs('local_database')

st.subheader("📤 Upload & Process Invoices",divider='gray')

# File uploader for multiple files
uploaded_files = st.file_uploader("Choose JPG files", type=["jpg"], accept_multiple_files=True)

if uploaded_files:
    try:
        for uploaded_file in uploaded_files:
            img = Image.open(uploaded_file)
            file_path = os.path.join('local_database', uploaded_file.name)
            img.save(file_path)
        st.success(f"{len(uploaded_files)} file(s) uploaded successfully.")
    except Exception as e:
        st.error(f"Error during file upload: {e}")
        logger.error(f"Error during file upload: {e}")

# Header: Invoice Processing Section
st.subheader("🛠️ Process Uploaded Invoices",divider='gray')

# Button for Processing Invoices
if st.button("Process Invoices"):
    with st.spinner("Processing invoices..."):
        try:
            # Process invoices
            result = process_invoices_and_store_data()
            st.success("Invoices processed successfully!")
        except Exception as e:
            st.error(f"Error during invoice processing: {e}")
            logger.error(f"Error during invoice processing: {e}")

# Header: Report Generation Section
st.subheader("📊 Generate Analytics Report",divider='gray')

# Button for Generating Report
if st.button("Generate Report"):
    with st.spinner("Generating report..."):
        try:
            # Generate Report
            report = process_and_generate_brief_report()
            
            # Show Report
            with open(path_manager.analytic_report, 'r') as file:
                report_text = file.read()
            st.subheader("Generated Report:")
            st.markdown(report_text)
            st.success("Report generated successfully! Go to Visual Trends page for detailed analysis.")
        except Exception as e:
            st.error(f"Error during report generation: {e}")
            logger.error(f"Error during report generation: {e}")
