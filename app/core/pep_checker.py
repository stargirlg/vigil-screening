from datetime import date
from sqlalchemy.orm import Session
from app.core.fuzzy_matcher import match_name
from app.utils.logger import get_logger

log = get_logger(__name__)

SEED_PEP_LIST = [
    {"name": "Narendra Modi", "dob": date(1950, 9, 17), "role": "Prime Minister", "country": "India"},
    {"name": "Amit Shah", "dob": date(1964, 10, 22), "role": "Home Minister", "country": "India"},
    {"name": "Vladimir Putin", "dob": date(1952, 10, 7), "role": "President", "country": "Russia"},
    {"name": "Xi Jinping", "dob": date(1953, 6, 15), "role": "President", "country": "China"},
    {"name": "Kim Jong-un", "dob": date(1984, 1, 8), "role": "Supreme Leader", "country": "North Korea"},
    {"name": "Bashar al-Assad", "dob": date(1965, 9, 11), "role": "President", "country": "Syria"},
    {"name": "Dawood Ibrahim", "dob": date(1955, 12, 26), "role": "Organized Crime", "country": "Pakistan"},
]


def check_pep(
    db: Session,
    full_name: str,
    dob: date | None = None,
) -> dict:
    best_match = None
    best_score = 0

    for pep in SEED_PEP_LIST:
        matched, score = match_name(full_name, pep["name"])
        if matched and score > best_score:
            best_score = score
            best_match = pep

    if not best_match:
        return {
            "is_pep": False,
            "pep_name": None,
            "pep_role": None,
            "pep_country": None,
            "name_score": 0,
            "dob_confirmed": False,
        }

    dob_confirmed = False
    if dob and best_match.get("dob"):
        dob_confirmed = (dob == best_match["dob"])

    return {
        "is_pep": True,
        "pep_name": best_match["name"],
        "pep_role": best_match["role"],
        "pep_country": best_match["country"],
        "name_score": best_score,
        "dob_confirmed": dob_confirmed,
    }