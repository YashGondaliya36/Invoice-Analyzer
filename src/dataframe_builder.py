import os
import json
import pandas as pd
from PIL import Image
import google.generativeai as genai
from dotenv import load_dotenv
from IA_Logger import logger
from config.path_manager import path_manager

load_dotenv()

def ensure_local_database_folder():
    """Ensure the 'local_database' folder exists."""
    local_database_folder = "local_database"
    if not os.path.exists(local_database_folder):
        os.makedirs(local_database_folder)
        logger.info(f"Created folder: {local_database_folder}")
    return local_database_folder

def configure_gemini_api():
    """Configure the Gemini API with the API key from environment variables."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        error_msg = "Error: API key not found. Please set the GOOGLE_API_KEY in your environment."
        logger.error(error_msg)
        raise ValueError(error_msg)

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name="gemini-2.5-flash-lite")
        logger.info("Gemini API configured successfully.")
        return model
    except Exception as e:
        error_msg = f"Error configuring Gemini API: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)

def load_images_from_folder(folder_path):
    """Load all .jpg and .jpeg images from the specified folder."""
    image_parts = []
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('.jpg', '.jpeg')):
            file_path = os.path.join(folder_path, filename)
            try:
                image = Image.open(file_path)
                image_parts.append(image)
                logger.info(f"Loaded image: {filename}")
            except Exception as e:
                logger.warning(f"Error reading image {filename}: {str(e)}")

    if not image_parts:
        error_msg = "Error: No valid image files found in the folder."
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)

    return image_parts

def process_invoices_with_gemini(model, images):
    """Send images and prompt to the Gemini model and get the structured response."""
    prompt = '''
    Now be serious. I have given you various images of invoices. Your task is to extract all the information from the invoices
    and give me the structured output like the below example. Make sure you use entities that are common in all the invoices.

    1. Required Fields (Use exact field names):
    - "Invoice No" - Extract invoice number/reference exactly as shown
    - "Product Name" - Include full product description 
    - "Qty" - Convert all quantities to numbers only
    - "Amount" - Extract as number only (no currency symbols)
    - "Date" - Convert all dates to DD-MM-YY format

    2. Quality Control Steps:
    - Double-check all extracted values against original
    - Verify no data was missed or incorrectly parsed
    - Ensure numbers make mathematical sense
    - Confirm date is logically valid
    - Verify invoice number format is consistent
    - ex. Qty : 20.00 -> 20 (keep only integer value)
          amount : 3000.3500 -> 3000.35(keep two digit after .)


    Example of structured response:
    [
        {"Invoice No": "INV001", "Product Name": "Pipe A", "Qty": 25, "Amount": 3593.10, "Date": "2025-01-01"},
        {"Invoice No": "INV002", "Product Name": "Pipe B", "Qty": 50, "Amount": 3849.76, "Date": "2025-01-02"}
    ]
    '''

    try:
        logger.info("Sending prompt and images to Gemini model.")
        response = model.generate_content([prompt, *images])
        response_text = response.text

        # Clean up the response text to ensure valid JSON
        response_text = response_text.replace("```json", "").replace("```", "").strip()
        start_idx = response_text.find('[')
        end_idx = response_text.rfind(']')
        if start_idx != -1 and end_idx != -1:
            response_text = response_text[start_idx:end_idx + 1]

        logger.info("Received response from Gemini model.")
        return response_text
    except Exception as e:
        error_msg = f"Error during Gemini model processing: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)

def parse_response_to_json(response_text):
    """Parse the Gemini model response into JSON format."""
    try:
        structured_data = json.loads(response_text)
        logger.info("Response successfully parsed as JSON.")
        return structured_data
    except json.JSONDecodeError as e:
        error_msg = f"Error parsing response as JSON: {str(e)}\nResponse Text: {response_text}"
        logger.error(error_msg)
        raise ValueError(error_msg)

def save_data_to_csv(data, folder_path):
    """Save the structured data to a CSV file in the specified folder."""
    csv_file_path = path_manager.invoice_data
    try:
        df = pd.DataFrame(data)
        df.to_csv(csv_file_path, index=False)
        logger.info(f"Structured data successfully saved to {csv_file_path}.")
        return csv_file_path
    except Exception as e:
        error_msg = f"Error saving DataFrame to CSV: {str(e)}"
        logger.error(error_msg)
        raise IOError(error_msg)

def process_invoices_and_store_data():
    """
    Main function to process invoice images and save structured data.
    """
    logger.info("Starting invoice processing pipeline.")
    try:
        local_database_folder = ensure_local_database_folder()
        model = configure_gemini_api()
        images = load_images_from_folder(local_database_folder)
        response_text = process_invoices_with_gemini(model, images)
        structured_data = parse_response_to_json(response_text)
        csv_file_path = save_data_to_csv(structured_data, local_database_folder)
        logger.info("Invoice processing pipeline completed successfully.")
        return f"Structured data successfully saved to {csv_file_path}"
    except Exception as e:
        logger.error(f"Invoice processing pipeline failed: {str(e)}")
        return f"Error: {str(e)}"
