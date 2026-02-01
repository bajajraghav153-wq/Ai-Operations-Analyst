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
# HELPER FUNCTIONS (CRITICAL)
# -------------------------------------------------
def clean_text_for_pdf(text: str) -> list[str]:
    """
    Convert AI output into clean consultant-style paragraphs.
    """
    lines = []
    for line in text.split("\n"):
        line = re.sub(r"[#*]", "", line).strip()
        if not line:
            continue
        if line.lower().startswith((
            "analysis overview",
            "profit leaks",
            "inefficiencies",
            "anomalies",
            "actionable"
        )):
            continue
        lines.append(line)
    return lines


def generate_pdf(exec_summary_bullets, detailed_text_lines, metrics_df):
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=42,
        leftMargin=42,
        topMargin=48,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    title = ParagraphStyle(
        "Title",
        fontSize=22,
        textColor=HexColor("#1F3A5F"),
        alignment=1,
        spaceAfter=18
    )

    section = ParagraphStyle(
        "Section",
        fontSize=14,
        textColor=HexColor("#1F3A5F"),
        spaceBefore=18,
        spaceAfter=8
    )

    body = ParagraphStyle(
        "Body",
        fontSize=10.5,
        leading=15,
        textColor=HexColor("#111827"),
        spaceAfter=6
    )

    bullet = ParagraphStyle(
        "Bullet",
        fontSize=10.5,
        leading=15,
        leftIndent=16,
        bulletIndent=6,
        spaceAfter=6
    )

    muted = ParagraphStyle(
        "Muted",
        fontSize=9,
        textColor=HexColor("#4B5563"),
        spaceAfter=10
    )

    elements = []

    # ---------------- TITLE ----------------
    elements.append(Paragraph("AI Operations Analysis Report", title))
    elements.append(Paragraph(
        "Prepared as an independent operational review.<br/>Confidential – Internal Use Only",
        muted
    ))
    elements.append(Spacer(1, 0.3 * inch))

    # ---------------- EXEC SUMMARY ----------------
    elements.append(Paragraph("Executive Summary", section))
    for b in exec_summary_bullets:
        elements.append(Paragraph(f"• {b}", bullet))

    # ---------------- METRICS ----------------
    elements.append(Spacer(1, 0.3 * inch))
    elements.append(Paragraph("Key Financial Metrics", section))

    table_data = [metrics_df.columns.tolist()] + metrics_df.round(1).values.tolist()
    table = Table(table_data, colWidths=[90, 70, 70, 70, 60])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HexColor("#E5E7EB")),
        ("TEXTCOLOR", (0, 0), (-1, 0), HexColor("#1F3A5F")),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#CBD5E1")),
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
    ]))
    elements.append(table)

    # ---------------- DETAILED ----------------
    elements.append(Spacer(1, 0.3 * inch))
    elements.append(Paragraph("Detailed Observations & Recommendations", section))
    for line in detailed_text_lines:
        elements.append(Paragraph(line, body))

    # ---------------- FOOTER ----------------
    elements.append(Spacer(1, 0.4 * inch))
    elements.append(Paragraph(
        "This document is intended to support management decision-making "
        "and should be interpreted in context of broader business judgment.",
        muted
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer

# -------------------------------------------------
# UI (UNCHANGED CORE)
# -------------------------------------------------
st.markdown(
    "<h1>📊 AI Operations Analyst</h1>",
    unsafe_allow_html=True
)

uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

if uploaded_file:
    df = load_csv(uploaded_file)
    df["profit"] = df["revenue"] - df["expenses"]
    df["margin"] = (df["profit"] / df["revenue"]) * 100

    if st.button("Run Analysis"):
        detailed_analysis = analyze_data(df, GEMINI_API_KEY, "gemini-2.5-flash")

        # --- Executive summary PROMPT ---
        summary_prompt = f"""
You are a senior business consultant.

Create EXACTLY 5 executive-level bullet points:
- No section names
- No statistics beyond rounded numbers
- Focus on decisions and implications
- Natural business language

Analysis:
{detailed_analysis}
"""

        exec_summary_text = analyze_data(df, GEMINI_API_KEY, "gemini-2.5-flash")
        exec_bullets = [b.strip("- ").strip() for b in exec_summary_text.split("\n") if b.strip()][:5]

        clean_lines = clean_text_for_pdf(detailed_analysis)

        metrics = df[["client", "revenue", "expenses", "profit", "margin"]]

        pdf = generate_pdf(exec_bullets, clean_lines, metrics)

        st.download_button(
            "⬇️ Download Consultant PDF",
            data=pdf,
            file_name="AI_Operations_Analysis_Report.pdf",
            mime="application/pdf"
        )
