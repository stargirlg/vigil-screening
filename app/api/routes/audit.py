from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
from app.db.database import get_db
from app.models.audit_log import AuditLog
from app.schemas.audit import AuditLogOut
from app.auth.rbac import require_analyst
from app.models.user import User

router = APIRouter(prefix="/audit", tags=["Audit"])


@router.get("", response_model=list[AuditLogOut])
def get_audit_logs(
    entity_id: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    user_email: Optional[str] = Query(None),
    from_date: Optional[datetime] = Query(None),
    to_date: Optional[datetime] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst),
):
    query = db.query(AuditLog)

    if entity_id:
        query = query.filter(AuditLog.entity_id == entity_id)
    if action:
        query = query.filter(AuditLog.action == action)
    if user_email:
        query = query.filter(AuditLog.user_email == user_email)
    if from_date:
        query = query.filter(AuditLog.timestamp >= from_date)
    if to_date:
        query = query.filter(AuditLog.timestamp <= to_date)

    logs = query.order_by(
        AuditLog.timestamp.desc()
    ).offset(skip).limit(limit).all()

    return [AuditLogOut.model_validate(l) for l in logs]