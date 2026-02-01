import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv

from utils.data_loader import load_csv
from utils.analyzer import analyze_data

# Load environment variables
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

st.set_page_config(
    page_title="AI Operations Analyst",
    page_icon="📊",
    layout="wide"
)

st.title("📊 AI Operations Analyst for SMBs")
st.subheader("Turn messy business data into clear profit insights")

st.markdown("""
Upload your business data (revenue, expenses, time tracking, clients).

The AI will:
- Find profit leaks
- Detect inefficiencies
- Explain everything in plain English
""")

uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

if uploaded_file:
    df = load_csv(uploaded_file)

    if df is None:
        st.error("Failed to read CSV file.")
    else:
        st.success("File uploaded successfully")

        with st.expander("🔍 Preview Data"):
            st.dataframe(df.head(20))

        if st.button("🧠 Analyze My Business"):
            if not GEMINI_API_KEY:
                st.error("Gemini API key missing.")
            else:
                with st.spinner("Analyzing your business..."):
                    insights = analyze_data(df, GEMINI_API_KEY)

                st.markdown("## 📌 Key Insights")
                st.write(insights)
