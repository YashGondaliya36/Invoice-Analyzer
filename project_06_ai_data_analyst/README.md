# 🧙‍♂️ DataWiz AI - Code-Executing AI Data Analyst

**Upload CSV/Excel → Ask Questions → Get Instant Insights & Visualizations**

An AI-powered data analyst that writes and executes Python code to analyze your data, create beautiful Plotly visualizations, and provide natural language explanations.

---

## ✨ **Features**

### **Core Capabilities** 🚀
- 📊 **Automated Data Analysis** - AI writes Python code to analyze your data
- 📈 **Plotly Visualizations** - Beautiful interactive charts
- 🤖 **Code Execution** - Safe execution environment
- 💬 **Natural Language** - Ask questions in plain English
- 🎨 **Premium UI** - Glassmorphism design with dark theme
- 🔄 **Session Management** - Upload, analyze, reset

### **What It Can Do** 💡
- Calculate statistics (mean, median, sum, etc.)
- Create visualizations (bar, line, scatter, pie charts)
- Find trends and patterns
- Group and aggregate data
- Filter and sort data
- Find correlations
- Generate insights

---

## 🏗️ **Architecture**

```
User Question
    ↓
Gemini generates Python code
    ↓
Code executed safely (pandas + plotly)
    ↓
Results + Visualization
    ↓
Gemini explains results
    ↓
Display to user
```

### **Tech Stack**
- **Backend**: FastAPI
- **AI**: Google Gemini 2.0 Flash (direct, no langchain-google-genai)
- **Data**: Pandas, NumPy
- **Visualization**: Plotly (interactive charts)
- **Frontend**: Vanilla JavaScript
- **UI**: Premium CSS with glassmorphism

---

## 🚀 **Quick Start**

### **1. Prerequisites**
- Python 3.8+
- Google Gemini API key
- Virtual environment (recommended)

### **2. Installation**

```bash
# Navigate to project
cd project_06_ai_data_analyst

# Activate virtual environment (if using)
# Windows:
F:\Data_Science_Project\temp\.venv\Scripts\activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### **3. Configure API Key**

Ensure your parent `.env` file has:
```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

### **4. Run**

```bash
python app.py
```

Open browser: **http://localhost:8000**

---

## 📖 **Usage Guide**

### **Step 1: Upload Data**
1. Click upload area or drag-and-drop
2. Select CSV or Excel file
3. AI loads and analyzes structure

### **Step 2: Ask Questions**
Examples:
- "What are the top 10 items by revenue?"
- "Show me a bar chart of sales by category"
- "Calculate average price per product"
- "Find correlation between price and quantity"
- "Create a line chart showing trends over time"

### **Step 3: Get Results**
- AI generates Python code
- Code executes safely
- Interactive Plotly charts displayed
- Natural language explanation provided

### **Step 4: Explore Further**
- Ask follow-up questions
- Request different visualizations
- Dig deeper into insights

---

## 🎯 **How It Works**

### **Step 1: Code Generation**
```python
User: "Show top 5 products by sales"

Gemini generates:
result = df.groupby('product')['sales'].sum()
         .nlargest(5)
         .reset_index()

fig = px.bar(result, x='product', y='sales', 
            title='Top 5 Products by Sales')
fig.write_html('outputs/chart.html')
```

### **Step 2: Safe Execution**
- Code runs in isolated namespace
- Has access to: pandas, plotly, the dataframe
- No file system access (except outputs/)
- No network access
- No system commands

### **Step 3: Explanation**
```
Gemini explains results in plain English:
"The analysis shows Product A leads with $50,000 in sales,
followed by Product B at $42,000..."
```

---

## 📊 **Visualization Examples**

All charts are created with **Plotly only**:
- Bar charts (`plotly.express.bar`)
- Line charts (`plotly.express.line`)
- Scatter plots (`plotly.express.scatter`)
- Pie charts (`plotly.express.pie`)
- Histograms (`plotly.express.histogram`)
- Box plots (`plotly.express.box`)

---

## 🛠️ **Project Structure**

```
project_06_ai_data_analyst/
├── app.py                 # FastAPI backend
├── ai_agent.py            # AI agent (code generation & execution)
├── requirements.txt       # Dependencies
├── .gitignore            # Git ignore rules
├── templates/
│   └── index.html        # Main UI
├── static/
│   ├── css/
│   │   └── style.css     # Premium design
│   └── js/
│       └── app.js        # Frontend logic
├── uploads/              # User uploaded files
└── outputs/              # Generated charts
```

---

## 🔒 **Security**

### **Safe Code Execution**
- ✅ Isolated namespace (no access to imports like `os`, `sys`)
- ✅ No file operations (except writing charts)
- ✅ No network access
- ✅ No shell commands
- ✅ Input validation

### **Data Privacy**
- ✅ Files stored locally only
- ✅ No data sent to external services (except Gemini for code generation)
- ✅ Session-based (no database)

---

## 🎨 **UI Highlights**

- **Glassmorphism Design** - Modern, premium look
- **Animated Background** - Floating gradient orbs
- **Dark Theme** - Easy on the eyes
- **Smooth Animations** - Polished interactions
- **Responsive** - Works on all devices
- **Drag & Drop** - Easy file upload
- **Code Viewer** - See generated Python code
- **Interactive Charts** - Plotly visualizations

---

## 🐛 **Troubleshooting**

### **Import Error: google.generativeai**
```bash
pip install --upgrade google-generativeai
```

### **Charts Not Showing**
- Check `outputs/` folder permissions
- Ensure Plotly is installed: `pip install plotly kaleido`

### **API Key Error**
- Verify `.env` file in parent directory
- Check `GOOGLE_API_KEY` is set correctly

---

## 📚 **Example Questions**

### **Basic Analysis**
- "What's the average price?"
- "Count rows by category"
- "Find maximum sales value"

### **Grouping & Aggregation**
- "Group by region and sum revenue"
- "Average rating by product type"
- "Count orders per customer"

### **Visualizations**
- "Create a bar chart of top 10 cities"
- "Show line chart of monthly trends"
- "Make a pie chart of category distribution"

### **Advanced**
- "Find products with price > $100 and quantity < 10"
- "Calculate correlation between age and spending"
- "Show distribution of values using histogram"

---

## 🚀 **Future Enhancements**

- [ ] Multi-file analysis
- [ ] SQL database support
- [ ] Export analysis reports (PDF)
- [ ] Save chat history
- [ ] Custom chart themes
- [ ] More chart types
- [ ] Data cleaning suggestions
- [ ] Automated insights

---

## 🎓 **What You'll Learn**

Building this project teaches:
- ✅ **Code-Executing Agents** - AI that writes and runs code
- ✅ **Safe Execution** - Sandboxed Python environments
- ✅ **Plotly Mastery** - Interactive visualizations
- ✅ **FastAPI** - Modern web APIs
- ✅ **Gemini AI** - Direct integration (avoiding langchain issues)
- ✅ **Prompt Engineering** - Generate accurate code
- ✅ **Error Handling** - Graceful failure recovery

---

## 📝 **License**

This project is for educational purposes.

---

## 🙏 **Credits**

Built with:
- **Google Gemini 2.0 Flash** - AI code generation
- **Plotly** - Interactive visualizations
- **FastAPI** - Web framework
- **Pandas** - Data manipulation

---

## 📧 **Support**

For issues:
1. Check API key configuration
2. Verify dependencies are installed
3. Check terminal logs for errors
4. Ensure file format is CSV or Excel

---

**Made with ❤️ for Data Enthusiasts**

*Transform your data into insights in seconds!* 🚀
