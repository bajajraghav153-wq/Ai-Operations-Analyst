import google.generativeai as genai
from utils.prompts import SYSTEM_PROMPT
import pandas as pd

def analyze_data(df: pd.DataFrame, api_key: str):
    genai.configure(api_key=api_key)

    model = genai.GenerativeModel("gemini-1.5-flash")

    data_summary = df.describe(include="all").to_string()

    user_prompt = f"""
Here is business data summary:

{data_summary}

Tasks:
1. Identify profit leaks
2. Identify inefficiencies
3. Highlight anomalies
4. Give 5 specific actions to improve profit
"""

    response = model.generate_content(
        SYSTEM_PROMPT + "\n\n" + user_prompt
    )

    return response.text
