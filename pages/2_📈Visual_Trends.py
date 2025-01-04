import os
import streamlit as st
import pandas as pd
from src.graph_builder import make_visualizations
from IA_Logger import logger
from config.path_manager import path_manager
import shutil
import atexit

# Page configuration
st.set_page_config(
    page_title="Visual Trends",
    page_icon="📈",
    layout="wide"
)

st.subheader("📈 Visual Analysis",divider='rainbow')

# Register cleanup function to run when the application exits
def cleanup_on_exit():
    try:
        if os.path.exists(path_manager.local_database):
            shutil.rmtree(path_manager.local_database)
            os.makedirs(path_manager.local_database)
            logger.info("Local database cleaned on exit")
    except Exception as e:
        logger.error(f"Error during cleanup on exit: {e}")

atexit.register(cleanup_on_exit)


if os.path.exists(path_manager.invoice_data):
    try:
        # Load and display DataFrame
        df = pd.read_csv(path_manager.invoice_data)
        
        # Column selection in sidebar
        selected_columns = st.sidebar.multiselect(
            "Select columns for analysis:",
            options=df.columns.tolist()
        )

        # Show complete DataFrame button
        if st.button("Show Complete DataFrame"):
            st.write("Complete DataFrame:")
            st.dataframe(df)

        # Show selected columns and generate plots
        if selected_columns:
            st.write("Selected Columns Data:")
            st.dataframe(df[selected_columns])
            
            # Generate visualizations button
            if st.button("Generate Visualizations"):
                plot = make_visualizations(selected_columns=selected_columns)
                st.success("Visualizations generated!")

                # Display plots
                if os.path.exists(path_manager.plotted_graphs):
                    plot_files = [f for f in os.listdir(path_manager.plotted_graphs) if f.endswith('.png')]
                    
                    if plot_files:
                        for plot_file in plot_files:
                            plot_path = os.path.join(path_manager.plotted_graphs, plot_file)
                            try:
                                st.image(plot_path)
                            except Exception as e:
                                st.error(f"Could not load {plot_file}")

        # Cleanup button
        if st.button("Complete Analysis"):
            try:
                cleanup_on_exit()
                st.success("Analysis complete! Local database cleaned.")
            except Exception as e:
                st.error(f"Error during cleanup: {e}")
                logger.error(f"Error during cleanup: {e}")
    
    except Exception as e:
        st.error(f"Error loading CSV or processing data: {e}")
        logger.error(f"Error loading CSV or processing data: {e}")
else:
    st.info("Please upload and process invoices in the Insightful Invoices page first.")