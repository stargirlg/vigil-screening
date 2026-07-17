from datetime import datetime
from sqlalchemy.orm import Session
from app.models.alert import Alert, AlertStatus, RiskLevel
from app.schemas.screening import ScreeningResult
from app.utils.logger import get_logger

log = get_logger(__name__)


def route_alert(result: ScreeningResult, db: Session) -> Alert:
    if result.risk_level == RiskLevel.LOW:
        status = AlertStatus.AUTO_CLOSED
        closed_at = datetime.utcnow()
    else:
        status = AlertStatus.PENDING_REVIEW
        closed_at = None

    alert = Alert(
        customer_id=result.customer_id,
        match_score=result.weighted_score,
        params_matched=result.params_matched_count,
        matched_params=result.matched_params,
        match_details={
            "name":          result.name.model_dump(),
            "dob":           result.dob.model_dump(),
            "id_check":      result.id_check.model_dump(),
            "nationality":   result.nationality.model_dump(),
            "occupation":    result.occupation.model_dump(),
            "adverse_media": result.adverse_media.model_dump(),
            "pep":           result.pep.model_dump(),
        },
        risk_level=result.risk_level,
        status=status,
        alert_type=result.alert_type,
        closed_at=closed_at,
    )

    db.add(alert)
    db.commit()
    db.refresh(alert)

    log.info(
        f"Alert routed: {alert.id} | "
        f"risk={result.risk_level} | status={status}"
    )
    return alert


def get_queue_stats(db: Session) -> dict:
    total = db.query(Alert).count()
    pending = db.query(Alert).filter(
        Alert.status == AlertStatus.PENDING_REVIEW
    ).count()
    auto_closed = db.query(Alert).filter(
        Alert.status == AlertStatus.AUTO_CLOSED
    ).count()
    confirmed = db.query(Alert).filter(
        Alert.status == AlertStatus.CONFIRMED_MATCH
    ).count()
    cleared = db.query(Alert).filter(
        Alert.status == AlertStatus.CLEARED
    ).count()

    reduction_pct = round(
        (auto_closed / total * 100), 1
    ) if total > 0 else 0.0

    return {
        "total_alerts": total,
        "pending_review": pending,
        "auto_closed": auto_closed,
        "confirmed_matches": confirmed,
        "cleared": cleared,
        "analyst_load_reduction_pct": reduction_pct,
    }