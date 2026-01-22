import sys
from pathlib import Path

# Add project root to PYTHONPATH
ROOT_DIR = Path(__file__).parent
sys.path.append(str(ROOT_DIR))

import streamlit as st
import pandas as pd
from backend.query_service import run_query

st.set_page_config(
    page_title="Smarteye Query Bot",
    layout="wide"
)

st.title("🧠 Smarteye Query Bot")
st.caption("Ask me queries in plain English and I will show you the data.")

mill = st.selectbox(
    "Select Mill",
    ["Hastings", "Gondalpara", "India"],
    index=0
)

question = st.text_input(
    "Ask your question",
    placeholder="e.g. show attendance of nz1073 yesterday"
)

if st.button("Ask"):
    if not question.strip():
        st.warning("Please enter a question")
    else:
        with st.spinner("Thinking and fetching data..."):
            try:
                result = run_query(question)

                if result["status"] == "invalid":
                    st.error("❌ Invalid query")
                elif result["status"] == "unsupported":
                    st.info("🤖 This query is not supported yet. We will work on that.")
                else:
                    st.success(f"Fetched {result['row_count']} rows")

                    df = pd.DataFrame(result["rows"])

                    with st.expander("Generated SQL"):
                        st.code(result["sql_used"], language="sql")

                    st.dataframe(df, use_container_width=True)

            except Exception as e:
                st.error(f"❌ Error: {e}")
