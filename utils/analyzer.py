import google.generativeai as genai
from utils.prompts import SYSTEM_PROMPT
import pandas as pd

def analyze_data(df: pd.DataFrame, api_key: str):
    # Configure Gemini
    genai.configure(api_key=api_key)

    # Gemini 3 Flash Preview model
    model = genai.GenerativeModel(
        model_name="models/gemini-3.0-flash-preview"
    )

    # Summarize data for AI
    summary = df.describe(include="all").to_string()

    prompt = f"""
Here is a summary of business data:

{summary}

Tasks:
1. Identify profit leaks
2. Identify inefficient clients or projects
3. Detect unusual costs or anomalies
4. Suggest 5 very specific actions to improve profitability

Explain everything in simple business language.
"""

    response = model.generate_content(
        SYSTEM_PROMPT + "\n\n" + prompt
    )

    return response.text
