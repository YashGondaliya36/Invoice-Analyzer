import streamlit as st
import os
from PIL import Image

# Set up a 'local database' folder
if not os.path.exists('local_database'):
    os.makedirs('local_database')

# Streamlit UI
st.title("Invoice Analyzer")
st.write("Upload multiple JPG files to analyze invoices.")

# File uploader for multiple files
uploaded_files = st.file_uploader("Choose JPG files", type=["jpg", "jpeg"], accept_multiple_files=True)

# Store all images first
saved_file_paths = []

if uploaded_files:
    for uploaded_file in uploaded_files:
        # Read the image
        img = Image.open(uploaded_file)
        
        # Save the image in the 'local database' folder
        file_path = os.path.join('local_database', uploaded_file.name)
        img.save(file_path)
        saved_file_paths.append(file_path)

    # Show a success message
    st.success(f"{len(uploaded_files)} file(s) uploaded and saved successfully.")
