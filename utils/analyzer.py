import google.generativeai as genai
from utils.prompts import SYSTEM_PROMPT
import pandas as pd

def analyze_data(df: pd.DataFrame, api_key: str):
    genai.configure(api_key=api_key)

    model = genai.GenerativeModel("gemini-1.5-flash")

    summary = df.describe(include="all").to_string()

    prompt = f"""
Here is a summary of business data:

{summary}

Tasks:
1. Identify profit leaks
2. Identify inefficient clients or projects
3. Highlight cost anomalies
4. Suggest 5 clear actions to increase profit
"""

    response = model.generate_content(
        SYSTEM_PROMPT + "\n\n" + prompt
    )

    return response.text
