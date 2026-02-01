import streamlit as st
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
Upload your business data and choose the AI model you want.

Different models give different trade-offs:
- Speed
- Cost
- Depth of analysis
""")

# 🔹 MODEL SELECTION (YOU CONTROL THIS LIST)
MODEL_OPTIONS = {
    "Gemini 3 Flash (Fast & Cheap)": "models/gemini-3.0-flash-preview",
    "Gemini 1.5 Flash (Balanced)": "models/gemini-1.5-flash",
    "Gemini 1.5 Pro (Deep Analysis)": "models/gemini-1.5-pro"
}

selected_model_label = st.selectbox(
    "🤖 Select AI Model",
    list(MODEL_OPTIONS.keys())
)

selected_model = MODEL_OPTIONS[selected_model_label]

st.info(f"Selected model: `{selected_model}`")

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
                    insights = analyze_data(
                        df=df,
                        api_key=GEMINI_API_KEY,
                        model_name=selected_model
                    )

                st.markdown("## 📌 Key Business Insights")
                st.write(insights)
