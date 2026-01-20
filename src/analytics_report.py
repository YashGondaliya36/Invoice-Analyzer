import os
from PIL import Image
import google.generativeai as genai
from dotenv import load_dotenv
from IA_Logger import logger
from config.path_manager import path_manager

# Load environment variables from .env file
load_dotenv()

def ensure_local_database_folder():
    """Ensure the 'local_database' folder exists."""
    local_database_folder = "local_database"
    if not os.path.exists(local_database_folder):
        os.makedirs(local_database_folder)
        logger.info(f"Created folder: {local_database_folder}")
    return local_database_folder

# Function to read all .jpg images from the 'local_database' folder
def load_images_from_local_database():
    image_parts = []
    for filename in os.listdir('local_database'):
        if filename.endswith(".jpg"):
            file_path = os.path.join('local_database', filename)
            try:
                image = Image.open(file_path)
                image_parts.append(image)
                logger.info(f"Image {filename} loaded successfully.")
            except Exception as e:
                logger.error(f"Failed to load image {filename}: {e}")
    if not image_parts:
        logger.warning("No image files found in 'local_database' folder.")
    return image_parts

# Function to generate a brief report using Gemini API
def generate_report(model, images):
    prompt = '''You are a financial analyst tasked with reviewing a dataset of invoices. Based on the provided data, create a detailed and structured report covering the following aspects:

            Spending Trends:

                Summarize the overall spending patterns, including total spending, average spending per invoice, and spending fluctuations over time.
                Highlight the top spending periods (e.g., months, quarters, or years).
                Identify categories, vendors, or clients contributing the most to spending.

            Key Performance Indicators (KPIs):

                Analyze the total number of invoices and the average number of items per invoice.
                Highlight high-value invoices (e.g., those exceeding a specific threshold).
                Report on vendor/client contributions to spending or revenue 

            Product or Service Usage Insights:

                Identify the most frequently purchased products or services and their revenue contributions.
                Highlight any underutilized or low-demand products/services.
                Note trends in product/service usage (e.g., increasing or decreasing demand).
                Rank the top product/service categories based on sales volume or revenue.

            Actionable Insights:

                Provide recommendations for optimizing spending, improving product/service utilization, or addressing any identified issues."
                Additional Instructions:
                Format the report with clear sections and bullet points for readability.
                Use quantitative metrics and percentages wherever possible.
                Ensure insights are actionable and backed by data trends.
                '''
    
    try:
        response = model.generate_content([prompt] + images)
        logger.info("Report generated successfully.")
        return response.text
    except Exception as e:
        logger.error(f"Failed to generate report: {e}")
        return None

# Function to save the report to a text file
def save_report_to_file(report_text):
    report_filename = path_manager.analytic_report
    try:
        with open(report_filename, 'w', encoding='utf-8') as report_file:
            report_file.write(report_text)
        logger.info(f"Report saved to {report_filename}.")
        return report_filename
    except Exception as e:
        logger.error(f"Failed to save report to file: {e}")
        return None

# Main function to process the images and generate the brief report
def process_and_generate_brief_report():
    
    ensure_local_database_folder()

    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        logger.error("API key not found. Please set the GOOGLE_API_KEY in your environment.")
        return "API key not found. Please set the GOOGLE_API_KEY in your environment."
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name="gemini-2.0-flash-exp")
    
    images = load_images_from_local_database()
    if not images:
        return "No image files found in 'local_database' folder."

    report_text = generate_report(model, images)
    if not report_text:
        return "Failed to generate the report."

    report_filename = save_report_to_file(report_text)
    if report_filename:
        return f"Report has been saved to {report_filename}"
    return "Failed to save the report."
