import streamlit as st
import os
from dotenv import load_dotenv
import pandas as pd
from io import BytesIO
import re

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
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
# PDF HELPERS
# -------------------------------------------------
def clean_for_pdf(text: str) -> str:
    """Remove markdown artifacts for PDF"""
    text = re.sub(r"##+", "", text)
    text = re.sub(r"\*\*", "", text)
    return text.strip()

def generate_pdf(exec_summary, detailed_analysis, metrics_df):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=36, leftMargin=36)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Title"],
        textColor=HexColor("#111827")
    )

    heading_style = ParagraphStyle(
        "HeadingStyle",
        parent=styles["Heading2"],
        spaceBefore=14,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        "BodyStyle",
        parent=styles["BodyText"],
        spaceAfter=6
    )

    elements = []

    elements.append(Paragraph("AI Operations Analysis Report", title_style))
    elements.append(Spacer(1, 16))

    elements.append(Paragraph("Executive Summary", heading_style))
    for line in exec_summary.split("\n"):
        if line.strip():
            elements.append(Paragraph(line, body_style))

    elements.append(Spacer(1, 16))
    elements.append(Paragraph("Key Metrics", heading_style))

    table_data = [metrics_df.columns.tolist()] + metrics_df.round(2).values.tolist()
    table = Table(table_data, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HexColor("#E5E7EB")),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#9CA3AF")),
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(table)

    elements.append(Spacer(1, 16))
    elements.append(Paragraph("Detailed Analysis", heading_style))

    for line in clean_for_pdf(detailed_analysis).split("\n"):
        if line.strip():
            elements.append(Paragraph(line, body_style))

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
        <p class="muted">Consultant-grade business insights with visuals & reports</p>
    </div>
    """,
    unsafe_allow_html=True
)

# -------------------------------------------------
# LAYOUT
# -------------------------------------------------
left, right = st.columns([1, 2.4])

# -------------------------------------------------
# LEFT PANEL
# -------------------------------------------------
with left:
    st.markdown("<div class='card'><h3>⚙️ Control Panel</h3>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

    MODEL_OPTIONS = {
        "gemini-3-pro-preview": "gemini-3-pro-preview",
        "gemini-3-flash-preview": "gemini-3-flash-preview",
        "gemini-2.5-flash": "gemini-2.5-flash",
    }
    selected_model = MODEL_OPTIONS[
        st.selectbox("Gemini Model", MODEL_OPTIONS.keys())
    ]
    st.markdown(f"<p class='muted'>Model: <b>{selected_model}</b></p></div>", unsafe_allow_html=True)

# -------------------------------------------------
# RIGHT PANEL
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
                    detailed_analysis = analyze_data(df, GEMINI_API_KEY, selected_model)

                    summary_prompt = f"""
Extract EXACTLY 5 bullet points for an executive summary.
Only bullets. Focus on profit, risk, efficiency.

Analysis:
{detailed_analysis}
"""
                    exec_summary = analyze_data(df, GEMINI_API_KEY, selected_model)

                # -----------------------------
                # EXEC SUMMARY
                # -----------------------------
                st.markdown("<div class='card'><h2>🧠 Executive Summary</h2></div>", unsafe_allow_html=True)
                st.markdown(exec_summary)

                # -----------------------------
                # VISUAL CHARTS (RESTORED)
                # -----------------------------
                st.markdown("<div class='card'><h2>📊 Visual Insights</h2></div>", unsafe_allow_html=True)

                c1, c2 = st.columns(2)
                with c1:
                    st.subheader("Profit by Client")
                    st.bar_chart(df.set_index("client")["profit"])
                with c2:
                    st.subheader("Hours vs Revenue")
                    st.scatter_chart(df[["hours_worked", "revenue"]])

                st.subheader("Expenses vs Revenue")
                st.scatter_chart(df[["expenses", "revenue"]])

                # -----------------------------
                # DETAILED ANALYSIS
                # -----------------------------
                st.markdown("<div class='card'><h2>📌 Detailed Analysis</h2></div>", unsafe_allow_html=True)
                st.markdown(detailed_analysis)

                # -----------------------------
                # PDF EXPORT (FIXED)
                # -----------------------------
                metrics = df[["client", "revenue", "expenses", "profit", "margin"]]
                pdf = generate_pdf(exec_summary, detailed_analysis, metrics)

                st.download_button(
                    "⬇️ Download Consultant PDF",
                    data=pdf,
                    file_name="AI_Operations_Analysis_Report.pdf",
                    mime="application/pdf"
                )
