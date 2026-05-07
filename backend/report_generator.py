"""
report_generator.py — PDF scan report generator using ReportLab.
Produces a single-page A4 PDF for a given scan result dict.
"""
import io
import logging
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT

logger = logging.getLogger(__name__)

# ── Color palette ──────────────────────────────────────────────────────────
CRITICAL_COLOR = colors.HexColor("#7c1e1e")
HIGH_COLOR = colors.HexColor("#dc2626")
MEDIUM_COLOR = colors.HexColor("#d97706")
LOW_COLOR = colors.HexColor("#16a34a")
BRAND_COLOR = colors.HexColor("#4f46e5")
LIGHT_GRAY = colors.HexColor("#f3f4f6")
DARK_GRAY = colors.HexColor("#374151")
WHITE = colors.white


def _get_risk_color(level: str) -> colors.Color:
    mapping = {
        "Critical": CRITICAL_COLOR,
        "High": HIGH_COLOR,
        "Medium": MEDIUM_COLOR,
        "Low": LOW_COLOR,
    }
    return mapping.get(level, DARK_GRAY)


def generate_pdf_report(scan_result: dict) -> bytes:
    """
    Generate a PDF security report from a scan result dict.

    Args:
        scan_result: Full response dict from /api/analyze

    Returns:
        bytes: Raw PDF content
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    story = []

    risk_level = scan_result.get("risk_level", "Unknown")
    risk_score = scan_result.get("risk_score", 0)
    risk_color = _get_risk_color(risk_level)
    scan_id = scan_result.get("scan_id", "N/A")
    scanned_at = scan_result.get("scanned_at", datetime.utcnow().isoformat())
    url = scan_result.get("url", "N/A")

    # ── Header ─────────────────────────────────────────────────────────────
    header_style = ParagraphStyle(
        "Header",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=22,
        textColor=WHITE,
        alignment=TA_CENTER,
        spaceAfter=4,
        backColor=BRAND_COLOR,
        borderPad=10,
    )

    header_table = Table(
        [["🔒 Security Scan Report"]],
        colWidths=[17 * cm],
    )
    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BRAND_COLOR),
        ("TEXTCOLOR", (0, 0), (-1, -1), WHITE),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 20),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
        ("ROUNDEDCORNERS", [6, 6, 6, 6]),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 0.4 * cm))

    # Scan meta
    meta_style = ParagraphStyle("Meta", parent=styles["Normal"], fontSize=8, textColor=DARK_GRAY)
    story.append(Paragraph(f"<b>Scan ID:</b> {scan_id}", meta_style))
    story.append(Paragraph(f"<b>Scanned At:</b> {scanned_at}", meta_style))
    story.append(Spacer(1, 0.3 * cm))

    story.append(HRFlowable(width="100%", thickness=1, color=LIGHT_GRAY))
    story.append(Spacer(1, 0.3 * cm))

    # ── URL ────────────────────────────────────────────────────────────────
    url_style = ParagraphStyle("URL", parent=styles["Normal"], fontSize=9,
                               textColor=BRAND_COLOR, wordWrap="CJK")
    story.append(Paragraph("<b>Analyzed URL</b>", styles["Heading3"]))
    story.append(Paragraph(url, url_style))
    story.append(Spacer(1, 0.4 * cm))

    # ── Risk Score Block ───────────────────────────────────────────────────
    score_data = [[
        Paragraph(f"<font size='36' color='#{risk_color.hexval()[2:]}'><b>{risk_score}%</b></font>",
                  ParagraphStyle("Score", alignment=TA_CENTER)),
        Paragraph(f"<font size='18'><b>{risk_level} Risk</b></font>",
                  ParagraphStyle("Level", alignment=TA_CENTER,
                                 textColor=risk_color)),
    ]]
    score_table = Table(score_data, colWidths=[8.5 * cm, 8.5 * cm])
    score_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_GRAY),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 16),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 16),
        ("ROUNDEDCORNERS", [6, 6, 6, 6]),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 0.4 * cm))

    # ── Recommendation ─────────────────────────────────────────────────────
    rec_style = ParagraphStyle("Rec", parent=styles["Normal"], fontSize=10,
                               textColor=DARK_GRAY, leading=14)
    story.append(Paragraph("<b>Recommendation</b>", styles["Heading3"]))
    story.append(Paragraph(scan_result.get("recommendation", ""), rec_style))
    story.append(Spacer(1, 0.4 * cm))
    story.append(HRFlowable(width="100%", thickness=1, color=LIGHT_GRAY))
    story.append(Spacer(1, 0.3 * cm))

    # ── Domain Info ────────────────────────────────────────────────────────
    domain_info = scan_result.get("domain_info", {})
    if domain_info:
        story.append(Paragraph("<b>Domain Information</b>", styles["Heading3"]))
        di_data = [
            ["Domain Age", f"{domain_info.get('domain_age_days', 'N/A')} days"],
            ["Registrar", str(domain_info.get("registrar", "N/A"))[:60]],
            ["SSL Days Remaining", str(domain_info.get("ssl_days_remaining", "N/A"))],
            ["SSL Self-Signed", "Yes" if domain_info.get("ssl_self_signed") else "No"],
            ["Redirect Count", str(domain_info.get("redirect_count", 0))],
            ["Closest Brand", domain_info.get("closest_brand", "N/A")],
            ["Typosquat Score", str(domain_info.get("typosquat_score", 0))],
        ]
        di_table = Table(di_data, colWidths=[5 * cm, 12 * cm])
        di_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), LIGHT_GRAY),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [WHITE, LIGHT_GRAY]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(di_table)
        story.append(Spacer(1, 0.4 * cm))

    # ── Threat Intel ───────────────────────────────────────────────────────
    threat_intel = scan_result.get("threat_intel", {})
    if threat_intel:
        story.append(Paragraph("<b>Threat Intelligence</b>", styles["Heading3"]))
        def intel_status(flagged, label):
            color = "#dc2626" if flagged else "#16a34a"
            icon = "🚨 FLAGGED" if flagged else "✅ Clean"
            return Paragraph(f"<font color='{color}'>{icon}</font>", rec_style), label

        urlhaus = threat_intel.get("urlhaus", {})
        google = threat_intel.get("google_sb", {})
        intel_rows = [
            ["", "Status"],
            ["URLhaus", "🚨 LISTED — " + str(urlhaus.get("threat", "")) if urlhaus.get("listed") else "✅ Clean"],
            ["Google Safe Browsing", "🚨 " + str(google.get("threat_type", "")) if google.get("flagged") else "✅ Clean"],
            ["PhishTank", "🚨 CONFIRMED PHISH" if threat_intel.get("phishtank") else "✅ Clean"],
            ["OpenPhish", "🚨 IN FEED" if threat_intel.get("openphish") else "✅ Clean"],
        ]
        intel_table = Table(intel_rows, colWidths=[5 * cm, 12 * cm])
        intel_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), BRAND_COLOR),
            ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_GRAY]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(intel_table)
        story.append(Spacer(1, 0.4 * cm))

    # ── Issues (top 5) ─────────────────────────────────────────────────────
    issues = scan_result.get("issues", [])[:5]
    if issues:
        story.append(Paragraph("<b>Security Issues Found</b>", styles["Heading3"]))
        for issue in issues:
            sev = issue.get("severity", "low")
            sev_color = HIGH_COLOR if sev == "high" else MEDIUM_COLOR if sev == "medium" else LOW_COLOR
            story.append(Paragraph(
                f"<font color='#{sev_color.hexval()[2:]}'>[{sev.upper()}]</font> "
                f"<b>{issue.get('type', '')}</b>: {issue.get('description', '')}",
                ParagraphStyle("Issue", parent=styles["Normal"], fontSize=9, leading=13, spaceAfter=4)
            ))
        story.append(Spacer(1, 0.3 * cm))

    # ── Feature Importances ────────────────────────────────────────────────
    importances = scan_result.get("feature_importances", [])
    if importances:
        story.append(Paragraph("<b>Top ML Feature Importances</b>", styles["Heading3"]))
        imp_data = [["Feature", "Importance", "Value"]]
        for fi in importances:
            imp_data.append([
                fi.get("feature", "").replace("_", " ").title(),
                f"{fi.get('importance', 0):.4f}",
                str(fi.get("value", "")),
            ])
        imp_table = Table(imp_data, colWidths=[7 * cm, 5 * cm, 5 * cm])
        imp_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), BRAND_COLOR),
            ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_GRAY]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(imp_table)

    story.append(Spacer(1, 0.5 * cm))

    # ── Footer ─────────────────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=1, color=LIGHT_GRAY))
    story.append(Spacer(1, 0.2 * cm))
    footer_style = ParagraphStyle("Footer", parent=styles["Normal"],
                                  fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
    story.append(Paragraph(
        "Generated by Security Scanner Portal | For informational purposes only",
        footer_style
    ))

    # Build PDF
    try:
        doc.build(story)
    except Exception as e:
        logger.error(f"PDF generation error: {e}")
        raise

    buffer.seek(0)
    return buffer.read()
