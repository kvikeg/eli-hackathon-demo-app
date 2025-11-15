import re
import sqlite3

import pandas as pd
import plotly.express as px
import streamlit as st
from google import genai

import ai_utils
import db_utils

# Page configuration
st.set_page_config(
    page_title="Text-to-SQL Visualization Bot", page_icon="🤖", layout="wide"
)

# Initialize session state
if "query_history" not in st.session_state:
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
    sql_query = ai_utils.text_to_sql(question, schema, st.secrets["MODEL"], client)
    return sql_query


def create_visualization(df, question):
    return ai_utils.create_visualization(df, question)


# Main app
def main():
    st.title("🤖 Text-to-SQL Visualization Bot")
    st.markdown("Ask questions about your data in plain English!")

    # Sidebar for API key
    with st.sidebar:
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
    question = st.text_input(
        "💬 Ask a question about your data:",
        placeholder="e.g., What were the top selling products last month?",
    )

    col1, col2 = st.columns([1, 5])
    with col1:
        search_button = st.button("🔍 Search", type="primary")

    if search_button and question:
        try:
            pass

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.info("💡 Try rephrasing your question or check the generated SQL query")

    # Show query history
    if st.session_state.query_history:
        st.markdown("---")
        st.subheader("📜 Query History")
        for i, item in enumerate(reversed(st.session_state.query_history[-5:]), 1):
            with st.expander(f"{i}. {item['question']} ({item['results']} results)"):
                st.code(item["sql"], language="sql")


if __name__ == "__main__":
    main()
