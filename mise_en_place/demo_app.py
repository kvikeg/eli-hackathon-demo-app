import streamlit as st
import sqlite3
import pandas as pd
from google import genai
import plotly.express as px
import re
import db_utils

# Page configuration
st.set_page_config(
    page_title="Text-to-SQL Visualization Bot",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state
if 'query_history' not in st.session_state:
    st.session_state.query_history = []

# Database setup
@st.cache_resource
def init_database():
    conn = db_utils.init_database() 
    return conn

def get_schema(conn):
    schema_text = db_utils.get_schema(conn)
    return schema_text

@st.cache_resource
def init_client():
    """Initialize the client"""
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    return client

def text_to_sql(question, schema, client):
    """Convert natural language to SQL using Gemini"""
    prompt = f"""You are a SQL expert. Convert the following natural language question into a SQL query.

{schema}

Question: {question}

Important:
- Return ONLY the SQL query, no explanations or markdown
- Use proper table and column names from the schema
- Make sure the query is valid SQLite syntax
- For aggregations, use appropriate GROUP BY clauses
- For date-based queries, use date functions properly

SQL Query:"""
    
    response = client.models.generate_content(model=st.secrets["MODEL"], contents=prompt)
    sql_query = response.text.strip()
    
    # Clean up the SQL (remove markdown code blocks if present)
    sql_query = re.sub(r'```sql\n?', '', sql_query)
    sql_query = re.sub(r'```\n?', '', sql_query)
    sql_query = sql_query.strip()
    
    return sql_query

def determine_chart_type(df, question):
    """Determine appropriate chart type based on data and question"""
    question_lower = question.lower()
    
    # Check for time series
    date_columns = [col for col in df.columns if 'date' in col.lower()]
    if date_columns:
        return 'line'
    
    # Check for percentage/proportion keywords
    if any(word in question_lower for word in ['percentage', 'proportion', 'share', 'distribution']):
        return 'pie'
    
    # Check for trend keywords
    if any(word in question_lower for word in ['trend', 'over time', 'monthly', 'yearly']):
        return 'line'
    
    # Check for comparison keywords
    if any(word in question_lower for word in ['compare', 'top', 'bottom', 'highest', 'lowest']):
        return 'bar'
    
    # Default based on data shape
    if len(df.columns) == 2:
        if df.shape[0] <= 10:
            return 'bar'
        else:
            return 'line'
    
    return 'bar'

def create_visualization(df, question):
    """Create appropriate visualization based on data"""
    if df.empty:
        return None
    
    chart_type = determine_chart_type(df, question)
    
    # Get column names
    cols = df.columns.tolist()
    
    try:
        if chart_type == 'pie' and len(cols) >= 2:
            fig = px.pie(df, names=cols[0], values=cols[1], title="Distribution")
        elif chart_type == 'line' and len(cols) >= 2:
            fig = px.line(df, x=cols[0], y=cols[1], title="Trend Over Time", markers=True)
        else:  # bar chart
            if len(cols) >= 2:
                fig = px.bar(df, x=cols[0], y=cols[1], title="Comparison")
            else:
                fig = px.bar(df, y=cols[0], title="Values")
        
        fig.update_layout(height=400)
        return fig
    except Exception as e:
        st.error(f"Error creating visualization: {str(e)}")
        return None

# Main app
def main():
    st.title("🤖 Text-to-SQL Visualization Bot")
    st.markdown("Ask questions about your data in plain English!")
    
    # Sidebar for API key
    with st.sidebar:
        st.header("⚙️ Configuration")
        api_key = st.text_input("Google Gemini API Key", type="password", help="Get your free API key from https://makersuite.google.com/app/apikey")
        
        st.markdown("---")
        st.header("📊 Sample Questions")
        st.markdown("""
        - What are the top 5 products by revenue?
        - Show total sales by region
        - What is the monthly sales trend for 2024?
        - Which customers have spent the most?
        - Show revenue distribution by category
        """)
        
        st.markdown("---")
        if st.button("🗑️ Clear History"):
            st.session_state.query_history = []
            st.rerun()
    
    # Initialize database
    conn = init_database()
    schema = get_schema(conn)
    
    # Initialize model and client
    client = init_client()
    
    # Show schema in expander
    with st.expander("📋 View Database Schema"):
        st.code(schema)
    
    # Main query interface
    question = st.text_input("💬 Ask a question about your data:", 
                            placeholder="e.g., What were the top selling products last month?")
    
    col1, col2 = st.columns([1, 5])
    with col1:
        search_button = st.button("🔍 Search", type="primary")
    
    if search_button and question:
        #if not api_key:
        #    st.error("⚠️ Please enter your Google Gemini API key in the sidebar")
        #    return
        
        try:
            with st.spinner("🤔 Converting your question to SQL..."):
                sql_query = text_to_sql(question, schema, client)
            
            st.success("✅ SQL Query Generated!")
            
            # Show generated SQL
            with st.expander("🔧 View Generated SQL", expanded=True):
                st.code(sql_query, language="sql")
            
            # Execute query
            with st.spinner("📊 Fetching data..."):
                df = pd.read_sql_query(sql_query, conn)
            
            if df.empty:
                st.warning("No results found for your query.")
            else:
                # Show results
                st.subheader("📈 Results")
                
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.dataframe(df, use_container_width=True)
                
                with col2:
                    fig = create_visualization(df, question)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                
                # Add to history
                st.session_state.query_history.append({
                    'question': question,
                    'sql': sql_query,
                    'results': len(df)
                })
        
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.info("💡 Try rephrasing your question or check the generated SQL query")
    
    # Show query history
    if st.session_state.query_history:
        st.markdown("---")
        st.subheader("📜 Query History")
        for i, item in enumerate(reversed(st.session_state.query_history[-5:]), 1):
            with st.expander(f"{i}. {item['question']} ({item['results']} results)"):
                st.code(item['sql'], language="sql")

if __name__ == "__main__":
    main()
