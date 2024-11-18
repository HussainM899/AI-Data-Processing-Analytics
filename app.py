import pandas as pd
import streamlit as st
import plotly.express as px
import google.generativeai as genai
from langchain_google_genai import GoogleGenerativeAI
from io import BytesIO
import os

# Configure page settings
st.set_page_config(page_title="Excel Automation App", layout="wide")

# Declare CADRE_MAPPINGS at the top level of your script, before any functions
CADRE_MAPPINGS = {
    "District NSTOP Officer": "District Level",
    "DCO/DHCSO": "District Level",
    "Disease Surveillance Officer": "District Level",
    "Immunization Officer": "District Level",
    "Federal/Provincial/District Facilitator": "District Level",
    "Divisional NSTOP Officer": "District Level",
    "ComNET staff": "District Level",
    "Area Coordinator / District Coordinator": "District Level",
    "Provincial Facilitator (M&E, Campaign, HRMP, etc.)": "District Level",
    "DDHO": "District Level",
    "CEO/DHO": "District Level",
    "DSV / ASV": "District Level",
    "Federal Facilitator (UNICEF)": "Federal Level",
    "EPI Coordinator": "Provincial Level",
    "Provincial Facilitator (EPI, Coordinator etc)": "Provincial Level",
    "Federal/Provincial/District Facilitator": "Provincial Level",
    "TPO/ TDO": "Town Level",
    "ComNET staff": "Town Level",
    "TCO": "Town Level",
    "UCPO / UCSP/ UCDO": "UC Level",
    "UCMO": "UC Level",
    "TTSP/TUSP": "UC Level",
    "Social Mobilizers": "UC Level",
    "Independent Monitor": "UC Level",
}

from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get API key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

def upload_and_parse_file():
    """Handle file upload and parsing."""
    try:
        # Detect file type and parse accordingly
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            # Handle multi-level headers
            df = pd.read_excel(uploaded_file, header=[0, 1])
        
        # If multi-level headers exist, combine them
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [' '.join(str(col) for col in cols if str(col) != 'nan').strip() 
                        for cols in df.columns.values]
        
        return df
    except Exception as e:
        st.error(f"Error reading file: {str(e)}")
        return None

def clean_data(df):
    """Perform data cleaning on the DataFrame."""
    try:
        # Remove duplicate rows
        df = df.drop_duplicates()
        
        # Fill NA values
        df = df.fillna("N/A")
        
        # Remove leading/trailing whitespace from string columns
        for col in df.select_dtypes(include=['object']):
            df[col] = df[col].str.strip()
        
        return df
    except Exception as e:
        st.error(f"Error cleaning data: {str(e)}")
        return df

def map_designations(df, column_name="designation_title"):
    """Map designations to cadres dynamically."""
    try:
        if column_name not in df.columns:
            st.error(f"Column '{column_name}' not found in the uploaded file.")
            return df

        # Create Cadre column using the mapping
        df["Cadre"] = df[column_name].map(CADRE_MAPPINGS).fillna("Unmapped")
        return df
    except Exception as e:
        st.error(f"Error mapping designations: {str(e)}")
        return df

def handle_new_designations(df, column_name="designation_title"):
    """Handle new designations and update the CADRE_MAPPINGS dictionary."""
    try:
        # Get current designations that aren't in our mapping
        current_designations = set(df[df['Cadre'] == 'Unmapped'][column_name].unique())
        
        if current_designations:
            st.warning(f"📝 Found {len(current_designations)} new designation(s) that need mapping!")
            
            # Available cadre levels (predefined options only)
            CADRE_LEVELS = [
                "District Level",
                "Federal Level",
                "Provincial Level",
                "Town Level",
                "UC Level"
            ]
            
            # Create a container for new mappings
            new_mappings = {}
            
            with st.expander("Map New Designations", expanded=True):
                st.markdown("### New Designations Found")
                st.markdown("Please assign appropriate cadres to the following designations:")
                
                # Create a form for mapping new designations
                for designation in current_designations:
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.text(designation)
                    with col2:
                        selected_cadre = st.selectbox(
                            "Select Cadre",
                            options=CADRE_LEVELS,
                            key=f"new_designation_{designation}"
                        )
                        new_mappings[designation] = selected_cadre
                
                # Button to confirm mappings
                if st.button("Confirm New Mappings"):
                    # Update CADRE_MAPPINGS
                    CADRE_MAPPINGS.update(new_mappings)
                    
                    # Update the DataFrame with new mappings
                    df["Cadre"] = df[column_name].map(CADRE_MAPPINGS).fillna("Unmapped")
                    
                    st.success("✅ Mappings updated successfully!")
                    
                    # Show the new mappings
                    st.markdown("### New Mappings Added:")
                    for designation, cadre in new_mappings.items():
                        st.markdown(f"- **{designation}**: {cadre}")
                    
                    # Option to export updated mappings
                    if st.button("Export Updated Mappings"):
                        export_mappings(CADRE_MAPPINGS)
        
        return df
                    
    except Exception as e:
        st.error(f"Error handling new designations: {str(e)}")
        return df

