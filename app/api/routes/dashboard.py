"""
VIGIL — Executive Dashboard
KPIs for management and compliance officers.
Shows the ROI of VIGIL in real numbers.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from app.db.database import get_db
from app.models.alert import Alert, AlertStatus, RiskLevel
from app.models.customer import Customer
from app.models.case import Case, CaseStatus
from app.models.audit_log import AuditLog
from app.core.alert_router import get_queue_stats
from app.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats")
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Main KPI stats for executive dashboard."""

    # ── Alert counts ──────────────────────────────────────────────────
    total_alerts = db.query(Alert).count()
    auto_closed = db.query(Alert).filter(
        Alert.status == AlertStatus.AUTO_CLOSED
    ).count()
    pending = db.query(Alert).filter(
        Alert.status == AlertStatus.PENDING_REVIEW
    ).count()
    confirmed = db.query(Alert).filter(
        Alert.status == AlertStatus.CONFIRMED_MATCH
    ).count()
    cleared = db.query(Alert).filter(
        Alert.status == AlertStatus.CLEARED
    ).count()
    escalated = db.query(Alert).filter(
        Alert.status == AlertStatus.ESCALATED
    ).count()

    # ── Risk distribution ─────────────────────────────────────────────
    critical_count = db.query(Alert).filter(
        Alert.risk_level == RiskLevel.CRITICAL
    ).count()
    high_count = db.query(Alert).filter(
        Alert.risk_level == RiskLevel.HIGH
    ).count()
    medium_count = db.query(Alert).filter(
        Alert.risk_level == RiskLevel.MEDIUM
    ).count()
    low_count = db.query(Alert).filter(
        Alert.risk_level == RiskLevel.LOW
    ).count()

    # ── Case stats ────────────────────────────────────────────────────
    total_cases = db.query(Case).count()
    open_cases = db.query(Case).filter(
        Case.status == CaseStatus.OPEN
    ).count()
    investigating = db.query(Case).filter(
        Case.status == CaseStatus.INVESTIGATING
    ).count()
    pending_co = db.query(Case).filter(
        Case.status == CaseStatus.PENDING_CO
    ).count()
    closed_cases = db.query(Case).filter(
        Case.status == CaseStatus.CLOSED
    ).count()
    sar_filed = db.query(Case).filter(
        Case.sar_required == True
    ).count()

    # ── SLA breaches ──────────────────────────────────────────────────
    sla_breached = db.query(Case).filter(
        Case.sla_deadline < datetime.utcnow(),
        Case.status != CaseStatus.CLOSED,
    ).count()

    # ── TAT (average minutes to close) ───────────────────────────────
    closed_alerts = db.query(Alert).filter(
        Alert.closed_at.isnot(None),
        Alert.created_at.isnot(None),
    ).all()

    avg_tat_minutes = None
    if closed_alerts:
        tats = [
            (a.closed_at - a.created_at).total_seconds() / 60
            for a in closed_alerts
            if a.closed_at and a.created_at
        ]
        avg_tat_minutes = round(sum(tats) / len(tats), 1) if tats else None

    # ── Customer stats ────────────────────────────────────────────────
    total_customers = db.query(Customer).count()

    # ── Workload reduction ────────────────────────────────────────────
    reduction_pct = round(
        (auto_closed / total_alerts * 100), 1
    ) if total_alerts > 0 else 0.0

    # ── False positive rate ───────────────────────────────────────────
    reviewed = confirmed + cleared
    false_positive_rate = round(
        (cleared / reviewed * 100), 1
    ) if reviewed > 0 else 0.0

    # ── Today's activity ──────────────────────────────────────────────
    today_start = datetime.utcnow().replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    alerts_today = db.query(Alert).filter(
        Alert.created_at >= today_start
    ).count()
    cases_today = db.query(Case).filter(
        Case.created_at >= today_start
    ).count()

    return {
        # Core KPIs
        "total_customers":          total_customers,
        "total_alerts":             total_alerts,
        "alerts_today":             alerts_today,
        "cases_today":              cases_today,

        # Alert breakdown
        "alert_breakdown": {
            "auto_closed":          auto_closed,
            "pending_review":       pending,
            "confirmed_matches":    confirmed,
            "cleared":              cleared,
            "escalated":            escalated,
        },

        # Risk distribution
        "risk_distribution": {
            "critical":             critical_count,
            "high":                 high_count,
            "medium":               medium_count,
            "low":                  low_count,
        },

        # Case management
        "case_stats": {
            "total":                total_cases,
            "open":                 open_cases,
            "investigating":        investigating,
            "pending_co":           pending_co,
            "closed":               closed_cases,
            "sar_filed":            sar_filed,
            "sla_breached":         sla_breached,
        },

        # Performance metrics
        "performance": {
            "analyst_load_reduction_pct":   reduction_pct,
            "false_positive_rate_pct":      false_positive_rate,
            "avg_tat_minutes":              avg_tat_minutes,
            "confirmed_match_rate_pct": round(
                (confirmed / reviewed * 100), 1
            ) if reviewed > 0 else 0.0,
        },

        "generated_at": datetime.utcnow().isoformat(),
    }


@router.get("/alerts/trend")
def get_alert_trend(
    days: int = 7,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Alert trend for last N days — for charts."""
    trend = []
    for i in range(days - 1, -1, -1):
        day_start = datetime.utcnow().replace(
            hour=0, minute=0, second=0, microsecond=0
        ) - timedelta(days=i)
        day_end = day_start + timedelta(days=1)

        day_total = db.query(Alert).filter(
            Alert.created_at >= day_start,
            Alert.created_at < day_end,
        ).count()

        day_high = db.query(Alert).filter(
            Alert.created_at >= day_start,
            Alert.created_at < day_end,
            Alert.risk_level.in_([RiskLevel.HIGH, RiskLevel.CRITICAL]),
        ).count()

        day_auto = db.query(Alert).filter(
            Alert.created_at >= day_start,
            Alert.created_at < day_end,
            Alert.status == AlertStatus.AUTO_CLOSED,
        ).count()

        trend.append({
            "date":        day_start.strftime("%Y-%m-%d"),
            "total":       day_total,
            "high":        day_high,
            "auto_closed": day_auto,
        })

    return {"days": days, "trend": trend}


@router.get("/analyst/productivity")
def get_analyst_productivity(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Analyst productivity metrics."""
    analysts = db.query(AuditLog).filter(
        AuditLog.action == "ALERT_REVIEWED"
    ).all()

    productivity = {}
    for log in analysts:
        email = log.user_email or "system"
        if email not in productivity:
            productivity[email] = 0
        productivity[email] += 1

        

    return {
        "analyst_reviews": [
            {"analyst": k, "reviews": v}
            for k, v in sorted(
                productivity.items(),
                key=lambda x: x[1],
                reverse=True
            )
        ]
    }


@router.get("/sla/breaches")
def get_sla_breaches(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all cases that have breached SLA."""
    from app.models.case import Case
    breached = db.query(Case).filter(
        Case.sla_breached == True
    ).order_by(Case.sla_deadline.asc()).all()

    return {
        "total_breaches": len(breached),
        "cases": [
            {
                "case_number": c.case_number,
                "case_id": str(c.id),
                "status": c.status,
                "sla_deadline": c.sla_deadline.isoformat() if c.sla_deadline else None,
                "created_at": c.created_at.isoformat(),
            }
            for c in breached
        ]
    }