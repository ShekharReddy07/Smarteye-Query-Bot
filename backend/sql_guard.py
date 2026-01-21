# backend/sql_guard.py

import re

FORBIDDEN_KEYWORDS = [
    "insert", "update", "delete", "drop",
    "alter", "create", "merge", "exec",
    "truncate", "grant", "revoke"
]

ALLOWED_TABLES = {
    "attendancereport"
}


def validate_sql(sql: str):
    sql_clean = sql.strip().lower()

    # 1. Must start with SELECT
    if not sql_clean.startswith("select"):
        raise ValueError("Only SELECT queries are allowed")

    # 2. No semicolons (multi-statement protection)
    if ";" in sql_clean:
        raise ValueError("Semicolons are not allowed")

    # 3. Block forbidden keywords
    for keyword in FORBIDDEN_KEYWORDS:
        if re.search(rf"\b{keyword}\b", sql_clean):
            raise ValueError(f"Forbidden SQL keyword detected: {keyword}")

    # 4. Enforce allowed tables only
    tables = re.findall(r"from\s+([a-zA-Z0-9_]+)", sql_clean)
    for table in tables:
        if table not in ALLOWED_TABLES:
            raise ValueError(f"Access to table '{table}' is not allowed")

    return True
