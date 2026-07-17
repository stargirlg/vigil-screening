from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table,
    TableStyle, HRFlowable,
)
from reportlab.lib.enums import TA_CENTER

OLIVE       = colors.HexColor("#495844")
LIGHT_OLIVE = colors.HexColor("#73856E")
BEIGE       = colors.HexColor("#F4F1EA")
BORDER      = colors.HexColor("#DDD6C9")
RED         = colors.HexColor("#8B4040")
GRAY        = colors.HexColor("#8B9388")
BLACK       = colors.HexColor("#2D2D2D")


def _header_style():
    return ParagraphStyle("VIGILHeader", fontName="Helvetica-Bold", fontSize=18, textColor=OLIVE, spaceAfter=4)

def _subheader_style():
    return ParagraphStyle("VIGILSub", fontName="Helvetica", fontSize=10, textColor=GRAY, spaceAfter=12)

def _section_style():
    return ParagraphStyle("VIGILSection", fontName="Helvetica-Bold", fontSize=10, textColor=OLIVE, spaceBefore=14, spaceAfter=6)

def _body_style():
    return ParagraphStyle("VIGILBody", fontName="Helvetica", fontSize=9, textColor=BLACK, spaceAfter=4, leading=14)

def _table_style():
    return TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0),  OLIVE),
        ("TEXTCOLOR",     (0, 0), (-1, 0),  colors.white),
        ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, 0),  8),
        ("FONTNAME",      (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",      (0, 1), (-1, -1), 8),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.white, BEIGE]),
        ("GRID",          (0, 0), (-1, -1), 0.3, BORDER),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ])


def _vigil_header(elements, title: str, subtitle: str = ""):
    elements.append(Paragraph("VIGIL", _header_style()))
    elements.append(Paragraph("Compliance Screening Platform · Confidential", _subheader_style()))
    elements.append(HRFlowable(width="100%", thickness=1, color=OLIVE, spaceAfter=10))
    elements.append(Paragraph(title, ParagraphStyle("Title", fontName="Helvetica-Bold", fontSize=14, textColor=BLACK, spaceAfter=4)))
    if subtitle:
        elements.append(Paragraph(subtitle, _subheader_style()))
    elements.append(Paragraph(
        f"Generated: {datetime.utcnow().strftime('%d %B %Y, %H:%M UTC')}",
        ParagraphStyle("Gen", fontName="Helvetica", fontSize=8, textColor=GRAY, spaceAfter=14)
    ))


def generate_case_report(case: dict, customer: dict, notes: list) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    elements = []

    _vigil_header(elements, title=f"Case Report — {case.get('case_number', 'N/A')}", subtitle=f"Status: {case.get('status', 'N/A')} · Customer: {customer.get('full_name', 'Unknown')}")

    elements.append(Paragraph("Case Summary", _section_style()))
    summary_data = [
        ["Field", "Value"],
        ["Case Number",    case.get("case_number", "—")],
        ["Status",         case.get("status", "—")],
        ["Created At",     str(case.get("created_at", "—"))[:19]],
        ["Closed At",      str(case.get("closed_at", "—"))[:19] if case.get("closed_at") else "Open"],
        ["SLA Breached",   "YES" if case.get("sla_breached") else "NO"],
        ["Rule Version",   case.get("rule_version", "1.0")],
        ["SAR Required",   "YES" if case.get("sar_required") else "NO"],
        ["Decision Locked","YES" if case.get("decision_locked") else "NO"],
    ]
    t = Table(summary_data, colWidths=[5*cm, 11*cm])
    t.setStyle(_table_style())
    elements.append(t)

    elements.append(Paragraph("Customer Details", _section_style()))
    cust_data = [
        ["Field", "Value"],
        ["Full Name",   customer.get("full_name", "—")],
        ["DOB",         str(customer.get("dob", "—"))],
        ["PAN",         customer.get("pan", "—")],
        ["Nationality", customer.get("nationality", "—")],
        ["Occupation",  customer.get("occupation", "—")],
        ["Source",      customer.get("source", "—")],
    ]
    t2 = Table(cust_data, colWidths=[5*cm, 11*cm])
    t2.setStyle(_table_style())
    elements.append(t2)

    if case.get("analyst_recommendation"):
        elements.append(Paragraph("Four-Eyes Review", _section_style()))
        review_data = [
            ["Role", "Decision", "Notes"],
            ["Analyst", case.get("analyst_recommendation", "—"), (case.get("analyst_notes", "—") or "—")[:80]],
            ["Compliance Officer", case.get("co_decision", "Pending"), (case.get("co_notes", "—") or "—")[:80]],
        ]
        t3 = Table(review_data, colWidths=[3.5*cm, 4*cm, 8.5*cm])
        t3.setStyle(_table_style())
        elements.append(t3)

    if notes:
        elements.append(Paragraph("Investigation Notes", _section_style()))
        notes_data = [["Author", "Type", "Date", "Note"]]
        for n in notes[:20]:
            notes_data.append([
                str(n.get("author_email", "—"))[:20],
                n.get("note_type", "—"),
                str(n.get("created_at", "—"))[:10],
                str(n.get("note", "—"))[:60],
            ])
        t4 = Table(notes_data, colWidths=[4*cm, 2.5*cm, 2.5*cm, 7*cm])
        t4.setStyle(_table_style())
        elements.append(t4)

    elements.append(Spacer(1, 20))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=BORDER))
    elements.append(Paragraph("VIGIL Compliance Platform · Confidential · Authorized personnel only",
        ParagraphStyle("Footer", fontName="Helvetica", fontSize=7, textColor=GRAY, alignment=TA_CENTER)))

    doc.build(elements)
    return buffer.getvalue()


