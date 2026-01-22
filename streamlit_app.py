import streamlit as st
import pandas as pd

# 🔴 IMPORTANT: direct backend call (NO HTTP)
from backend.query_service import run_query

# ---------------------------------
# Page Config
# ---------------------------------
st.set_page_config(
    page_title="Smarteye Query Bot",
    layout="wide"
)

st.title("🧠 Smarteye Query Bot")
st.caption("Ask me queries in plain English and I will show you the data.")

# ---------------------------------
# Mill Selection
# ---------------------------------
mill = st.selectbox(
    "Select Mill",
    ["Hastings", "Gondalpara", "India"],
    index=0
)

# ---------------------------------
# Input
# ---------------------------------
question = st.text_input(
    "Ask your question",
    placeholder="e.g. show attendance of nz1073 yesterday"
)

# ---------------------------------
# Button Action
# ---------------------------------
if st.button("Ask"):
    if not question.strip():
        st.warning("Please enter a question")
    else:
        with st.spinner("Thinking and fetching data..."):
            try:
                # 🔴 NO HTTP CALL — direct function call
                result = run_query(question)

                # -------------------------
                # Handle invalid / unsupported
                # -------------------------
                if result["status"] == "invalid":
                    st.error("❌ Invalid query")
                    st.stop()

                if result["status"] == "unsupported":
                    st.info("🤖 This query is not supported yet. We will work on that.")
                    st.stop()

                # -------------------------
                # Success
                # -------------------------
                st.success(f"Fetched {result['row_count']} rows")

                df = pd.DataFrame(result["rows"])

                with st.expander("Generated SQL"):
                    st.code(result["sql_used"], language="sql")

                st.dataframe(df, use_container_width=True)

            except Exception as e:
                st.error(f"❌ Error while executing query: {e}")
