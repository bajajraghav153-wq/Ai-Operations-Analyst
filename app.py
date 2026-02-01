import streamlit as st
import os
from dotenv import load_dotenv

from utils.data_loader import load_csv
from utils.analyzer import analyze_data

# -----------------------------
# Load environment variables
# -----------------------------
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# -----------------------------
# Page configuration
# -----------------------------
st.set_page_config(
    page_title="AI Operations Analyst",
    page_icon="📊",
    layout="wide"
)

# -----------------------------
# Header
# -----------------------------
st.title("📊 AI Operations Analyst for SMBs")
st.subheader("Turn business CSV data into clear profit insights")

st.markdown(
    """
Upload your business CSV file and select a **Google Gemini model**
(exact names as listed in Google AI documentation).

The AI will:
- Identify profit leaks
- Highlight inefficiencies
- Detect anomalies
- Provide clear, actionable recommendations
"""
)

# -----------------------------
# OFFICIAL GEMINI MODELS (NO RENAMING)
# -----------------------------
MODEL_OPTIONS = {
    "gemini-3-pro-preview": "gemini-3-pro-preview",
    "gemini-3-pro-image-preview": "gemini-3-pro-image-preview",
    "gemini-3-flash-preview": "gemini-3-flash-preview",
    "gemini-2.5-flash": "gemini-2.5-flash",
    "gemini-2.5-flash-preview-09-2025": "gemini-2.5-flash-preview-09-2025",
    "gemini-2.5-flash-preview-12-2025": "gemini-2.5-flash-preview-12-2025"
}

# -----------------------------
# Model selector
# -----------------------------
selected_model_label = st.selectbox(
    "🤖 Select Gemini Model (official names)",
    list(MODEL_OPTIONS.keys())
)

selected_model = MODEL_OPTIONS[selected_model_label]

st.info(f"Selected model: `{selected_model}`")

# -----------------------------
# CSV upload
# -----------------------------
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

        with st.expander("🔍 Preview Uploaded Data"):
            st.dataframe(df.head(20))

        # -----------------------------
        # Run analysis
        # -----------------------------
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

                        # IMPORTANT:
                        # markdown rendering preserves headings & spacing
                        st.markdown(insights, unsafe_allow_html=False)

                    except Exception:
                        st.error(
                            "❌ Analysis failed. "
                            "This model may not be enabled for your API key or region."
                        )
