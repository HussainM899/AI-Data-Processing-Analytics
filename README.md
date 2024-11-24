# AI-Powered Excel Data Analysis App 

A Streamlit application that automates Excel data processing, provides intelligent analysis using Google's Gemini AI, and offers interactive visualizations. Perfect for analyzing EOC (Emergency Operations Center) data with automated designation-to-cadre mapping.

## Video Tutorial: 

[AI-Powered Excel Automation App](https://drive.google.com/file/d/15bSBfMZLzDJXDJ74gD3NItOFDzfB_UDp/view?usp=sharing)

## Features 

- **File Upload & Processing**
  - Supports CSV, XLS, XLSX formats
  - Automatic data cleaning
  - Smart designation to cadre mapping
  - Handles multi-level headers

- **Interactive Data Preview**
  - Column selection
  - Global search functionality
  - Advanced column-specific filters
  - Customizable row display
  - Hide/show index options

- **AI-Powered Analysis**
  - Intelligent data insights using Gemini AI
  - Natural language queries
  - Automated data summaries
  - Pattern recognition
  - Follow-up question suggestions

- **Data Visualization**
  - Dynamic charts and graphs
  - Cadre distribution analysis
  - District-wise visualizations
  - Interactive dashboards
  - Correlation analysis
## Setup & Installation 

Live Web App on Huggingface Space: [AI Data Processing Analytics](https://huggingface.co/spaces/HussainM899/AI-Powered_Excel_Data_Analysis_App)


## Setup & Installation 

1. **Clone the repository**
   ```bash
   git clone https://github.com/HussainM899/AI-Data-Processing-Analytics.git
   cd AI-Data-Processing-Analytics
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # For Linux/Mac
   venv\Scripts\activate     # For Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   - Create a `.env` file in the root directory
   - Add required credentials (see `.env.example`)

## Required Environment Variables 
   ```.env
   env
   GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json
   GOOGLE_API_KEY=your_api_key_here
   ```

## Usage 

1. **Start the application**
   ```bash
   streamlit run app.py
   ```

2. **Upload Data**
   - Use the file uploader to import your Excel/CSV file
   - The app automatically processes and cleans the data
   - Multi-level headers are automatically handled

3. **Analyze Data**
   - Use the navigation sidebar to switch between modes:
     - Data Processing
     - Analysis & Visualization
     - About
   - Ask questions in natural language
   - View automated insights and visualizations

4. **Export Results**
   - Download processed data in Excel format
   - Export updated designation mappings
   - Save analysis reports

## Project Structure 
```
AI-Data-Processing-Analytics/
├── app.py # Main application file
├── requirements.txt # Project dependencies
├── .env.example # Example environment variables
├── .gitignore # Git ignore rules
└── README.md # Project documentation
```


## Dependencies 

- `streamlit`: Web application framework
- `pandas`: Data manipulation and analysis
- `plotly`: Interactive visualizations
- `google-generativeai`: Gemini AI integration
- `langchain-google-genai`: LangChain integration
- `python-dotenv`: Environment variable management
- `openpyxl`: Excel file handling

## Security Notes 

- Never commit sensitive credentials
- Use environment variables for API keys
- Keep service account JSON file secure
- Regularly rotate credentials
- Avoid sharing API keys publicly

## Features in Detail 

### Data Processing
- Automatic cleaning of data
- Handling of missing values
- Removal of duplicates
- Smart string cleaning
- Multi-level header handling

### AI Analysis
- District-wise analysis
- Cadre distribution insights
- Trend identification
- Anomaly detection
- Custom query handling

### Visualization
- Pie charts for distributions
- Bar charts for comparisons
- Histograms for numerical data
- Correlation matrices
- Interactive filters

## Contributing 

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License 

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact 

Hussain - hussainmurtaza899@gmail.com
Project Link: [https://github.com/HussainM899/AI-Data-Processing-Analytics](https://github.com/HussainM899/AI-Data-Processing-Analytics)

---
Built using Streamlit and Gemini AI
