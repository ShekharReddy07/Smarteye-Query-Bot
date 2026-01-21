# backend/llm_engine.py

import json
import os
from pathlib import Path
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def load_llm_instructions():
    base = Path(__file__).resolve().parent.parent / "llm"

    return {
        "instructions": (base / "instructions.md").read_text(encoding="utf-8"),
        "sql_rules": (base / "sql_rules.md").read_text(encoding="utf-8"),
        "examples": (base / "examples.md").read_text(encoding="utf-8"),
    }


def generate_sql_from_question(question: str, schema_text: str):
    llm_files = load_llm_instructions()

    prompt = f"""
{llm_files['instructions']}

{llm_files['sql_rules']}

SCHEMA:
{schema_text}

EXAMPLES:
{llm_files['examples']}

USER QUESTION:
{question}

Return ONLY valid JSON.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a SQL generation engine."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    raw_output = response.choices[0].message.content.strip()

    try:
        return json.loads(raw_output)
    except json.JSONDecodeError:
        raise ValueError(f"LLM returned invalid JSON:\n{raw_output}")