def show_interactive_preview(df):
    """Show interactive data preview with enhanced features."""
    st.subheader("📋 Interactive Data Preview")
    
    # View options in an expander
    with st.expander("🔧 View Options", expanded=False):
        # Column selection
        cols = st.multiselect(
            "Select columns to display:",
            df.columns.tolist(),
            default=df.columns.tolist()
        )
        
        # Row count slider
        row_count = st.slider(
            "Number of rows to display:",
            min_value=5,
            max_value=len(df),
            value=min(50, len(df))
        )
        
        # Index visibility
        hide_index = st.checkbox("Hide index", value=True)
    
    # Search and filter in an expander
    with st.expander("🔍 Search & Filters", expanded=False):
        # Global search
        search = st.text_input("Search in all columns:", "")
        
        # Column-specific filters
        filter_col = st.selectbox("Filter by column:", ["None"] + df.columns.tolist())
        
        if filter_col != "None":
            if df[filter_col].dtype in ['int64', 'float64']:
                # Numeric filter
                min_val, max_val = st.slider(
                    f"Range for {filter_col}:",
                    float(df[filter_col].min()),
                    float(df[filter_col].max()),
                    (float(df[filter_col].min()), float(df[filter_col].max()))
                )
            else:
                # Category filter
                unique_vals = df[filter_col].unique().tolist()
                selected_vals = st.multiselect(
                    f"Select values for {filter_col}:",
                    unique_vals,
                    default=unique_vals
                )
    
    # Apply filters
    filtered_df = df.copy()
    
    # Apply search
    if search:
        mask = filtered_df.astype(str).apply(
            lambda x: x.str.contains(search, case=False)
        ).any(axis=1)
        filtered_df = filtered_df[mask]
    
    # Apply column filter
    if filter_col != "None":
        if df[filter_col].dtype in ['int64', 'float64']:
            filtered_df = filtered_df[
                (filtered_df[filter_col] >= min_val) & 
                (filtered_df[filter_col] <= max_val)
            ]
        else:
            filtered_df = filtered_df[filtered_df[filter_col].isin(selected_vals)]
    
    # Show the filtered dataframe
    st.dataframe(
        filtered_df[cols].head(row_count),
        use_container_width=True,
        height=400,  # Fixed height for scrolling
        hide_index=hide_index,
    )
    
    # Show statistics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.caption(f"Showing {len(filtered_df)} of {len(df)} rows")
    with col2:
        st.caption(f"Selected {len(cols)} columns")
    with col3:
        st.caption(f"Memory usage: {df.memory_usage().sum() / 1024:.2f} KB")
    
    return filtered_df

def show_visualizations(df):
    """Display various visualizations of the data."""
    try:
        st.subheader("📊 Data Visualizations")
        
        # Cadre distribution if available
        if "Cadre" in df.columns:
            with st.expander("Cadre Distribution", expanded=True):
                fig_cadre = px.pie(df, names="Cadre", title="Distribution of Cadres")
                st.plotly_chart(fig_cadre, use_container_width=True)
        
        # Numeric column distributions
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            with st.expander("Numeric Distributions", expanded=False):
                selected_column = st.selectbox(
                    "Select numeric column for distribution",
                    numeric_cols
                )
                fig_dist = px.histogram(
                    df, 
                    x=selected_column,
                    title=f"Distribution of {selected_column}"
                )
                st.plotly_chart(fig_dist, use_container_width=True)
        
        # Correlation matrix for numeric columns
        if len(numeric_cols) > 1:
            with st.expander("Correlation Matrix", expanded=False):
                corr_matrix = df[numeric_cols].corr()
                fig_corr = px.imshow(
                    corr_matrix,
                    title="Correlation Matrix"
                )
                st.plotly_chart(fig_corr, use_container_width=True)
                
    except Exception as e:
        st.error(f"Error creating visualizations: {str(e)}")