def generate_sar_draft(case: dict, customer: dict, alert: dict) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    elements = []

    _vigil_header(elements, title="Suspicious Activity Report (SAR) — DRAFT", subtitle=f"FIU-IND Filing Draft · Case: {case.get('case_number', 'N/A')}")

    elements.append(Paragraph("⚠ DRAFT — For CO review before FIU-IND submission",
        ParagraphStyle("Warning", fontName="Helvetica-Bold", fontSize=9, textColor=RED, spaceAfter=12)))

    elements.append(Paragraph("1. Subject Details", _section_style()))
    subject_data = [
        ["Field", "Value"],
        ["Full Name",    customer.get("full_name", "—")],
        ["Date of Birth", str(customer.get("dob", "—"))],
        ["PAN Number",   customer.get("pan", "—")],
        ["Aadhaar",      customer.get("aadhaar", "—")],
        ["Nationality",  customer.get("nationality", "—")],
        ["Occupation",   customer.get("occupation", "—")],
    ]
    t = Table(subject_data, colWidths=[5*cm, 11*cm])
    t.setStyle(_table_style())
    elements.append(t)

    elements.append(Paragraph("2. Nature of Suspicious Activity", _section_style()))
    elements.append(Paragraph(f"Alert Type: {alert.get('alert_type', 'Unknown')}", _body_style()))
    elements.append(Paragraph(f"Risk Score: {alert.get('match_score', 0)}/100 — Risk Level: {alert.get('risk_level', 'Unknown')}", _body_style()))
    elements.append(Paragraph(f"Parameters Matched: {alert.get('params_matched', 0)} of 7", _body_style()))

    elements.append(Paragraph("3. Grounds for Suspicion", _section_style()))
    grounds = []
    if "SANCTION" in str(alert.get("alert_type", "")):
        grounds.append("• Customer name matched against OFAC/UN sanctions list")
    if "PEP" in str(alert.get("alert_type", "")):
        grounds.append("• Customer identified as Politically Exposed Person (PEP)")
    if "MEDIA" in str(alert.get("alert_type", "")):
        grounds.append("• Adverse media coverage indicating suspicious activity")
    if not grounds:
        grounds.append("• Customer flagged by automated AML screening engine")
    for g in grounds:
        elements.append(Paragraph(g, _body_style()))

    elements.append(Paragraph("4. Investigation Summary", _section_style()))
    elements.append(Paragraph(f"Case: {case.get('case_number', '—')} · Status: {case.get('status', '—')}", _body_style()))
    if case.get("analyst_recommendation"):
        elements.append(Paragraph(f"Analyst Recommendation: {case.get('analyst_recommendation', '—')}", _body_style()))
    if case.get("co_decision"):
        elements.append(Paragraph(f"CO Decision: {case.get('co_decision', '—')}", _body_style()))

    elements.append(Paragraph("5. Declaration", _section_style()))
    elements.append(Paragraph(
        "This SAR has been prepared based on automated AML screening by VIGIL Compliance Platform "
        "and subsequent investigation by our compliance team.", _body_style()))
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("Compliance Officer Signature: _______________________", _body_style()))
    elements.append(Paragraph("Date: _______________________", _body_style()))
    elements.append(Paragraph("Designation: _______________________", _body_style()))

    elements.append(Spacer(1, 20))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=BORDER))
    elements.append(Paragraph("VIGIL · SAR Draft · Confidential · For FIU-IND submission after CO approval",
        ParagraphStyle("Footer", fontName="Helvetica", fontSize=7, textColor=GRAY, alignment=TA_CENTER)))

    doc.build(elements)
    return buffer.getvalue()


def generate_audit_export(logs: list) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    elements = []

    _vigil_header(elements, title="Audit Trail Export", subtitle=f"Compliance audit log · {len(logs)} entries")

    if not logs:
        elements.append(Paragraph("No audit logs found.", _body_style()))
    else:
        audit_data = [["Timestamp", "User", "Action", "Entity"]]
        for log in logs[:100]:
            audit_data.append([
                str(log.get("timestamp", "—"))[:16],
                str(log.get("user_email", "—"))[:20],
                str(log.get("action", "—"))[:25],
                f"{log.get('entity_type', '—')} {str(log.get('entity_id', '—'))[:8]}",
            ])
        t = Table(audit_data, colWidths=[3.5*cm, 4.5*cm, 5*cm, 3*cm])
        t.setStyle(_table_style())
        elements.append(t)

    elements.append(Spacer(1, 20))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=BORDER))
    elements.append(Paragraph("VIGIL · Audit Export · Confidential · Immutable record",
        ParagraphStyle("Footer", fontName="Helvetica", fontSize=7, textColor=GRAY, alignment=TA_CENTER)))

    doc.build(elements)
    return buffer.getvalue()