"""
VIGIL — Case Manager
Handles case lifecycle:
  OPEN → INVESTIGATING → PENDING_CO → CLOSED

Four-eyes enforcement:
  Analyst adds notes and recommends
  CO makes final decision
  No self-approval allowed

Decision locking:
  After CO decision → case frozen
  Nothing can be changed
"""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.case import Case, CaseStatus, CaseNote, CaseDecisionLog
from app.models.audit_log import AuditLog
from app.utils.logger import get_logger

log = get_logger(__name__)

# SLA rules per risk level
SLA_HOURS = {
    "LOW":      None,   # auto-closed, no SLA
    "MEDIUM":   48,
    "HIGH":     24,
    "CRITICAL": 4,
}

CASE_COUNTER_PREFIX = "VIGIL"


def generate_case_number(db: Session) -> str:
    """Generate sequential case number like VIGIL-2026-0001."""
    count = db.query(Case).count() + 1
    year = datetime.utcnow().year
    return f"{CASE_COUNTER_PREFIX}-{year}-{count:04d}"


def create_case(
    db: Session,
    alert_id: str,
    customer_id: str,
    risk_level: str,
    rule_version: str = "1.0",
    assigned_to=None,
    assigned_email=None,
) -> Case:
    """Create a new case from an alert."""
    sla_hours = SLA_HOURS.get(risk_level)
    sla_deadline = None
    if sla_hours:
        sla_deadline = datetime.utcnow() + timedelta(hours=sla_hours)

    case = Case(
        case_number=generate_case_number(db),
        alert_id=alert_id,
        customer_id=customer_id,
        status=CaseStatus.OPEN,
        assigned_to=assigned_to,
        assigned_email=assigned_email,
        rule_version=rule_version,
        sla_deadline=sla_deadline,
    )
    db.add(case)
    db.commit()
    db.refresh(case)

    log.info(f"Case created: {case.case_number} | alert={alert_id} | SLA={sla_deadline}")
    return case


def add_note(
    db: Session,
    case_id: str,
    author_id: str,
    author_email: str,
    note: str,
    note_type: str = "GENERAL",
) -> CaseNote:
    """Add a note to a case. Anyone assigned can add notes."""
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise ValueError(f"Case {case_id} not found")
    if case.decision_locked:
        raise ValueError("Case is locked — no changes allowed after CO decision")

    case_note = CaseNote(
        case_id=case_id,
        author_id=author_id,
        author_email=author_email,
        note=note,
        note_type=note_type,
    )
    db.add(case_note)

    # Move to INVESTIGATING if still OPEN
    if case.status == CaseStatus.OPEN:
        case.status = CaseStatus.INVESTIGATING
        case.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(case_note)
    return case_note


def submit_analyst_recommendation(
    db: Session,
    case_id: str,
    analyst_id: str,
    analyst_email: str,
    recommendation: str,
    notes: str,
) -> Case:
    """Analyst submits recommendation — moves case to PENDING_CO."""
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise ValueError(f"Case {case_id} not found")
    if case.decision_locked:
        raise ValueError("Case is locked")

    case.analyst_recommendation = recommendation
    case.analyst_notes = notes
    case.analyst_id = analyst_id
    case.analyst_submitted_at = datetime.utcnow()
    case.status = CaseStatus.PENDING_CO
    case.updated_at = datetime.utcnow()

    db.add(AuditLog(
        user_id=analyst_id,
        user_email=analyst_email,
        action="ANALYST_RECOMMENDATION_SUBMITTED",
        entity_type="CASE",
        entity_id=str(case_id),
        details={"recommendation": recommendation, "notes": notes},
    ))
    db.commit()
    db.refresh(case)
    log.info(f"Analyst recommendation: {case.case_number} → {recommendation}")
    return case


def submit_co_decision(
    db: Session,
    case_id: str,
    co_id: str,
    co_email: str,
    decision: str,
    notes: str,
    sar_required: bool = False,
) -> Case:
    """
    CO makes final decision. Case is locked after this.
    Four-eyes: CO cannot decide on their own cases.
    """
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise ValueError(f"Case {case_id} not found")
    if case.decision_locked:
        raise ValueError("Case already locked")

    # Four-eyes check — CO cannot be same as analyst
    if str(case.analyst_id) == str(co_id):
        raise ValueError(
            "Four-eyes violation: CO cannot approve their own recommendation"
        )

    case.co_decision = decision
    case.co_notes = notes
    case.co_id = co_id
    case.co_decided_at = datetime.utcnow()
    case.sar_required = sar_required
    case.status = CaseStatus.CLOSED
    case.closed_at = datetime.utcnow()
    case.decision_locked = True  # LOCK THE CASE
    case.updated_at = datetime.utcnow()

    if sar_required:
        case.sar_filed_at = datetime.utcnow()

    # Log the decision
    decision_log = CaseDecisionLog(
        case_id=case_id,
        decided_by=co_id,
        decider_email=co_email,
        decision=decision,
        notes=notes,
        rule_version=case.rule_version,
    )
    db.add(decision_log)

    db.add(AuditLog(
        user_id=co_id,
        user_email=co_email,
        action="CO_DECISION_MADE",
        entity_type="CASE",
        entity_id=str(case_id),
        details={
            "decision": decision,
            "notes": notes,
            "sar_required": sar_required,
            "decision_locked": True,
        },
    ))
    db.commit()
    db.refresh(case)
    log.info(f"CO decision: {case.case_number} → {decision} | locked=True")
    return case