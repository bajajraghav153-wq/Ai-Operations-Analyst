import google.generativeai as genai
import pandas as pd
import re
from utils.prompts import SYSTEM_PROMPT

def clean_text(text: str) -> str:
    # Fix broken markdown asterisks
    text = text.replace("∗∗", "**")

    # Remove weird unicode spaces but KEEP newlines
    text = re.sub(r"[ \t]+", " ", text)

    # Ensure headings start on new lines
    text = re.sub(r"(## )", r"\n\n## ", text)

    # Ensure bullet points start on new lines
    text = re.sub(r"(- )", r"\n- ", text)

    # Clean excessive blank lines (max 2)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()

def analyze_data(df: pd.DataFrame, api_key: str, model_name: str):
    genai.configure(api_key=api_key)

    model = genai.GenerativeModel(model_name)

    summary = df.describe(include="all").to_string()

    prompt = f"""
{SYSTEM_PROMPT}

Business data summary:
{summary}

Now produce the analysis using the required structure.
"""

    response = model.generate_content(prompt)

    return clean_text(response.text)
