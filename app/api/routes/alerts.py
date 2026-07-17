from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.alert import Alert, AlertStatus
from app.models.audit_log import AuditLog
from app.schemas.alert import AlertOut, AlertReviewRequest
from app.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/alerts", tags=["Alerts"])

ACTION_MAP = {
    "CLEAR":     AlertStatus.CLEARED,
    "CONFIRM":   AlertStatus.CONFIRMED_MATCH,
    "ESCALATE":  AlertStatus.ESCALATED,
    "REJECT":    AlertStatus.REJECTED,
}


@router.get("", response_model=list[AlertOut])
def list_alerts(
    status: str = Query(None),
    risk_level: str = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Alert)
    if status:
        query = query.filter(Alert.status == status)
    if risk_level:
        query = query.filter(Alert.risk_level == risk_level)
    query = query.order_by(Alert.match_score.desc())
    alerts = query.offset(skip).limit(limit).all()
    return [AlertOut.model_validate(a) for a in alerts]


@router.get("/{alert_id}", response_model=AlertOut)
def get_alert(
    alert_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return AlertOut.model_validate(alert)


@router.patch("/{alert_id}/review", response_model=AlertOut)
def review_alert(
    alert_id: UUID,
    payload: AlertReviewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    new_status = ACTION_MAP.get(payload.action.upper())
    if not new_status:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid action. Use: {list(ACTION_MAP.keys())}"
        )

    alert.status = new_status
    alert.reviewed_by = current_user.id
    alert.review_notes = payload.notes
    alert.reviewed_at = datetime.utcnow()
    alert.closed_at = datetime.utcnow()

    db.add(AuditLog(
        user_id=current_user.id,
        user_email=current_user.email,
        action=f"ALERT_{payload.action.upper()}",
        entity_type="ALERT",
        entity_id=str(alert_id),
        details={
            "action": payload.action,
            "notes": payload.notes,
            "previous_status": alert.status.value,
        },
    ))
    db.commit()
    db.refresh(alert)
    return AlertOut.model_validate(alert)