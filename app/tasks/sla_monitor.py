"""
VIGIL — SLA Monitor
Checks all open cases against their SLA deadlines.
Runs every hour via Celery Beat.

SLA rules:
  MEDIUM   → 48 hours
  HIGH     → 24 hours
  CRITICAL → 4 hours
"""
from datetime import datetime
from app.tasks.celery_app import celery_app
from app.db.database import SessionLocal
from app.models.case import Case, CaseStatus
from app.models.audit_log import AuditLog
from app.utils.logger import get_logger

log = get_logger(__name__)


@celery_app.task(name="app.tasks.sla_monitor.check_sla_breaches")
def check_sla_breaches() -> dict:
    """
    Find all open cases past their SLA deadline.
    Mark them as breached and log for CO notification.
    """
    db = SessionLocal()
    breached = []

    try:
        now = datetime.utcnow()

        # Find open cases with expired SLA
        overdue = db.query(Case).filter(
            Case.sla_deadline < now,
            Case.sla_breached == False,
            Case.status != CaseStatus.CLOSED,
        ).all()

        for case in overdue:
            case.sla_breached = True
            case.updated_at = now

            db.add(AuditLog(
                action="SLA_BREACHED",
                entity_type="CASE",
                entity_id=str(case.id),
                details={
                    "case_number": case.case_number,
                    "deadline": case.sla_deadline.isoformat(),
                    "breached_at": now.isoformat(),
                    "status": case.status,
                },
            ))

            breached.append({
                "case_number": case.case_number,
                "case_id": str(case.id),
                "deadline": case.sla_deadline.isoformat(),
            })

            log.warning(
                f"SLA BREACHED: {case.case_number} | "
                f"deadline={case.sla_deadline} | status={case.status}"
            )

        db.commit()

        log.info(f"SLA check complete: {len(breached)} breaches found")
        return {
            "checked_at": now.isoformat(),
            "breaches_found": len(breached),
            "cases": breached,
        }

    except Exception as e:
        log.error(f"SLA monitor error: {e}")
        db.rollback()
        return {"error": str(e)}

    finally:
        db.close()