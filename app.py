import streamlit as st
import os
from dotenv import load_dotenv

from utils.data_loader import load_csv
from utils.analyzer import analyze_data

# Load env variables
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

st.info("💡 Tip: Use the sample CSV from the GitHub repository to test the app.")

uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

if uploaded_file:
    df = load_csv(uploaded_file)

    if df is None:
        st.error("Could not read the CSV file.")
    else:
        st.success("CSV uploaded successfully")

        st.dataframe(df.head(20))

        if st.button("🧠 Analyze My Business"):
            if not GEMINI_API_KEY:
                st.error("Gemini API key is missing.")
            else:
                with st.spinner("Analyzing your business..."):
                    insights = analyze_data(df, GEMINI_API_KEY)

                st.markdown("## 📌 Key Business Insights")
                st.write(insights)
