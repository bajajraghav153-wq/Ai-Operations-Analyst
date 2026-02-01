import google.generativeai as genai
import pandas as pd
import re
from utils.prompts import SYSTEM_PROMPT

def clean_text(text: str) -> str:
    # Remove broken spacing between letters
    text = re.sub(r'(?<=\w)\s+(?=\w)', ' ', text)

    # Remove weird markdown artifacts
    text = text.replace('∗∗', '**')

    # Remove double spaces
    text = re.sub(r'\s{2,}', ' ', text)

    return text.strip()

def analyze_data(df: pd.DataFrame, api_key: str, model_name: str):
    genai.configure(api_key=api_key)

    model = genai.GenerativeModel(model_name)

    summary = df.describe(include="all").to_string()

    prompt = f"""
{SYSTEM_PROMPT}

Business data summary:

{summary}

Provide the analysis now.
"""

    response = model.generate_content(prompt)

    cleaned_output = clean_text(response.text)

    return cleaned_output
