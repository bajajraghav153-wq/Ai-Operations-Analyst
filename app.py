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
# Global Styling (UI FIX)
# -----------------------------
st.markdown(
    """
    <style>
    .main {
        background-color: #0e1117;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    h1, h2, h3 {
        color: #ffffff;
    }
    .card {
        background: #161b22;
        padding: 20px;
        border-radius: 14px;
        margin-bottom: 20px;
        border: 1px solid #30363d;
    }
    .muted {
        color: #9ba3af;
        font-size: 14px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# Header
# -----------------------------
st.markdown(
    """
    <div class="card">
        <h1>📊 AI Operations Analyst</h1>
        <p class="muted">
        Turn messy business data into clear profit decisions.
        Built for founders, operators, and consultants.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# Layout Columns
# -----------------------------
left, right = st.columns([1, 2])

# -----------------------------
# LEFT SIDEBAR (INPUTS)
# -----------------------------
with left:
    st.markdown(
        """
        <div class="card">
            <h3>📂 Upload Data</h3>
            <p class="muted">
            Upload revenue, expense, or project CSV data.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    uploaded_file = st.file_uploader(
        "Upload CSV file",
        type=["csv"]
    )

    st.markdown(
        """
        <div class="card">
            <h3>🤖 AI Model</h3>
            <p class="muted">
            Choose any Gemini model (official names).
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    MODEL_OPTIONS = {
        "gemini-3-pro-preview": "gemini-3-pro-preview",
        "gemini-3-pro-image-preview": "gemini-3-pro-image-preview",
        "gemini-3-flash-preview": "gemini-3-flash-preview",
        "gemini-2.5-flash": "gemini-2.5-flash",
        "gemini-2.5-flash-preview-09-2025": "gemini-2.5-flash-preview-09-2025",
        "gemini-2.5-flash-preview-12-2025": "gemini-2.5-flash-preview-12-2025"
    }

    selected_model_label = st.selectbox(
        "Select Gemini Model",
        list(MODEL_OPTIONS.keys())
    )

    selected_model = MODEL_OPTIONS[selected_model_label]

    st.markdown(
        f"""
        <div class="card">
            <p class="muted">
            Selected model:<br>
            <b>{selected_model}</b>
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

# -----------------------------
# RIGHT SIDE (OUTPUT)
# -----------------------------
with right:
    if uploaded_file:
        df = load_csv(uploaded_file)

        if df is None:
            st.error("Failed to read CSV file.")
        else:
            st.markdown(
                """
                <div class="card">
                    <h3>🔍 Data Preview</h3>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.dataframe(df.head(15), use_container_width=True)

            if st.button("🧠 Analyze Business", use_container_width=True):
                if not GEMINI_API_KEY:
                    st.error("Gemini API key is missing.")
                else:
                    with st.spinner("Analyzing business performance..."):
                        insights = analyze_data(
                            df=df,
                            api_key=GEMINI_API_KEY,
                            model_name=selected_model
                        )

                    # -----------------------------
                    # EXECUTIVE SUMMARY (NEW)
                    # -----------------------------
                    st.markdown(
                        """
                        <div class="card">
                            <h2>🧠 Executive Summary</h2>
                            <p class="muted">
                            One-minute overview for decision makers
                            </p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    # Extract top bullets automatically
                    summary_prompt = """
                    From the analysis below, extract ONLY 5 bullets:
                    - Each bullet must be one clear business insight
                    - Focus on money, risk, or efficiency
                    - No extra text

                    Analysis:
                    """

                    summary_text = analyze_data(
                        df=df,
                        api_key=GEMINI_API_KEY,
                        model_name=selected_model
                    )

                    st.markdown(summary_text)

                    # -----------------------------
                    # FULL INSIGHTS
                    # -----------------------------
                    st.markdown(
                        """
                        <div class="card">
                            <h2>📌 Detailed Insights</h2>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    st.markdown(insights)
