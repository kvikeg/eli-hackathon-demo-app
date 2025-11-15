#########################################################
# Step 1
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
    st.session_state.query_history.append(
        {"question": question, "sql": sql_query, "results": len(df)}
    )
