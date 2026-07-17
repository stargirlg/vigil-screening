from app.tasks.celery_app import celery_app
from app.db.database import SessionLocal
from app.models.sanction_entry import SanctionEntry
from app.models.audit_log import AuditLog
from app.utils.ofac_parser import download_and_parse_ofac
from app.config import settings
from app.utils.logger import get_logger

log = get_logger(__name__)


@celery_app.task(name="app.tasks.sanction_sync.sync_ofac_list")
def sync_ofac_list() -> dict:
    log.info("Starting OFAC sanction list sync...")
    db = SessionLocal()

    try:
        entries = download_and_parse_ofac(settings.OFAC_SDN_URL)

        if not entries:
            log.error("No entries downloaded — aborting sync")
            return {"status": "FAILED", "reason": "No entries downloaded"}

        db.query(SanctionEntry).filter(
            SanctionEntry.source == "OFAC"
        ).update({"is_active": "false"})

        for entry in entries:
            db.add(entry)

        db.commit()

        audit = AuditLog(
            action="SANCTION_LIST_SYNCED",
            entity_type="SYSTEM",
            details={
                "source": "OFAC",
                "entries_loaded": len(entries)
            },
        )
        db.add(audit)
        db.commit()

        log.info(f"OFAC sync complete: {len(entries)} entries")
        return {
            "status": "SUCCESS",
            "source": "OFAC",
            "entries": len(entries)
        }

    except Exception as e:
        log.error(f"OFAC sync failed: {e}")
        db.rollback()
        return {"status": "FAILED", "error": str(e)}

    finally:
        db.close()