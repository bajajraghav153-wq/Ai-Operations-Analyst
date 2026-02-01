import streamlit as st
import os
from dotenv import load_dotenv
import pandas as pd
from io import BytesIO

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor

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
# DARK THEME
# -------------------------------------------------
st.markdown(
    """
    <style>
    .stApp { background-color: #0b0f14; color: #e5e7eb; }
    .card {
        background: #111827;
        border: 1px solid #1f2937;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 16px;
    }
    .muted { color: #9ca3af; font-size: 14px; }
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #6366f1, #4f46e5);
        color: white;
        border-radius: 14px;
        padding: 0.7rem;
        font-weight: 600;
        border: none;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------------------------------------
# PDF GENERATION FUNCTION
# -------------------------------------------------
def generate_pdf(exec_summary, insights, metrics_df):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    title = Paragraph("<b>AI Operations Analysis Report</b>", styles["Title"])
    elements.append(title)
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("<b>Executive Summary</b>", styles["Heading2"]))
    elements.append(Spacer(1, 8))
    elements.append(Paragraph(exec_summary.replace("\n", "<br/>"), styles["BodyText"]))
    elements.append(Spacer(1, 16))

    elements.append(Paragraph("<b>Key Metrics</b>", styles["Heading2"]))
    table_data = [metrics_df.columns.tolist()] + metrics_df.values.tolist()

    table = Table(table_data, hAlign="LEFT")
    table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), HexColor("#E5E7EB")),
            ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#9CA3AF")),
            ("FONT", (0, 0), (-1, 0), "Helvetica-Bold")
        ])
    )
    elements.append(table)
    elements.append(Spacer(1, 16))

    elements.append(Paragraph("<b>Detailed Analysis</b>", styles["Heading2"]))
    elements.append(Spacer(1, 8))
    elements.append(Paragraph(insights.replace("\n", "<br/>"), styles["BodyText"]))

    doc.build(elements)
    buffer.seek(0)
    return buffer

# -------------------------------------------------
# HEADER
# -------------------------------------------------
st.markdown(
    """
    <div class="card">
        <h1>📊 AI Operations Analyst</h1>
        <p class="muted">Consultant-grade business analysis & reporting</p>
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
    st.markdown("<div class='card'><h3>⚙️ Control Panel</h3>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

    MODEL_OPTIONS = {
        "gemini-3-pro-preview": "gemini-3-pro-preview",
        "gemini-3-flash-preview": "gemini-3-flash-preview",
        "gemini-2.5-flash": "gemini-2.5-flash"
    }

    selected_model_label = st.selectbox("Gemini Model", list(MODEL_OPTIONS.keys()))
    selected_model = MODEL_OPTIONS[selected_model_label]
    st.markdown(f"<p class='muted'>Selected model: <b>{selected_model}</b></p></div>", unsafe_allow_html=True)

# -------------------------------------------------
# RIGHT: OUTPUT
# -------------------------------------------------
with right:
    if uploaded_file:
        df = load_csv(uploaded_file)
        if df is None:
            st.error("Failed to read CSV.")
        else:
            df["profit"] = df["revenue"] - df["expenses"]
            df["margin"] = (df["profit"] / df["revenue"]) * 100

            st.markdown("<div class='card'><h3>📄 Data Preview</h3></div>", unsafe_allow_html=True)
            st.dataframe(df, use_container_width=True)

            if st.button("🚀 Run AI Analysis"):
                with st.spinner("Analyzing…"):
                    insights = analyze_data(df, GEMINI_API_KEY, selected_model)

                    exec_summary_prompt = f"""
Extract EXACTLY 5 bullet points for an executive summary.
Focus on money, efficiency, and risk.

Analysis:
{insights}
"""
                    exec_summary = analyze_data(df, GEMINI_API_KEY, selected_model)

                st.markdown("<div class='card'><h2>🧠 Executive Summary</h2></div>", unsafe_allow_html=True)
                st.markdown(exec_summary)

                st.markdown("<div class='card'><h2>📌 Detailed Analysis</h2></div>", unsafe_allow_html=True)
                st.markdown(insights)

                # -----------------------------
                # PDF EXPORT
                # -----------------------------
                metrics = df[["client", "revenue", "expenses", "profit", "margin"]]
                pdf_file = generate_pdf(exec_summary, insights, metrics)

                st.download_button(
                    "⬇️ Download PDF Report",
                    data=pdf_file,
                    file_name="AI_Operations_Analysis_Report.pdf",
                    mime="application/pdf"
                )
