import streamlit as st
import requests
import pandas as pd

st.set_page_config(
    page_title="Smarteye Query Bot",
    layout="wide"
)

st.title("🧠 Smarteye Query Bot")
st.caption("Ask me queries in plain English and I will show you the data.")

# -------------------------------
# Mill Selection
# -------------------------------
mill = st.selectbox(
    "Select Mill",
    ["Hastings", "Gondalpara", "India"],
    index=0
)

# -------------------------------
# Input
# -------------------------------
question = st.text_input(
    "Ask your question",
    placeholder="e.g. show attendance of nz1073 yesterday"
)

# -------------------------------
# Button Action
# -------------------------------
if st.button("Ask"):
    if not question.strip():
        st.warning("Please enter a question")
    else:
        with st.spinner("Thinking and fetching data..."):
            try:
                response = requests.post(
                    "http://127.0.0.1:8000/ask",
                    json={
                        "question": question,
                        "mill": mill.lower()
                    },
                    timeout=30
                )

                data = response.json()

                if data["status"] != "ok":
                    st.error(data.get("message", "Unknown error"))
                    st.stop()
                else:
                    st.success(f"Fetched {data['row_count']} rows")

                    df = pd.DataFrame(data["rows"])

                    with st.expander("Generated SQL"):
                        st.code(data["sql_used"], language="sql")

                    st.dataframe(df, use_container_width=True)

            except Exception as e:
                st.error(f"Failed to connect to backend: {e}")
