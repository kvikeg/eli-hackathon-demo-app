import re

import pandas as pd
import plotly.express as px
from google import genai


def text_to_sql(question, schema, model, client: genai.client.Client):
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

    response = client.models.generate_content(model=model, contents=prompt)
    sql_query = response.text.strip()

    # Clean up the SQL (remove markdown code blocks if present)
    sql_query = re.sub(r"```sql\n?", "", sql_query)
    sql_query = re.sub(r"```\n?", "", sql_query)
    sql_query = sql_query.strip()

    return sql_query


def determine_chart_type(df: pd.DataFrame, question):
    """Determine appropriate chart type based on data and question"""
    question_lower = question.lower()

    # Check for time series
    date_columns = [col for col in df.columns if "date" in col.lower()]
    if date_columns:
        return "line"

    # Check for percentage/proportion keywords
    if any(
        word in question_lower
        for word in ["percentage", "proportion", "share", "distribution"]
    ):
        return "pie"

    # Check for trend keywords
    if any(
        word in question_lower for word in ["trend", "over time", "monthly", "yearly"]
    ):
        return "line"

    # Check for comparison keywords
    if any(
        word in question_lower
        for word in ["compare", "top", "bottom", "highest", "lowest"]
    ):
        return "bar"

    # Default based on data shape
    if len(df.columns) == 2:
        if df.shape[0] <= 10:
            return "bar"
        else:
            return "line"

    return "bar"


def create_visualization(df: pd.DataFrame, question):
    """Create appropriate visualization based on data"""
    if df.empty:
        return None

    chart_type = determine_chart_type(df, question)

    # Get column names
    cols = df.columns.tolist()

    try:
        if chart_type == "pie" and len(cols) >= 2:
            fig = px.pie(df, names=cols[0], values=cols[1], title="Distribution")
        elif chart_type == "line" and len(cols) >= 2:
            fig = px.line(
                df, x=cols[0], y=cols[1], title="Trend Over Time", markers=True
            )
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
