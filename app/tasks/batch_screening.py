from app.tasks.celery_app import celery_app
from app.db.database import SessionLocal
from app.models.customer import Customer
from app.models.audit_log import AuditLog
from app.core.screening_engine import screen_customer
from app.core.alert_router import route_alert
from app.utils.logger import get_logger

log = get_logger(__name__)


@celery_app.task(
    bind=True,
    max_retries=3,
    name="app.tasks.batch_screening.screen_batch"
)
def screen_batch(
    self,
    customer_ids: list[str],
    triggered_by: str = "system"
) -> dict:
    total = len(customer_ids)
    processed = 0
    high_count = 0
    auto_closed = 0
    errors = []

    log.info(f"Batch started: {total} customers | task={self.request.id}")

    db = SessionLocal()
    try:
        for i, cid in enumerate(customer_ids):
            try:
                customer = db.query(Customer).filter(
                    Customer.id == cid
                ).first()

                if not customer:
                    errors.append({"customer_id": cid, "error": "Not found"})
                    continue

                result = screen_customer(customer, db)
                alert = route_alert(result, db)

                if alert.risk_level.value == "HIGH":
                    high_count += 1
                else:
                    auto_closed += 1

                processed += 1

                if i % 10 == 0:
                    self.update_state(
                        state="PROGRESS",
                        meta={
                            "total": total,
                            "processed": processed,
                            "high_alerts": high_count,
                            "auto_closed": auto_closed,
                        },
                    )

            except Exception as e:
                log.error(f"Error screening {cid}: {e}")
                errors.append({"customer_id": cid, "error": str(e)})

        audit = AuditLog(
            user_email=triggered_by,
            action="BATCH_SCREENING_COMPLETE",
            entity_type="BATCH",
            entity_id=self.request.id,
            details={
                "total": total,
                "processed": processed,
                "high_alerts": high_count,
                "auto_closed": auto_closed,
                "errors": len(errors),
                "reduction_pct": round(
                    (auto_closed / processed * 100), 1
                ) if processed > 0 else 0,
            },
        )
        db.add(audit)
        db.commit()

    finally:
        db.close()

    summary = {
        "task_id": self.request.id,
        "total": total,
        "processed": processed,
        "high_alerts": high_count,
        "auto_closed": auto_closed,
        "errors": len(errors),
        "analyst_load_reduction_pct": round(
            (auto_closed / processed * 100), 1
        ) if processed > 0 else 0,
    }

    log.info(f"Batch complete: {summary}")
    return summary