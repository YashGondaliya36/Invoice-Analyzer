# Invoice Analyzer 📊

A powerful tool that processes multiple invoices and generates analytical reports using Google's Gemini AI. This application provides interactive data visualization capabilities through a user-friendly Streamlit interface.

## 🌟 Features

- **Multiple Invoice Processing**: Upload and analyze multiple invoices simultaneously
- **AI-Powered Analysis**: Leverages Google's Gemini AI for intelligent invoice data extraction
- **Smart Visualization**: Automatically generates appropriate graphs based on selected data columns
- **Data Frame Generation**: Automatically converts extracted data into structured format
- **Column-Based Analysis**: Users can select specific data columns to view relevant pre-configured visualizations

## 🛠️ Technologies Used

- **Streamlit**: For creating the web application interface
- **Google Gemini API**: For invoice processing and data extraction
- **Plotly**: Interactive data visualization

## 📋 Prerequisites

- Python 3.7 or higher
- Google Cloud API credentials
- Required Python packages

## ⚙️ Installation

1. Clone the repository:
```bash
git clone https://github.com/YourUsername/Invoice-Analyzer.git
cd Invoice-Analyzer
```

2. Create and activate virtual environment:

For Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

For macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install required dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the root directory and add:
```
GOOGLE_API_KEY=your_api_key_here
```

## 🚀 Usage

1. Activate the virtual environment (if not already activated):

For Windows:
```bash
venv\Scripts\activate
```

For macOS/Linux:
```bash
source venv/bin/activate
```

2. Start the application:
```bash
streamlit run Invoice_Analyzer.py
```

3. Upload Invoices:
   - Click on the upload button
   - Select multiple invoice files
   - Wait for processing

4. Analyze Data:
   - Select a column from the available dropdown menu
   - The application will automatically display relevant pre-configured visualizations for that column
   - Each column has specific graph types associated with it based on the data type and analysis requirements

5. When finished, deactivate the virtual environment:
```bash
deactivate
```

## 📊 Visualization System

The application uses an intelligent visualization system where:
- Each data column has predefined graph types associated with it
- Appropriate visualizations are automatically displayed based on the selected column
- Graphs are pre-configured to best represent the data type of each column
- Users don't need to choose graph types - the system automatically shows the most relevant visualization

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📬 Contact

Your Name - [@Yash Gondaliya](https://www.linkedin.com/in/yash-gondaliya-02427a260)

Project Link: [https://github.com/YashGondaliya36/Invoice-Analyzer](https://github.com/YashGondaliya36/Invoice-Analyzer)