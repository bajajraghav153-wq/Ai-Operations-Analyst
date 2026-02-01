import google.generativeai as genai
from utils.prompts import SYSTEM_PROMPT
import pandas as pd

def analyze_data(df: pd.DataFrame, api_key: str, model_name: str):
    # Configure Gemini API
    genai.configure(api_key=api_key)

    # Load selected model
    model = genai.GenerativeModel(model_name=model_name)

    # Summarize dataset for reasoning
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
