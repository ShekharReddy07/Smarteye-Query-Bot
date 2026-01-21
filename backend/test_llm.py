from main import get_schema_text
from llm_engine import generate_sql_from_question

if __name__ == "__main__":
    schema = get_schema_text(["AttendanceReport"])

    question = "show attendance of nz1073 yesterday"

    result = generate_sql_from_question(question, schema)
    print(result)
