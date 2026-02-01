import streamlit as st
import os
from dotenv import load_dotenv

from utils.data_loader import load_csv
from utils.analyzer import analyze_data

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Page config
st.set_page_config(
    page_title="AI Operations Analyst",
    page_icon="📊",
    layout="wide"
)

# Header
st.title("📊 AI Operations Analyst for SMBs")
st.subheader("Analyze business data using Google Gemini models")

st.markdown("""
Upload your business CSV file and choose any **Google Gemini model**
(as listed in official Google AI documentation).

The AI will:
- Find profit leaks
- Identify inefficiencies
- Detect anomalies
- Suggest clear actions
""")

# ============================
# OFFICIAL GEMINI MODELS (NO RENAMING)
# ============================
MODEL_OPTIONS = {
    "gemini-3-pro-preview": "gemini-3-pro-preview",
    "gemini-3-pro-image-preview": "gemini-3-pro-image-preview",
    "gemini-3-flash-preview": "gemini-3-flash-preview",
    "gemini-2.5-flash": "gemini-2.5-flash",
    "gemini-2.5-flash-preview-09-2025": "gemini-2.5-flash-preview-09-2025",
    "gemini-2.5-flash-preview-12-2025": "gemini-2.5-flash-preview-12-2025"
}

# Model selector
selected_model_label = st.selectbox(
    "🤖 Select Gemini Model (official names)",
    list(MODEL_OPTIONS.keys())
)

selected_model = MODEL_OPTIONS[selected_model_label]

st.info(f"Selected model: `{selected_model}`")

# File uploader
uploaded_file = st.file_uploader(
    "Upload CSV file",
    type=["csv"]
)

if uploaded_file:
    df = load_csv(uploaded_file)

    if df is None:
        st.error("❌ Failed to read CSV file.")
    else:
        st.success("✅ CSV uploaded successfully")

        with st.expander("🔍 Preview Data"):
            st.dataframe(df.head(20))

        if st.button("🧠 Analyze Business"):
            if not GEMINI_API_KEY:
                st.error("❌ Gemini API key is missing.")
            else:
                with st.spinner("Analyzing business data..."):
                    try:
                        insights = analyze_data(
                            df=df,
                            api_key=GEMINI_API_KEY,
                            model_name=selected_model
                        )

                        st.markdown("## 📌 Insights")
                        # IMPORTANT: markdown rendering (fixes broken text)
                        st.markdown(insights)

                    except Exception as e:
                        st.error(
                            "❌ Analysis failed. "
                            "This model may not be enabled for your API key or region."
                        )