def query_gemini(df, question):
    """Query Gemini AI with enhanced analytics capabilities"""
    try:
        llm = GoogleGenerativeAI(
            model="gemini-1.5-pro",
            google_api_key=GOOGLE_API_KEY,
            temperature=0.1
        )
        
        # Analyze the question to determine what data to include
        question_lower = question.lower()
        
        # Initialize context parts
        context_parts = []
        
        # Add basic dataset info
        context_parts.append(f"Total Records: {len(df)}")
        context_parts.append(f"Available Columns: {', '.join(df.columns.tolist())}")
        
        # Add relevant data based on question
        if 'district' in question_lower:
            district_counts = df['district_name'].value_counts()
            context_parts.append("\nDistrict Information:")
            context_parts.append(f"Total Districts: {len(district_counts)}")
            context_parts.append("Top Districts by Count:")
            context_parts.append(district_counts.head().to_string())
            
        if 'cadre' in question_lower:
            cadre_counts = df['Cadre'].value_counts()
            context_parts.append("\nCadre Information:")
            context_parts.append(cadre_counts.to_string())
            
        if 'designation' in question_lower:
            designation_counts = df['designation_title'].value_counts()
            context_parts.append("\nDesignation Information:")
            context_parts.append(designation_counts.head().to_string())
            
        # For questions about "most" or "highest"
        if any(word in question_lower for word in ['most', 'highest', 'maximum', 'top']):
            if 'district' in question_lower:
                top_district = df['district_name'].value_counts().head(1)
                context_parts.append(f"\nHighest Count District:")
                context_parts.append(f"{top_district.index[0]}: {top_district.values[0]} records")
        
        # Combine all context parts
        context = "\n".join(context_parts)
        
        prompt = f"""You are an expert Operational data analyst who has more than 15 years of experience in Polio Program internationally. Answer the following question using the provided data:

        Context:
        {context}

        Question: {question}

        Requirements for your answer:
        1. Give ONLY the exact answer with specific numbers
        2. For questions about "most" or "highest", give the specific name and count
        3. Format: "[Name/Value] with [count] records" or similar
        4. If asking about a specific column, give values from that column only
        5. Do not mention other columns unless specifically asked
        6. Do not explain methodology
        7. Keep response to one sentence
        8. If data isn't available, say "Data not available"

        Examples:
        Q: "Which district has most data?" 
        A: "Karachi South with 1,234 records."
        
        Q: "What is the total count?"
        A: "The dataset contains 5,678 total records."

        Answer the question directly and concisely."""

        with st.spinner('Analyzing data...'):
            response = llm.invoke(prompt)
            
            # Debug logging
            st.session_state['last_context'] = context
            st.session_state['last_response'] = response
            
            return response

    except Exception as e:
        st.error(f"Error in analysis: {str(e)}")
        return "Error occurred during analysis"

