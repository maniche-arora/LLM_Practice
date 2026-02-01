# Resume AI Analyzer - Usage Guide

## Project Structure

- **agent.py** - Core Resume Analysis Agent with AI-powered analysis logic
- **app.py** - Main application orchestrator that binds UI and Agent
- **ui.py** - All UI components and rendering functions
- **requirements.txt** - Project dependencies

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set OpenAI API Key
You have two options:

**Option A: Environment Variable (Recommended)**
```bash
# On Windows (PowerShell)
$env:OPENAI_API_KEY = "your-api-key-here"

# Or add to .env file in the project root
OPENAI_API_KEY=your-api-key-here
```

**Option B: Direct Input in UI**
- Enter your API key directly in the sidebar when the app runs

### 3. Run the Application
```bash
streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`

## How to Use

### 1. **Configure Settings** (Sidebar)
   - Enter your OpenAI API Key
   - Adjust the Selection Cutoff Score (default: 75%)

### 2. **Upload Documents**
   Choose one of two approaches:
   
   **Approach A: Upload Resume + Job Description**
   - Upload your resume (PDF or TXT)
   - Upload a job description (PDF or TXT)
   - The app will extract skills from the job description

   **Approach B: Upload Resume + Manual Requirements**
   - Upload your resume (PDF or TXT)
   - Enter required skills manually (comma-separated)
   - Example: `Python, Machine Learning, SQL, TensorFlow, Data Analysis`

### 3. **Analyze**
   - Click the "🔍 Analyze Resume" button
   - Wait for the analysis to complete (typically 1-2 minutes)

### 4. **Review Results**
   The results include:
   - **Overall Score**: Resume match percentage (0-100%)
   - **Selection Status**: RECOMMENDED or NOT RECOMMENDED
   - **Skill Analysis**: Detailed scores for each required skill
   - **Strengths**: Skills where the resume excels
   - **Areas for Improvement**: Missing or weak skills with specific suggestions
   - **Example Additions**: Concrete bullet points to add to the resume

### 5. **Export Results**
   - Download results as JSON for programmatic use
   - Download results as Text for a readable report

## Features

### 🔍 Intelligent Analysis
- Uses GPT-4 for semantic understanding of resume content
- Evaluates skills in context, not just keyword matching
- Provides detailed reasoning for each score

### 💪 Strength Identification
- Identifies which required skills are well-demonstrated
- Confidence scores based on resume content depth

### ⚠️ Weakness Analysis
- Pinpoints missing or underdeveloped skills
- Provides actionable improvement suggestions
- Includes example text that could be added

### 📊 Comprehensive Reporting
- Multiple view options for analysis results
- Easy-to-understand visualizations
- Exportable reports

## Architecture

### app.py (Orchestrator)
- Manages application state using Streamlit session
- Handles file validation
- Coordinates between UI and Agent
- Manages user interactions

### ui.py (UI Components)
- Renders all UI elements
- Handles file uploads
- Displays analysis results
- Provides export functionality

### agent.py (Core Logic)
- Extracts text from PDF/TXT files
- Performs semantic skill analysis using RAG
- Identifies weaknesses with AI-powered suggestions
- Returns structured analysis results

## Error Handling

The application handles:
- Missing API key
- Invalid file formats
- Missing resume or job description
- API rate limits
- File extraction errors

Check the error messages in the UI for troubleshooting.

## Tips for Best Results

1. **Resume Quality**: Use a well-formatted resume with clear section headers
2. **Job Description**: Provide the full job description for accurate skill extraction
3. **Skills Format**: When entering skills manually, be as specific as possible (e.g., "Python 3.9" vs just "Python")
4. **Review Suggestions**: Read the improvement suggestions carefully and customize them for your resume

## Performance Notes

- Initial analysis typically takes 1-2 minutes
- Processing time depends on resume length and number of skills
- API rate limits may apply based on your OpenAI plan

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "API Key is required" | Add your OpenAI API key in the sidebar |
| "Please upload resume" | Upload a PDF or TXT file |
| "Analysis failed" | Check that your API key is valid and has sufficient credits |
| Slow performance | Reduce resume length or number of skills to analyze |
| Empty results | Ensure the resume file isn't corrupted and is readable |
