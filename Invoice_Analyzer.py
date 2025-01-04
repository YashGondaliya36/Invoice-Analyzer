import streamlit as st
from time import sleep

# Page configuration
st.set_page_config(
    page_title="Invoice Analyzer",
    page_icon="📊",
    layout="wide"
)

# Title with animation effect
def animated_title():
    title = "📊 Invoice Analyzer"
    with st.empty():
        for i in range(len(title) + 1):
            st.title(title[:i])
            sleep(0.05)

animated_title()

# Welcome section
with st.container():
    st.markdown("### :blue[Welcome to Invoice Analyzer!]")
    st.markdown("This application helps you analyze invoice images using AI and provides detailed insights.")



# Features section with columns
st.header("Key Features 🌟 ",divider='rainbow')
col1, col2 = st.columns(2)

with col1:
    with st.expander("🔄 Upload & Process", expanded=True):
        st.write("""
        - Upload multiple invoice images
        - AI-powered data extraction
        - Automatic data structuring
        - Detailed AI-generated report
        """)

with col2:
    with st.expander("📊 Analysis & Visualization", expanded=True):
        st.write("""
        - Interactive data tables
        - Automated visual analytics
        - Spending pattern analysis
        - Trend identification
        """)


# How to Use section with built-in container
st.header("How to Use 🛠️",divider='rainbow')

# Using success message for light background effect
with st.success(""):
    st.markdown("""
    1. Go to **Insightful Invoices** page
    2. Upload your invoice images (JPG format)
    3. Process the images and view report
    4. Check **Visual Trends** for graphs
    5. After seen Generated graph Click **Complete Anylysis**
    """)


# Note section
with st.container():
    st.warning("**Note:** All data is processed locally and cleaned after analysis for security.")

# Final divider
st.divider()

# Footer
url = "https://www.linkedin.com/in/yash-gondaliya-02427a260/?originalSubdomain=in"
st.markdown("👨‍💻 Made with ❤️ by [Yash Gondaliya](%s)" % url)