import streamlit as st
import os
from dotenv import load_dotenv

from utils.data_loader import load_csv
from utils.analyzer import analyze_data

# -------------------------------------------------
# ENV
# -------------------------------------------------
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="AI Operations Analyst",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -------------------------------------------------
# GLOBAL DARK THEME CSS
# -------------------------------------------------
st.markdown(
    """
    <style>
    /* App background */
    .stApp {
        background-color: #0b0f14;
        color: #e5e7eb;
    }

    /* Main container */
    .block-container {
        padding: 2rem 2.5rem;
    }

    /* Headings */
    h1, h2, h3, h4 {
        color: #f9fafb;
        font-weight: 600;
    }

    /* Cards */
    .card {
        background: #111827;
        border: 1px solid #1f2937;
        border-radius: 16px;
        padding: 22px;
        margin-bottom: 20px;
    }

    /* Muted text */
    .muted {
        color: #9ca3af;
        font-size: 14px;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #6366f1, #4f46e5);
        color: white;
        border-radius: 12px;
        padding: 0.6rem 1.2rem;
        border: none;
        font-weight: 600;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #4f46e5, #4338ca);
        color: white;
    }

    /* File uploader */
    section[data-testid="stFileUploader"] {
        background: #0f172a;
        border: 1px dashed #334155;
        padding: 16px;
        border-radius: 12px;
    }

    /* Selectbox */
    div[data-baseweb="select"] > div {
        background-color: #0f172a;
        border-color: #334155;
        color: #e5e7eb;
    }

    /* Dataframe */
    .stDataFrame {
        background-color: #0f172a;
        border-radius: 12px;
        border: 1px solid #1f2937;
    }

    /* Expander */
    details {
        background: #0f172a;
        border-radius: 12px;
        border: 1px solid #1f2937;
        padding: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------------------------------------
# HEADER
# -------------------------------------------------
st.markdown(
    """
    <div class="card">
        <h1>📊 AI Operations Analyst</h1>
        <p class="muted">
        AI-powered business analysis for founders, agencies, and operators.
        Identify profit leaks, inefficiencies, and risks in minutes.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# -------------------------------------------------
# LAYOUT
# -------------------------------------------------
left, right = st.columns([1, 2.3])

# -------------------------------------------------
# LEFT PANEL – INPUTS
# -------------------------------------------------
with left:
    st.markdown(
        """
        <div class="card">
            <h3>📂 Upload Business Data</h3>
            <p class="muted">Upload a CSV with revenue, expenses, hours, or projects.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    uploaded_file = st.file_uploader("", type=["csv"])

    st.markdown(
        """
        <div class="card">
            <h3>🤖 AI Model</h3>
            <p class="muted">Select any official Google Gemini model.</p>
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
        "",
        list(MODEL_OPTIONS.keys())
    )

    selected_model = MODEL_OPTIONS[selected_model_label]

    st.markdown(
        f"""
        <div class="card">
            <p class="muted">Selected model</p>
            <b>{selected_model}</b>
        </div>
        """,
        unsafe_allow_html=True
    )

# -------------------------------------------------
# RIGHT PANEL – OUTPUT
# -------------------------------------------------
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

            if st.button("🧠 Run AI Analysis", use_container_width=True):
                if not GEMINI_API_KEY:
                    st.error("Gemini API key is missing.")
                else:
                    with st.spinner("Analyzing your business…"):
                        insights = analyze_data(
                            df=df,
                            api_key=GEMINI_API_KEY,
                            model_name=selected_model
                        )

                    # -----------------------------
                    # EXECUTIVE SUMMARY
                    # -----------------------------
                    st.markdown(
                        """
                        <div class="card">
                            <h2>🧠 Executive Summary</h2>
                            <p class="muted">Key findings you should act on immediately</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    st.markdown(insights.split("##")[0])

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
