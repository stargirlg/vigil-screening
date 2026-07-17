"""
VIGIL — Case Management Routes
POST /cases                          → create case from alert
GET  /cases                          → list all cases
GET  /cases/{id}                     → case detail
POST /cases/{id}/notes               → add note
POST /cases/{id}/recommend           → analyst recommendation
POST /cases/{id}/decide              → CO final decision
GET  /cases/{id}/notes               → get all notes
"""
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.case import Case, CaseNote, CaseEvidence, CaseStatus
from app.models.user import UserRole
from app.schemas.case import (
    CaseCreate, CaseOut, CaseNoteCreate, CaseNoteOut,
    AnalystRecommendation, CODecision, CaseEvidenceOut
)
from app.core.case_manager import (
    create_case, add_note,
    submit_analyst_recommendation, submit_co_decision
)
from app.dependencies import get_current_user
from app.models.user import User
from app.auth.rbac import require_analyst, require_co

router = APIRouter(prefix="/cases", tags=["Cases"])


@router.post("", response_model=CaseOut)
def create_new_case(
    payload: CaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst),
):
    """Create a case from an alert. Analyst or Admin only."""
    case = create_case(
        db=db,
        alert_id=str(payload.alert_id),
        customer_id=str(payload.customer_id),
        risk_level="HIGH",
        assigned_to=current_user.id,
        assigned_email=current_user.email,
    )
    return CaseOut.model_validate(case)


@router.get("", response_model=list[CaseOut])
def list_cases(
    status: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst),
):
    """List all cases. Filter by status."""
    query = db.query(Case)
    if status:
        query = query.filter(Case.status == status)
    query = query.order_by(Case.created_at.desc())
    cases = query.all()
    return [CaseOut.model_validate(c) for c in cases]


@router.get("/{case_id}", response_model=CaseOut)
def get_case(
    case_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst),
):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return CaseOut.model_validate(case)


@router.post("/{case_id}/notes", response_model=CaseNoteOut)
def add_case_note(
    case_id: UUID,
    payload: CaseNoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst),
):
    """Add a note to a case. Analysts and CO can add notes."""
    try:
        note = add_note(
            db=db,
            case_id=str(case_id),
            author_id=str(current_user.id),
            author_email=current_user.email,
            note=payload.note,
            note_type=payload.note_type,
        )
        return CaseNoteOut.model_validate(note)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{case_id}/notes", response_model=list[CaseNoteOut])
def get_case_notes(
    case_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst),
):
    notes = db.query(CaseNote).filter(
        CaseNote.case_id == case_id
    ).order_by(CaseNote.created_at.asc()).all()
    return [CaseNoteOut.model_validate(n) for n in notes]


@router.post("/{case_id}/recommend", response_model=CaseOut)
def analyst_recommend(
    case_id: UUID,
    payload: AnalystRecommendation,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst),
):
    """
    Analyst submits recommendation.
    Moves case to PENDING_CO for CO review.
    """
    try:
        case = submit_analyst_recommendation(
            db=db,
            case_id=str(case_id),
            analyst_id=str(current_user.id),
            analyst_email=current_user.email,
            recommendation=payload.recommendation,
            notes=payload.notes,
        )
        return CaseOut.model_validate(case)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{case_id}/decide", response_model=CaseOut)
def co_decide(
    case_id: UUID,
    payload: CODecision,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_co),
):
    """
    CO makes final decision. Case is locked after this.
    Four-eyes: CO cannot approve their own recommendation.
    """
    try:
        case = submit_co_decision(
            db=db,
            case_id=str(case_id),
            co_id=str(current_user.id),
            co_email=current_user.email,
            decision=payload.decision,
            notes=payload.notes,
            sar_required=payload.sar_required,
        )
        return CaseOut.model_validate(case)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))