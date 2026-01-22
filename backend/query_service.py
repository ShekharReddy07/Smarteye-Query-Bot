import pandas as pd
import re
from backend.llm_engine import generate_sql_from_question
from backend.sql_guard import validate_sql
from backend.main import get_conn, get_schema_text


def run_query(question: str):
    schema_text = get_schema_text(["AttendanceReport"])

    llm_result = generate_sql_from_question(question, schema_text)

    if llm_result.get("unsupported"):
        return {
            "status": "unsupported",
            "message": "This query is not supported yet. We will work on that."
        }

    sql = llm_result.get("sql")
    params = llm_result.get("params", [])

    if not sql:
        return {"status": "invalid", "message": "Invalid query"}

    # Dept_Code safety
    if "Dept_Code" in sql:
        for i, p in enumerate(params):
            if isinstance(p, str):
                digits = re.findall(r"\d+", p)
                if not digits:
                    return {"status": "invalid", "message": "Invalid query"}
                params[i] = int(digits[0])

    validate_sql(sql)

    conn = get_conn()
    df = pd.read_sql(sql, conn, params=params)
    conn.close()

    return {
        "status": "ok",
        "row_count": len(df),
        "columns": df.columns.tolist(),
        "rows": df.to_dict(orient="records"),
        "sql_used": sql
    }
