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
# GLOBAL DARK SAAS THEME
# -------------------------------------------------
st.markdown(
    """
    <style>
    .stApp {
        background-color: #0b0f14;
        color: #e5e7eb;
    }

    .block-container {
        padding: 1.8rem 2.5rem 2rem;
    }

    h1, h2, h3 {
        color: #f9fafb;
        font-weight: 600;
    }

    .card {
        background: linear-gradient(180deg, #111827, #0f172a);
        border: 1px solid #1f2937;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 16px;
    }

    .muted {
        color: #9ca3af;
        font-size: 14px;
        line-height: 1.5;
    }

    /* Buttons */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #6366f1, #4f46e5);
        color: white;
        border-radius: 14px;
        padding: 0.7rem 1.2rem;
        border: none;
        font-weight: 600;
        font-size: 15px;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #4f46e5, #4338ca);
    }

    /* Inputs */
    section[data-testid="stFileUploader"] {
        background: #0f172a;
        border: 1px dashed #334155;
        padding: 14px;
        border-radius: 12px;
    }

    div[data-baseweb="select"] > div {
        background-color: #0f172a;
        border-color: #334155;
        color: #e5e7eb;
        border-radius: 10px;
    }

    /* Dataframe dark */
    .stDataFrame {
        background-color: #0f172a;
        border-radius: 14px;
        border: 1px solid #1f2937;
    }

    .stDataFrame table {
        background-color: #0f172a;
        color: #e5e7eb;
    }

    .stDataFrame thead tr th {
        background-color: #020617 !important;
        color: #c7d2fe !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------------------------------------
# HERO HEADER
# -------------------------------------------------
st.markdown(
    """
    <div class="card">
        <h1>📊 AI Operations Analyst</h1>
        <p class="muted">
        AI-powered operational intelligence for founders, agencies, and SMB operators.
        Upload your data and get consultant-level insights in minutes.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# -------------------------------------------------
# LAYOUT
# -------------------------------------------------
left, right = st.columns([1, 2.4])

# -------------------------------------------------
# LEFT: CONTROL PANEL
# -------------------------------------------------
with left:
    st.markdown(
        """
        <div class="card">
            <h3>⚙️ Control Panel</h3>
            <p class="muted">
            Upload data, choose AI model, then run analysis.
            </p>
        """,
        unsafe_allow_html=True
    )

    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

    MODEL_OPTIONS = {
        "gemini-3-pro-preview": "gemini-3-pro-preview",
        "gemini-3-pro-image-preview": "gemini-3-pro-image-preview",
        "gemini-3-flash-preview": "gemini-3-flash-preview",
        "gemini-2.5-flash": "gemini-2.5-flash",
        "gemini-2.5-flash-preview-09-2025": "gemini-2.5-flash-preview-09-2025",
        "gemini-2.5-flash-preview-12-2025": "gemini-2.5-flash-preview-12-2025"
    }

    selected_model_label = st.selectbox(
        "Gemini Model",
        list(MODEL_OPTIONS.keys())
    )

    selected_model = MODEL_OPTIONS[selected_model_label]

    st.markdown(
        f"""
        <p class="muted">
        Selected model:<br>
        <b>{selected_model}</b>
        </p>
        </div>
        """,
        unsafe_allow_html=True
    )

# -------------------------------------------------
# RIGHT: OUTPUT
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
                    <h3>📄 Data Preview</h3>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.dataframe(df, use_container_width=True)

            st.markdown("<br>", unsafe_allow_html=True)

            if st.button("🚀 Run AI Analysis"):
                if not GEMINI_API_KEY:
                    st.error("Gemini API key is missing.")
                else:
                    with st.spinner("Analyzing business performance…"):
                        insights = analyze_data(
                            df=df,
                            api_key=GEMINI_API_KEY,
                            model_name=selected_model
                        )

                    st.markdown(
                        """
                        <div class="card">
                            <h2>🧠 Executive Summary</h2>
                            <p class="muted">Key insights you should act on immediately</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    st.markdown(insights.split("##")[0])

                    st.markdown(
                        """
                        <div class="card">
                            <h2>📌 Detailed Analysis</h2>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    st.markdown(insights)
