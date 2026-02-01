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
from reportlab.lib.units import inch

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
# DARK SAAS THEME
# -------------------------------------------------
st.markdown(
    """
    <style>
    .stApp { background-color: #0b0f14; color: #e5e7eb; }
    .block-container { padding: 1.8rem 2.5rem; }
    h1, h2, h3 { color: #f9fafb; font-weight: 600; }

    .card {
        background: linear-gradient(180deg, #111827, #0f172a);
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

    section[data-testid="stFileUploader"] {
        background: #0f172a;
        border: 1px dashed #334155;
        padding: 14px;
        border-radius: 12px;
    }

    .stDataFrame {
        background-color: #0f172a;
        border-radius: 14px;
        border: 1px solid #1f2937;
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
# PDF GENERATION (CONSULTANT GRADE)
# -------------------------------------------------
def generate_pdf(exec_summary, detailed_analysis, metrics_df):
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=48,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleStyle",
        fontSize=22,
        leading=26,
        textColor=HexColor("#1F3A5F"),
        alignment=1,
        spaceAfter=20
    )

    section_style = ParagraphStyle(
        "SectionStyle",
        fontSize=15,
        leading=18,
        textColor=HexColor("#1F3A5F"),
        spaceBefore=18,
        spaceAfter=10
    )

    body_style = ParagraphStyle(
        "BodyStyle",
        fontSize=10.5,
        leading=15,
        textColor=HexColor("#111827"),
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        "BulletStyle",
        fontSize=10.5,
        leading=15,
        textColor=HexColor("#111827"),
        leftIndent=14,
        bulletIndent=6,
        spaceAfter=6
    )

    muted_style = ParagraphStyle(
        "MutedStyle",
        fontSize=9,
        textColor=HexColor("#4B5563"),
        spaceAfter=10
    )

    elements = []

    elements.append(Paragraph("AI Operations Analysis Report", title_style))
    elements.append(Paragraph(
        "Prepared by an AI Operations Analyst<br/>Confidential – Internal Use Only",
        muted_style
    ))
    elements.append(Spacer(1, 0.3 * inch))

    elements.append(Paragraph("Executive Summary", section_style))
    for line in exec_summary.split("\n"):
        if line.strip():
            elements.append(Paragraph(f"• {line.replace('-', '').strip()}", bullet_style))

    elements.append(Spacer(1, 0.3 * inch))
    elements.append(Paragraph("Key Financial Metrics", section_style))

    table_data = [metrics_df.columns.tolist()] + metrics_df.round(2).values.tolist()
    table = Table(table_data, hAlign="LEFT", colWidths=[90, 70, 70, 70, 60])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HexColor("#E5E7EB")),
        ("TEXTCOLOR", (0, 0), (-1, 0), HexColor("#1F3A5F")),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#CBD5E1")),
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
    ]))
    elements.append(table)

    elements.append(Spacer(1, 0.3 * inch))
    elements.append(Paragraph("Detailed Analysis & Recommendations", section_style))

    for line in detailed_analysis.split("\n"):
        clean = re.sub(r"[#*]", "", line).strip()
        if clean:
            elements.append(Paragraph(clean, body_style))

    elements.append(Spacer(1, 0.4 * inch))
    elements.append(Paragraph(
        "This report is a decision-support document and should be interpreted "
        "with professional judgment.",
        muted_style
    ))

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
        <p class="muted">
        Consultant-grade business analysis with AI, visuals, and reports.
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
                with st.spinner("Analyzing business performance…"):
                    detailed_analysis = analyze_data(df, GEMINI_API_KEY, selected_model)

                    summary_prompt = f"""
Extract EXACTLY 5 bullet points.
Focus on profit, cost, efficiency, and risk.

Analysis:
{detailed_analysis}
"""
                    executive_summary = analyze_data(df, GEMINI_API_KEY, selected_model)

                st.markdown("<div class='card'><h2>🧠 Executive Summary</h2></div>", unsafe_allow_html=True)
                st.markdown(executive_summary)

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

                st.markdown("<div class='card'><h2>📌 Detailed Analysis</h2></div>", unsafe_allow_html=True)
                st.markdown(detailed_analysis)

                metrics = df[["client", "revenue", "expenses", "profit", "margin"]]
                pdf = generate_pdf(executive_summary, detailed_analysis, metrics)

                st.download_button(
                    "⬇️ Download Consultant PDF",
                    data=pdf,
                    file_name="AI_Operations_Analysis_Report.pdf",
                    mime="application/pdf"
                )
