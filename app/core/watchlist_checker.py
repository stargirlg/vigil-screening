"""
VIGIL — Watchlist Checker
8th screening parameter — risk override system.
State-based scoring, not linear +points.
"""
from sqlalchemy.orm import Session
from app.models.watchlist import WatchlistEntry, WatchlistStatus
from app.utils.logger import get_logger
from uuid import UUID

log = get_logger(__name__)

STATUS_PRIORITY = {
    "FRAUD_CONFIRMED":     5,
    "SAR_FILED":           4,
    "UNDER_INVESTIGATION": 3,
    "PREVIOUS_ESCALATION": 2,
    "FALSE_POSITIVE":      1,
}


def check_watchlist(db: Session, customer_id: UUID) -> dict:
    entries = db.query(WatchlistEntry).filter(
        WatchlistEntry.customer_id == customer_id
    ).order_by(WatchlistEntry.added_at.desc()).all()

    if not entries:
        return {
            "found": False,
            "status": None,
            "entries": [],
            "score_override": None,
            "score_addition": 0,
            "impact": "NONE",
            "reason": "No watchlist history",
        }

    statuses = [e.status for e in entries]
    highest = max(statuses, key=lambda s: STATUS_PRIORITY.get(s, 0))

    result = {
        "found": True,
        "status": highest,
        "entries": [
            {
                "status": e.status,
                "reason": e.reason,
                "added_at": str(e.added_at),
                "case_reference": e.case_reference,
            }
            for e in entries[:5]
        ],
        "score_override": None,
        "score_addition": 0,
        "impact": "NONE",
        "reason": f"Customer has {len(entries)} watchlist entries. Highest: {highest}",
    }

    if highest == "FRAUD_CONFIRMED":
        result["score_override"] = 90
        result["impact"] = "HIGH"
    elif highest == "SAR_FILED":
        result["score_override"] = 75
        result["impact"] = "HIGH"
    elif highest == "UNDER_INVESTIGATION":
        result["score_override"] = 50
        result["score_addition"] = 10
        result["impact"] = "MEDIUM"
    elif highest == "PREVIOUS_ESCALATION":
        result["score_addition"] = 10
        result["impact"] = "LOW"
    elif highest == "FALSE_POSITIVE":
        result["score_override"] = None
        result["score_addition"] = 0
        result["impact"] = "NONE"

    log.info(
        f"Watchlist: {customer_id} | "
        f"status={highest} | impact={result['impact']}"
    )
    return result


def apply_watchlist_override(
    base_score: int,
    watchlist_result: dict,
) -> int:
    if not watchlist_result["found"]:
        return base_score

    override = watchlist_result.get("score_override")
    addition = watchlist_result.get("score_addition", 0)

    if override is not None:
        new_score = max(base_score, override)
    else:
        new_score = base_score + addition

    return min(new_score, 100)