from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from datetime import datetime

from app.db.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.utils.pdf_generator import (
    generate_case_report,
    generate_sar_draft,
    generate_audit_export,
)

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/case/{case_id}")
def download_case_report(
    case_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.models.case import Case, CaseNote
    from app.models.customer import Customer

    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    customer = db.query(Customer).filter(Customer.id == case.customer_id).first()
    notes = db.query(CaseNote).filter(
        CaseNote.case_id == case_id
    ).order_by(CaseNote.created_at.asc()).all()

    case_dict = {
        "case_number":            case.case_number,
        "status":                 case.status,
        "created_at":             case.created_at,
        "closed_at":              case.closed_at,
        "sla_deadline":           case.sla_deadline,
        "sla_breached":           case.sla_breached,
        "rule_version":           case.rule_version,
        "sar_required":           case.sar_required,
        "decision_locked":        case.decision_locked,
        "analyst_recommendation": case.analyst_recommendation,
        "analyst_notes":          case.analyst_notes,
        "co_decision":            case.co_decision,
        "co_notes":               case.co_notes,
    }

    customer_dict = {
        "full_name":   customer.full_name if customer else "—",
        "dob":         str(customer.dob) if customer and customer.dob else "—",
        "pan":         customer.pan if customer else "—",
        "aadhaar":     customer.aadhaar if customer else "—",
        "nationality": customer.nationality if customer else "—",
        "occupation":  customer.occupation if customer else "—",
        "source":      customer.source if customer else "—",
    }

    notes_list = [
        {
            "author_email": n.author_email,
            "note_type":    n.note_type,
            "note":         n.note,
            "created_at":   n.created_at,
        }
        for n in notes
    ]

    pdf_bytes = generate_case_report(
        case=case_dict,
        customer=customer_dict,
        notes=notes_list,
    )

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=VIGIL-Case-{case.case_number}.pdf"
        }
    )


@router.get("/sar/{case_id}")
def download_sar_draft(
    case_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.models.case import Case
    from app.models.customer import Customer
    from app.models.alert import Alert

    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    customer = db.query(Customer).filter(Customer.id == case.customer_id).first()
    alert = db.query(Alert).filter(Alert.id == case.alert_id).first()

    case_dict = {
        "case_number":            case.case_number,
        "status":                 case.status,
        "analyst_recommendation": case.analyst_recommendation,
        "analyst_notes":          case.analyst_notes,
        "co_decision":            case.co_decision,
        "co_notes":               case.co_notes,
    }

    customer_dict = {
        "full_name":   customer.full_name if customer else "—",
        "dob":         str(customer.dob) if customer and customer.dob else "—",
        "pan":         customer.pan if customer else "—",
        "aadhaar":     customer.aadhaar if customer else "—",
        "nationality": customer.nationality if customer else "—",
        "occupation":  customer.occupation if customer else "—",
    }

    alert_dict = {}
    if alert:
        alert_dict = {
            "alert_type":     alert.alert_type,
            "match_score":    alert.match_score,
            "risk_level":     alert.risk_level.value if alert.risk_level else "—",
            "params_matched": alert.params_matched,
            "matched_params": alert.matched_params or [],
        }

    pdf_bytes = generate_sar_draft(
        case=case_dict,
        customer=customer_dict,
        alert=alert_dict,
    )

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=VIGIL-SAR-{case.case_number}.pdf"
        }
    )


@router.get("/audit")
def download_audit_export(
    limit: int = 500,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.models.audit_log import AuditLog

    logs = db.query(AuditLog).order_by(
        AuditLog.timestamp.desc()
    ).limit(limit).all()

    logs_list = [
        {
            "timestamp":   l.timestamp,
            "user_email":  l.user_email,
            "action":      l.action,
            "entity_type": l.entity_type,
            "entity_id":   str(l.entity_id) if l.entity_id else None,
        }
        for l in logs
    ]

    pdf_bytes = generate_audit_export(logs=logs_list)

    filename = f"VIGIL-Audit-{datetime.utcnow().strftime('%Y%m%d')}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )