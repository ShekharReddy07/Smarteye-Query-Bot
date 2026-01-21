from llm_engine import generate_sql_from_question
from sql_guard import validate_sql

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import pyodbc
import os
from dotenv import load_dotenv
import re

# -------------------------------------
# Load ENV
# -------------------------------------
load_dotenv()

DB_SERVER = os.getenv("DB_SERVER")
DB_DATABASE = os.getenv("DB_DATABASE")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DRIVER = os.getenv("DB_DRIVER")

MILL_DB_MAP = {
    "hastings": "Smart_Eye_Jute_STIL_Hastings_Live",
    "gondalpara": "Smart_Eye_Jute_STIL_Gondalpara_Live",
    "shaktigarh": "Smart_Eye_Jute_STIL_Shaktigarh_Live"
}


print("DEBUG ENV:", DB_SERVER, DB_DATABASE, DB_DRIVER)

# -------------------------------------
# DB Connection
# -------------------------------------
def get_conn(mill: str):
    mill = mill.lower()

    if mill not in MILL_DB_MAP:
        raise ValueError("Invalid mill selected")

    db_name = MILL_DB_MAP[mill]

    conn_str = (
        f"DRIVER={{{DB_DRIVER}}};"
        f"SERVER={DB_SERVER};"
        f"DATABASE={db_name};"
        f"UID={DB_USER};"
        f"PWD={DB_PASSWORD}"
    )
    return pyodbc.connect(conn_str)


def get_schema_text(table_names, mill):
    conn = get_conn(mill)
    cursor = conn.cursor()

    lines = []

    for table in table_names:
        lines.append(f"Table: {table}")
        lines.append("Columns:")

        cursor.execute("""
            SELECT COLUMN_NAME, DATA_TYPE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = ?
            ORDER BY ORDINAL_POSITION
        """, table)

        for col, dtype in cursor.fetchall():
            lines.append(f"- {col} ({dtype})")

        lines.append("")

    conn.close()
    return "\n".join(lines)


# -------------------------------------
# FASTAPI APP
# -------------------------------------
class AskRequest(BaseModel):
    question: str
    mill: str



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------
# Health Check
# -------------------------------------
@app.get("/ping")
def ping():
    return {"status": "ok"}

# -------------------------------------
# MAIN QUERY ENGINE
# -------------------------------------
@app.post("/ask")
def ask_query(req: AskRequest):
    question = req.question

    try:
        # 1. Get schema
        schema_text = get_schema_text(
                                        ["AttendanceReport"],
                                        req.mill
                                    )


        # 2. Generate SQL via LLM
        llm_result = generate_sql_from_question(question, schema_text)

        # --- LLM unsupported handling ---
        if llm_result.get("unsupported"):
            return {
                "status": "unsupported",
                "message": "This query is not supported yet. We will work on that."
            }

        sql = llm_result.get("sql")
        params = llm_result.get("params", [])

        if not sql:
            raise ValueError("No SQL generated")

        # --- HARD SANITIZATION FOR Dept_Code ---
        if "Dept_Code" in sql:
            for i, p in enumerate(params):
                if isinstance(p, str):
                    digits = re.findall(r"\d+", p)
                    if digits:
                        params[i] = int(digits[0])
                    else:
                        raise ValueError("Invalid Dept_Code parameter")

        # 3. Validate SQL
        validate_sql(sql)

        # 4. Execute SQL safely
        conn = get_conn(req.mill)
        df = pd.read_sql(sql, conn, params=params)
        conn.close()

        return {
            "status": "ok",
            "row_count": len(df),
            "columns": df.columns.tolist(),
            "rows": df.to_dict(orient="records"),
            "sql_used": sql
        }

    except Exception:
        # --- FINAL SAFE FALLBACK ---
        return {
            "status": "unsupported",
            "message": "This query is not supported yet. We will work on that."
        }


# -------------------------------------
# TEST DB ENDPOINT
# -------------------------------------
@app.get("/test-db")
def test_db():
    try:
        conn = get_conn()
        df = pd.read_sql("SELECT TOP 5 * FROM AttendanceReport", conn)
        conn.close()
        return {
            "status": "ok",
            "rows": df.to_dict(orient="records")
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    print(get_schema_text(["AttendanceReport"]))
