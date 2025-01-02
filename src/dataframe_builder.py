import os
import json
import pandas as pd
from PIL import Image
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

def process_invoices_and_store_data():
    """
    Reads invoice images from the 'local_database' folder, processes them using the Gemini model,
    extracts structured data, and saves it as a CSV file in the 'local_database' folder.

    Returns:
        str: Path to the saved CSV file or an error message.
    """
    # Ensure the 'local_database' folder exists
    local_database_folder = "local_database"
    if not os.path.exists(local_database_folder):
        os.makedirs(local_database_folder)

    # Configure the Gemini API
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return "Error: API key not found. Please set the GOOGLE_API_KEY in your environment."

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    except Exception as e:
        return f"Error configuring Gemini API: {str(e)}"

    # Read all .jpg files in the 'local_database' folder
    image_parts = []
    for filename in os.listdir(local_database_folder):
        if filename.lower().endswith(".jpg") or filename.lower().endswith(".jpeg"):
            file_path = os.path.join(local_database_folder, filename)
            try:
                image = Image.open(file_path)
                image_parts.append(image)
            except Exception as e:
                print(f"Error reading image {filename}: {str(e)}")

    if not image_parts:
        return "Error: No valid image files found in the 'local_database' folder."

    # Define the prompt for the Gemini model
    prompt = '''
    Now be serious. I have given you various images of invoices. Your task is to extract all the information from the invoices
    and give me the structured output like the below example. Make sure you use entities that are common in all the invoices.
    Example of structured response:
    [
        {"Invoice No": "INV001", "Product Name": "Pipe A", "Qty": 25, "Amount": 3593.10, "Date": "2025-01-01"},
        {"Invoice No": "INV002", "Product Name": "Pipe B", "Qty": 50, "Amount": 3849.76, "Date": "2025-01-02"}
    ]
    '''

    try:
        response = model.generate_content([prompt, *image_parts])
        response_text = response.text
        
        # Clean up the response text to ensure valid JSON
        # Remove any markdown formatting, quotes, and whitespace
        response_text = response_text.replace("```json", "").replace("```", "").strip()
        
        # Try to find JSON array in the response if it's embedded in other text
        start_idx = response_text.find('[')
        end_idx = response_text.rfind(']')
        if start_idx != -1 and end_idx != -1:
            response_text = response_text[start_idx:end_idx + 1]
            
    except Exception as e:
        return f"Error during Gemini model processing: {str(e)}"
    # Parse the response text as JSON
    try:
        structured_data = json.loads(response_text)
    except json.JSONDecodeError as e:
        return f"Error parsing response as JSON: {str(e)}\nResponse Text: {response_text}"

    # Convert structured data to a DataFrame
    try:
        df = pd.DataFrame(structured_data)
    except ValueError as e:
        return f"Error converting structured data to DataFrame: {str(e)}"

    # Save the DataFrame as a CSV file in the 'local_database' folder
    csv_file_path = os.path.join(local_database_folder, "invoice_data.csv")
    try:
        df.to_csv(csv_file_path, index=False)
    except Exception as e:
        return f"Error saving DataFrame to CSV: {str(e)}"

    return f"Structured data successfully saved to {csv_file_path}"
