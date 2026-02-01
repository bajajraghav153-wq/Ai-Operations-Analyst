import streamlit as st
import os
import re
import pandas as pd
from io import BytesIO
from dotenv import load_dotenv

from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.lib.units import inch

from utils.data_loader import load_csv
from utils.analyzer import analyze_data

# =================================================
# CONFIG
# =================================================
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

st.set_page_config(
    page_title="AI Operations Analyst",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =================================================
# DARK SAAS THEME (LOCKED)
# =================================================
st.markdown(
    """
    <style>
    .stApp { background:#0b0f14; color:#e5e7eb; }
    .block-container { padding:1.8rem 2.5rem; }

    h1,h2,h3 { color:#f9fafb; font-weight:600; }

    .card {
        background:linear-gradient(180deg,#111827,#0f172a);
        border:1px solid #1f2937;
        border-radius:16px;
        padding:20px;
        margin-bottom:16px;
    }

    .muted { color:#9ca3af; font-size:14px; }

    .stButton>button {
        width:100%;
        background:linear-gradient(135deg,#6366f1,#4f46e5);
        color:white;
        border-radius:14px;
        padding:0.7rem;
        font-weight:600;
        border:none;
    }

    section[data-testid="stFileUploader"] {
        background:#0f172a;
        border:1px dashed #334155;
        padding:14px;
        border-radius:12px;
    }

    .stDataFrame {
        background:#0f172a;
        border-radius:14px;
        border:1px solid #1f2937;
    }

    .stDataFrame thead th {
        background:#020617 !important;
        color:#c7d2fe !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =================================================
# PDF HELPERS (CONSULTANT-GRADE)
# =================================================
def clean_analysis_for_pdf(text: str) -> list[str]:
    paragraphs, buf = [], []

    for line in text.split("\n"):
        line = re.sub(r"[#*]", "", line).strip()
        if not line:
            continue
        if line.lower().startswith((
            "analysis overview", "profit leaks", "inefficiencies",
            "anomalies", "actionable"
        )):
            continue

        buf.append(line)

        if len(buf) >= 2:
            paragraphs.append(" ".join(buf))
            buf = []

        if len(paragraphs) >= 6:
            break

    if buf and len(paragraphs) < 6:
        paragraphs.append(" ".join(buf))

    return paragraphs


def generate_pdf(exec_bullets, insight_paragraphs, metrics_df):
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=42,
        leftMargin=42,
        topMargin=48,
        bottomMargin=42
    )

    styles = getSampleStyleSheet()

    title = ParagraphStyle(
        "Title",
        fontSize=22,
        textColor=HexColor("#1F3A5F"),
        alignment=1,
        spaceAfter=20
    )

    section = ParagraphStyle(
        "Section",
        fontSize=14,
        textColor=HexColor("#1F3A5F"),
        spaceBefore=18,
        spaceAfter=10
    )

    body = ParagraphStyle(
        "Body",
        fontSize=10.5,
        leading=15,
        textColor=HexColor("#111827"),
        spaceAfter=10
    )

    bullet = ParagraphStyle(
        "Bullet",
        fontSize=10.5,
        leading=15,
        leftIndent=16,
        bulletIndent=6,
        spaceAfter=8
    )

    muted = ParagraphStyle(
        "Muted",
        fontSize=9,
        textColor=HexColor("#4B5563"),
        spaceAfter=12
    )

    elements = []

    # PAGE 1
    elements.append(Paragraph("AI Operations Analysis Report", title))
    elements.append(Paragraph(
        "Prepared as an independent operational review.<br/>"
        "Confidential – Internal Business Use Only",
        muted
    ))
    elements.append(Spacer(1, 0.4 * inch))

    elements.append(Paragraph("Executive Summary", section))
    for b in exec_bullets[:5]:
        elements.append(Paragraph(f"• {b}", bullet))

    elements.append(PageBreak())

    # PAGE 2
    elements.append(Paragraph("Key Financial Metrics", section))
    table_data = [metrics_df.columns.tolist()] + metrics_df.round(0).values.tolist()
    table = Table(table_data, colWidths=[90, 70, 70, 70, 60])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), HexColor("#E5E7EB")),
        ("TEXTCOLOR", (0,0), (-1,0), HexColor("#1F3A5F")),
        ("GRID", (0,0), (-1,-1), 0.5, HexColor("#CBD5E1")),
        ("FONT", (0,0), (-1,0), "Helvetica-Bold"),
        ("ALIGN", (1,1), (-1,-1), "RIGHT"),
    ]))
    elements.append(table)

    elements.append(Spacer(1, 0.4 * inch))
    elements.append(Paragraph("Operational Insights", section))

    for p in insight_paragraphs:
        elements.append(Paragraph(p, body))

    elements.append(Spacer(1, 0.4 * inch))
    elements.append(Paragraph(
        "This report is intended to support management decision-making "
        "and should be interpreted alongside professional judgment.",
        muted
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer

# =================================================
# HEADER
# =================================================
st.markdown(
    """
    <div class="card">
        <h1>📊 AI Operations Analyst</h1>
        <p class="muted">
        Consultant-grade operational intelligence with visuals & reports.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# =================================================
# LAYOUT
# =================================================
left, right = st.columns([1, 2.4])

# =================================================
# LEFT PANEL
# =================================================
with left:
    st.markdown("<div class='card'><h3>⚙️ Control Panel</h3>", unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

    MODEL_OPTIONS = {
        "gemini-3-flash-preview": "gemini-3-flash-preview",
        "gemini-3-pro-preview": "gemini-3-pro-preview",
        "gemini-2.5-flash": "gemini-2.5-flash"
    }

    selected_model = MODEL_OPTIONS[
        st.selectbox("Gemini Model", MODEL_OPTIONS.keys())
    ]

    st.markdown(f"<p class='muted'>Model: <b>{selected_model}</b></p></div>",
                unsafe_allow_html=True)

# =================================================
# RIGHT PANEL
# =================================================
with right:
    if uploaded_file:
        df = load_csv(uploaded_file)

        df["profit"] = df["revenue"] - df["expenses"]
        df["margin"] = (df["profit"] / df["revenue"]) * 100

        st.markdown("<div class='card'><h3>📄 Data Preview</h3></div>",
                    unsafe_allow_html=True)
        st.dataframe(df, use_container_width=True)

        if st.button("🚀 Run AI Analysis"):
            with st.spinner("Analyzing business performance…"):
                detailed = analyze_data(df, GEMINI_API_KEY, selected_model)

                summary_prompt = f"""
You are a senior business consultant.
Create EXACTLY 5 executive-level bullets.
No headings. No raw statistics. Advisory tone.

Analysis:
{detailed}
"""
                summary_text = analyze_data(df, GEMINI_API_KEY, selected_model)

            exec_bullets = [
                b.strip("- ").strip()
                for b in summary_text.split("\n")
                if b.strip()
            ][:5]

            insights = clean_analysis_for_pdf(detailed)

            # EXEC SUMMARY
            st.markdown("<div class='card'><h2>🧠 Executive Summary</h2></div>",
                        unsafe_allow_html=True)
            for b in exec_bullets:
                st.markdown(f"- {b}")

            # VISUALS
            st.markdown("<div class='card'><h2>📊 Visual Insights</h2></div>",
                        unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                st.subheader("Profit by Client")
                st.bar_chart(df.set_index("client")["profit"])
            with c2:
                st.subheader("Hours vs Revenue")
                st.scatter_chart(df[["hours_worked", "revenue"]])

            st.subheader("Expenses vs Revenue")
            st.scatter_chart(df[["expenses", "revenue"]])

            # DETAILED
            st.markdown("<div class='card'><h2>📌 Detailed Analysis</h2></div>",
                        unsafe_allow_html=True)
            for p in insights:
                st.markdown(p)

            # PDF
            metrics = df[["client", "revenue", "expenses", "profit", "margin"]]
            pdf = generate_pdf(exec_bullets, insights, metrics)

            st.download_button(
                "⬇️ Download Consultant PDF",
                data=pdf,
                file_name="AI_Operations_Analysis_Report.pdf",
                mime="application/pdf"
            )
