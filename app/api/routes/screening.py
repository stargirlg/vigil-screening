from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from celery.result import AsyncResult
from app.db.database import get_db
from app.models.customer import Customer
from app.models.audit_log import AuditLog
from app.core.screening_engine import screen_customer
from app.core.alert_router import route_alert
from app.schemas.screening import ScreeningResult, BatchScreenRequest, ScreeningStatus
from app.tasks.batch_screening import screen_batch
from app.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/screen", tags=["Screening"])


@router.post("", response_model=ScreeningResult)
def screen_single(
    customer_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    customer = db.query(Customer).filter(
        Customer.id == customer_id
    ).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    result = screen_customer(customer, db)
    alert = route_alert(result, db)

    db.add(AuditLog(
        user_id=current_user.id,
        user_email=current_user.email,
        action="CUSTOMER_SCREENED",
        entity_type="CUSTOMER",
        entity_id=str(customer_id),
        details={
            "risk_level": result.risk_level.value,
            "score": result.weighted_score,
            "alert_id": str(alert.id),
        },
    ))
    db.commit()
    return result


@router.post("/batch")
def screen_batch_endpoint(
    payload: BatchScreenRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    customer_id_strs = [str(cid) for cid in payload.customer_ids]

    found = db.query(Customer.id).filter(
        Customer.id.in_(customer_id_strs)
    ).count()
    if found != len(customer_id_strs):
        raise HTTPException(
            status_code=400,
            detail="Some customer IDs not found"
        )

    task = screen_batch.delay(
        customer_id_strs,
        triggered_by=current_user.email
    )

    db.add(AuditLog(
        user_id=current_user.id,
        user_email=current_user.email,
        action="BATCH_SCREENING_STARTED",
        entity_type="BATCH",
        entity_id=task.id,
        details={"total_customers": len(customer_id_strs)},
    ))
    db.commit()

    return {
        "task_id": task.id,
        "status": "STARTED",
        "total_customers": len(customer_id_strs),
        "message": "Poll /screen/status/{task_id} for progress",
    }


@router.get("/status/{task_id}", response_model=ScreeningStatus)
def get_batch_status(
    task_id: str,
    current_user: User = Depends(get_current_user)
):
    result = AsyncResult(task_id)

    if result.state == "PENDING":
        return ScreeningStatus(task_id=task_id, status="PENDING")

    if result.state == "PROGRESS":
        meta = result.info or {}
        return ScreeningStatus(
            task_id=task_id,
            status="IN_PROGRESS",
            total=meta.get("total"),
            processed=meta.get("processed"),
            high_alerts=meta.get("high_alerts"),
            auto_closed=meta.get("auto_closed"),
        )

    if result.state == "SUCCESS":
        info = result.result or {}
        return ScreeningStatus(
            task_id=task_id,
            status="SUCCESS",
            total=info.get("total"),
            processed=info.get("processed"),
            high_alerts=info.get("high_alerts"),
            auto_closed=info.get("auto_closed"),
        )

    return ScreeningStatus(task_id=task_id, status=result.state)