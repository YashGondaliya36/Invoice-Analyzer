import os
from PIL import Image
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def process_and_generate_brief_report():
    # Set up the 'local_database' folder if it doesn't exist
    if not os.path.exists('local_database'):
        os.makedirs('local_database')

    # Ensure the API key is set in the environment
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return "API key not found. Please set the GOOGLE_API_KEY in your environment."

    # Choose a Gemini model
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    

    # Read all the .jpg files in the 'local_database' folder
    image_parts = []
    for filename in os.listdir('local_database'):
        if filename.endswith(".jpg"):
            file_path = os.path.join('local_database', filename)
            # Create image part for Gemini
            image = Image.open(file_path)
            image_parts.append(image)

    if not image_parts:
        return "No image files found in 'local_database' folder."

    # Create a simplified prompt for the Gemini model
    prompt = '''You are an analyst reviewing a set of invoices. Based on the invoices, provide a brief report about:
    - The spending trends
    - Any notable KPIs
    - Insights into product or service usage.'''

    # Generate the brief report using Gemini model
    response = model.generate_content([prompt] + image_parts)

       # Save the response in a text file in the 'local_database' folder
    report_filename = os.path.join('local_database', 'generated_report.txt')
    with open(report_filename, 'w', encoding='utf-8') as report_file:
        report_file.write(response.text)

    # Return the path to the saved report
    return f"Report has been saved to {report_filename}"
