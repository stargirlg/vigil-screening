"""
VIGIL — Watchlist Routes
POST /watchlist              → add customer to watchlist
GET  /watchlist/{customer_id} → get watchlist history
"""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.watchlist import WatchlistEntry
from app.models.audit_log import AuditLog
from app.schemas.watchlist import WatchlistCreate, WatchlistOut
from app.dependencies import get_current_user
from app.auth.rbac import require_analyst
from app.models.user import User

router = APIRouter(prefix="/watchlist", tags=["Watchlist"])


@router.post("", response_model=WatchlistOut)
def add_to_watchlist(
    payload: WatchlistCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst),
):
    """Add a customer to the internal watchlist."""
    entry = WatchlistEntry(
        customer_id=payload.customer_id,
        status=payload.status.value,
        reason=payload.reason,
        case_reference=payload.case_reference,
        added_by=current_user.id,
        added_by_email=current_user.email,
        notes=payload.notes,
    )
    db.add(entry)

    db.add(AuditLog(
        user_id=current_user.id,
        user_email=current_user.email,
        action="WATCHLIST_ENTRY_ADDED",
        entity_type="CUSTOMER",
        entity_id=str(payload.customer_id),
        details={
            "status": payload.status.value,
            "reason": payload.reason,
            "case_reference": payload.case_reference,
        },
    ))
    db.commit()
    db.refresh(entry)
    return WatchlistOut.model_validate(entry)


@router.get("/{customer_id}", response_model=list[WatchlistOut])
def get_watchlist(
    customer_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst),
):
    """Get full watchlist history for a customer."""
    entries = db.query(WatchlistEntry).filter(
        WatchlistEntry.customer_id == customer_id
    ).order_by(WatchlistEntry.added_at.desc()).all()

    if not entries:
        raise HTTPException(
            status_code=404,
            detail="No watchlist entries found for this customer"
        )
    return [WatchlistOut.model_validate(e) for e in entries]