"""
VIGIL — Screening Engine
THE HEART of the platform.
Orchestrates all 8 checks and returns a complete ScreeningResult.

8 Parameters:
  1. Name          — fuzzy match (RapidFuzz)
  2. DOB           — exact date match
  3. ID            — PAN/Aadhaar/Passport exact match
  4. Nationality   — country match
  5. Occupation    — high-risk keyword match
  6. Adverse Media — NewsAPI/GDELT search
  7. PEP           — politically exposed person
  8. Watchlist     — internal risk override (state-based)
"""
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.core.sanction_checker import check_sanction_list
from app.core.pep_checker import check_pep
from app.core.adverse_media import check_adverse_media
from app.core.id_matcher import check_ids
from app.core.watchlist_checker import check_watchlist, apply_watchlist_override
from app.core.threshold import (
    calculate_weighted_score,
    classify_risk,
    determine_alert_type,
    build_explainability,
)
from app.schemas.screening import ScreeningResult, ParamResult
from app.utils.logger import get_logger

log = get_logger(__name__)

SUSPICIOUS_OCCUPATIONS = [
    "arms dealer", "arms trader", "weapons dealer",
    "money changer", "hawala", "bullion trader",
]

RULE_VERSION = "1.0"

FEATURE_WEIGHTS_SNAPSHOT = {
    "name":          25,
    "dob":           15,
    "id":            20,
    "nationality":   10,
    "occupation":    5,
    "adverse_media": 10,
    "pep":           15,
}


def screen_customer(customer: Customer, db: Session) -> ScreeningResult:
    log.info(f"Screening: {customer.full_name} [{customer.id}]")

    # ── Param 1 — Name ────────────────────────────────────────────────
    sanction_result = check_sanction_list(
        db=db,
        full_name=customer.full_name,
        dob=customer.dob,
        nationality=customer.nationality,
    )
    name_matched = sanction_result["found"]
    name_fuzzy_score = sanction_result.get("best_score", 0)
    name_result = ParamResult(
        matched=name_matched,
        score=name_fuzzy_score,
        detail=sanction_result["entries"][0]["matched_name"]
        if name_matched else None,
    )

    # ── Param 2 — DOB ─────────────────────────────────────────────────
    dob_matched = (
        name_matched
        and customer.dob is not None
        and "dob" in sanction_result.get("matched_on", [])
    )
    dob_result = ParamResult(
        matched=dob_matched,
        score=100 if dob_matched else 0,
        detail=str(customer.dob) if dob_matched else None,
    )

    # ── Param 3 — ID ──────────────────────────────────────────────────
    id_check = check_ids(
        db=db,
        pan=customer.pan,
        aadhaar=customer.aadhaar,
        passport=customer.passport,
        din=customer.din,
        uin=customer.uin,
    )
    id_result = ParamResult(
        matched=id_check["matched"],
        score=100 if id_check["matched"] else 0,
        detail=f"{id_check['matched_field']}={id_check['matched_value']}"
        if id_check["matched"] else None,
    )

    # ── Param 4 — Nationality ─────────────────────────────────────────
    nat_matched = (
        name_matched
        and "nationality" in sanction_result.get("matched_on", [])
    ) if customer.nationality else False
    nat_result = ParamResult(
        matched=nat_matched,
        score=100 if nat_matched else 0,
        detail=customer.nationality if nat_matched else None,
    )

    # ── Param 5 — Occupation ──────────────────────────────────────────
    occ_matched = False
    if customer.occupation:
        occ_lower = customer.occupation.lower()
        occ_matched = any(s in occ_lower for s in SUSPICIOUS_OCCUPATIONS)
    occ_result = ParamResult(
        matched=occ_matched,
        score=100 if occ_matched else 0,
        detail=customer.occupation if occ_matched else None,
    )

    # ── Param 6 — Adverse Media ───────────────────────────────────────
    media_raw = check_adverse_media(customer.full_name)
    media_matched = media_raw.get("found", False)
    media_result = ParamResult(
        matched=media_matched,
        score=100 if media_matched else 0,
        detail=f"{media_raw.get('hit_count', 0)} articles"
        if media_matched else None,
    )

    # ── Param 7 — PEP ─────────────────────────────────────────────────
    pep_raw = check_pep(
        db=db,
        full_name=customer.full_name,
        dob=customer.dob
    )
    pep_matched = pep_raw["is_pep"]
    pep_result = ParamResult(
        matched=pep_matched,
        score=pep_raw.get("name_score", 0) if pep_matched else 0,
        detail=f"{pep_raw.get('pep_role')} ({pep_raw.get('pep_country')})"
        if pep_matched else None,
    )

    # ── Param 8 — Watchlist (risk override) ───────────────────────────
    watchlist_result = check_watchlist(
        db=db,
        customer_id=str(customer.id)
    )

    # ── Aggregate base score ───────────────────────────────────────────
    param_results = {
        "name":          {"matched": name_matched, "fuzzy_score": name_fuzzy_score},
        "dob":           {"matched": dob_matched},
        "id":            {"matched": id_check["matched"]},
        "nationality":   {"matched": nat_matched},
        "occupation":    {"matched": occ_matched},
        "adverse_media": {"matched": media_matched},
        "pep":           {"matched": pep_matched},
    }

    base_score, matched_params = calculate_weighted_score(param_results)

    # ── Apply watchlist override ───────────────────────────────────────
    weighted_score = apply_watchlist_override(base_score, watchlist_result)
    if watchlist_result["found"]:
        matched_params.append("watchlist")

    # ── Classify and explain ───────────────────────────────────────────
    risk_level = classify_risk(weighted_score)
    alert_type = determine_alert_type(matched_params, pep_raw, sanction_result)

    explainability = build_explainability(
        param_results=param_results,
        matched_params=matched_params,
        weighted_score=weighted_score,
        sanction_result=sanction_result,
        pep_result=pep_raw,
        media_result=media_raw,
    )

    # Add watchlist to explainability if found
    if watchlist_result["found"]:
        explainability["reasons"].append("WATCHLIST_HIT")
        explainability["evidence"].append({
            "param": "watchlist",
            "reason": "WATCHLIST_HIT",
            "detail": watchlist_result["reason"],
            "confidence": "100%",
            "weight_contributed": weighted_score - base_score,
        })
        explainability["auditor_summary"] += (
            f" Additionally, customer has watchlist history: "
            f"{watchlist_result['status']} "
            f"(impact: {watchlist_result['impact']})."
        )

    log.info(
        f"Done: {customer.full_name} | "
        f"base={base_score} | watchlist_score={weighted_score} | "
        f"risk={risk_level} | rule_version={RULE_VERSION}"
    )

    return ScreeningResult(
        customer_id=customer.id,
        customer_name=customer.full_name,
        name=name_result,
        dob=dob_result,
        id_check=id_result,
        nationality=nat_result,
        occupation=occ_result,
        adverse_media=media_result,
        pep=pep_result,
        matched_params=matched_params,
        params_matched_count=len(matched_params),
        weighted_score=weighted_score,
        risk_level=risk_level,
        alert_type=alert_type if matched_params else None,
        is_false_alert=(risk_level.value in ["LOW", "MEDIUM"]),
        explainability=explainability,
        screened_at=datetime.utcnow(),
    )