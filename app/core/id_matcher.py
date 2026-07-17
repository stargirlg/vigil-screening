from sqlalchemy.orm import Session
from app.models.sanction_entry import SanctionEntry
from app.utils.logger import get_logger

log = get_logger(__name__)


def normalize_id(value: str) -> str:
    return value.replace(" ", "").replace("-", "").upper().strip()


def check_ids(
    db: Session,
    pan: str | None = None,
    aadhaar: str | None = None,
    passport: str | None = None,
    din: str | None = None,
    uin: str | None = None,
) -> dict:
    customer_ids = {
        "pan": normalize_id(pan) if pan else None,
        "passport": normalize_id(passport) if passport else None,
    }
    customer_ids = {k: v for k, v in customer_ids.items() if v}

    if not customer_ids:
        return {
            "matched": False,
            "matched_field": None,
            "matched_value": None,
            "entry_name": None,
            "entry_source": None,
        }

    for field, value in customer_ids.items():
        col = getattr(SanctionEntry, field, None)
        if col is None:
            continue
        entry = db.query(SanctionEntry).filter(
            col == value,
            SanctionEntry.is_active == "true"
        ).first()
        if entry:
            return {
                "matched": True,
                "matched_field": field,
                "matched_value": value,
                "entry_name": entry.full_name,
                "entry_source": entry.source,
            }

    return {
        "matched": False,
        "matched_field": None,
        "matched_value": None,
        "entry_name": None,
        "entry_source": None,
    }