def export_data(df):
    """Allow users to download the processed DataFrame."""
    try:
        towrite = BytesIO()
        df.to_excel(towrite, index=False, engine="openpyxl")
        towrite.seek(0)
        
        return st.download_button(
            label="📥 Download Processed Data",
            data=towrite,
            file_name="processed_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        st.error(f"Error exporting data: {str(e)}")

def export_mappings(mappings):
    """Export the updated mappings dictionary."""
    try:
        import json
        mappings_json = json.dumps(mappings, indent=4)
        st.download_button(
            label="📥 Download Mappings",
            data=mappings_json,
            file_name="cadre_mappings.json",
            mime="application/json"
        )
    except Exception as e:
        st.error(f"Error exporting mappings: {str(e)}")

def main():
    """Main application function."""
    try:
        st.title("📊 Excel Automation App with Gemini AI")
        
        # Add sidebar for app navigation
        st.sidebar.title("Navigation")
        app_mode = st.sidebar.selectbox(
            "Choose the app mode",
            ["Data Processing", "Analysis & Visualization", "About"]
        )
        
        if app_mode == "About":
            st.markdown("""
            ### About this app
            This app helps you process Excel files and analyze data using AI.
            
            #### Features:
            - Upload and process Excel/CSV files
            - Automatic data cleaning
            - Interactive data preview
            - Designation to Cadre mapping
            - AI-powered analysis
            - Data visualization
            - Export processed data
            
            #### How to use:
            1. Upload your file
            2. Review and clean the data
            3. Map designations to cadres
            4. Analyze using AI
            5. Export processed data
            """)
            return

        # Create two columns for layout
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # File uploader in main function
            uploaded_file = st.file_uploader("Upload your file (CSV/XLS/XLSX)", type=["csv", "xls", "xlsx"])
            
            if uploaded_file:
                try:
                    # Read the file
                    with st.spinner('Reading file...'):
                        if uploaded_file.name.endswith(".csv"):
                            df = pd.read_csv(uploaded_file)
                        else:
                            df = pd.read_excel(uploaded_file, header=[0, 1])
                        
                        # Handle multi-level headers
                        if isinstance(df.columns, pd.MultiIndex):
                            df.columns = [' '.join(str(col) for col in cols if str(col) != 'nan').strip() 
                                        for cols in df.columns.values]
                    
                    st.success("File uploaded successfully!")
                    
                    # Clean data with progress indicator
                    with st.spinner('Cleaning data...'):
                        df = clean_data(df)
                    
                    # Map designations to cadres
                    with st.spinner('Mapping designations to cadres...'):
                        df = map_designations(df)
                        
                        # Show the unique designations that weren't mapped
                        unmapped = df[df['Cadre'] == 'Unmapped']['designation_title'].unique()
                        if len(unmapped) > 0:
                            st.warning(f"Found {len(unmapped)} unmapped designations!")
                    
                    if app_mode == "Data Processing":
                        # Handle new designations if any are unmapped
                        if len(unmapped) > 0:
                            df = handle_new_designations(df)
                            # Reapply mapping after handling new designations
                            df = map_designations(df)
                        
                        # Show interactive preview
                        filtered_df = show_interactive_preview(df)
                        
                        # Export Options
                        st.subheader("📥 Export Options")
                        col1, col2 = st.columns(2)
                        with col1:
                            export_data(filtered_df)
                        with col2:
                            export_mappings(CADRE_MAPPINGS)
                    
                    elif app_mode == "Analysis & Visualization":
                        show_visualizations(df)
                        
                        # Gemini AI Query Section
                        st.subheader("💬 Ask Gemini AI about your data")
                        
                        # Add suggested questions
                        suggested_questions = [
                            f"How many total records are in the dataset?",
                            f"What is the exact count and percentage for each Cadre level?",
                            f"How many unmapped designations are there?",
                            f"What is the most common Cadre level?",
                            f"What percentage of staff is at the District Level?",
                            "Custom Question"
                        ]
                        
                        question_type = st.selectbox(
                            "Choose a question type:",
                            suggested_questions
                        )
                        
                        if question_type == "Custom Question":
                            question = st.text_input("Enter your question about the data:")
                        else:
                            question = question_type
                        
                        if question:
                            with st.spinner('Analyzing data...'):
                                response = query_gemini(df, question)
                                st.markdown("### Analysis Results")
                                st.markdown(response)
                                
                                # Add debug expander
                                with st.expander("Debug Information", expanded=False):
                                    if 'last_context' in st.session_state:
                                        st.text("Context sent to AI:")
                                        st.code(st.session_state['last_context'])
                                    if 'last_response' in st.session_state:
                                        st.text("Raw AI Response:")
                                        st.code(st.session_state['last_response'])
                                
                                if st.button("Generate Follow-up Questions"):
                                    follow_up_prompt = f"Based on the previous analysis about '{question}', what are 3 relevant follow-up questions we could ask about this data?"
                                    follow_up_response = query_gemini(df, follow_up_prompt)
                                    st.markdown("### Suggested Follow-up Questions")
                                    st.markdown(follow_up_response)
                
                except Exception as e:
                    st.error(f"Error processing file: {str(e)}")
        
        # Add footer
        st.markdown("---")
        st.markdown("Built with Streamlit and Gemini AI")

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()