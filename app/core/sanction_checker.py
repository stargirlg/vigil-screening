from datetime import date
from sqlalchemy.orm import Session
from app.models.sanction_entry import SanctionEntry
from app.core.fuzzy_matcher import match_name, match_aliases
from app.utils.logger import get_logger

log = get_logger(__name__)


def check_sanction_list(
    db: Session,
    full_name: str,
    dob: date | None = None,
    nationality: str | None = None,
) -> dict:
    entries = db.query(SanctionEntry).filter(
        SanctionEntry.is_active == "true"
    ).all()

    if not entries:
        log.warning("Sanction list is empty")
        return {
            "found": False,
            "entries": [],
            "best_score": 0,
            "matched_on": []
        }

    matches = []

    for entry in entries:
        name_matched, name_score = match_name(full_name, entry.full_name)

        alias_matched, alias_score = match_aliases(
            full_name,
            entry.aliases if isinstance(entry.aliases, list) else []
        )

        best_name_score = max(name_score, alias_score)
        name_hit = name_matched or alias_matched

        if not name_hit:
            continue

        matched_on = ["name"]

        dob_match = False
        if dob and entry.dob:
            dob_match = (dob == entry.dob)
            if dob_match:
                matched_on.append("dob")

        nat_match = False
        if nationality and entry.nationality:
            nat_match = nationality.lower() == entry.nationality.lower()
            if nat_match:
                matched_on.append("nationality")

        matches.append({
            "entry_id": str(entry.id),
            "source": entry.source,
            "source_id": entry.source_id,
            "matched_name": entry.full_name,
            "name_score": best_name_score,
            "dob_match": dob_match,
            "nationality_match": nat_match,
            "matched_on": matched_on,
            "program": entry.program,
            "reason": entry.reason,
        })

    if not matches:
        return {
            "found": False,
            "entries": [],
            "best_score": 0,
            "matched_on": []
        }

    matches.sort(key=lambda x: x["name_score"], reverse=True)
    best = matches[0]

    return {
        "found": True,
        "entries": matches,
        "best_score": best["name_score"],
        "matched_on": best["matched_on"],
    }