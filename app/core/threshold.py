from app.config import settings
from app.models.alert import RiskLevel

WEIGHTS = {
    "name":          settings.WEIGHT_NAME,
    "dob":           settings.WEIGHT_DOB,
    "id":            settings.WEIGHT_ID,
    "nationality":   settings.WEIGHT_NATIONALITY,
    "occupation":    settings.WEIGHT_OCCUPATION,
    "adverse_media": settings.WEIGHT_ADVERSE_MEDIA,
    "pep":           settings.WEIGHT_PEP,
}


def calculate_weighted_score(param_results: dict) -> tuple[int, list[str]]:
    total_score = 0
    matched_params = []

    for param, weight in WEIGHTS.items():
        result = param_results.get(param, {})
        matched = result.get("matched", False)
        if not matched:
            continue
        if param == "name":
            fuzzy_score = result.get("fuzzy_score", 100)
            contribution = int((fuzzy_score / 100) * weight)
        else:
            contribution = weight
        total_score += contribution
        matched_params.append(param)

    return min(total_score, 100), matched_params


def classify_risk(weighted_score: int) -> RiskLevel:
    if weighted_score >= 75:
        return RiskLevel.CRITICAL
    elif weighted_score >= 50:
        return RiskLevel.HIGH
    elif weighted_score >= 30:
        return RiskLevel.MEDIUM
    else:
        return RiskLevel.LOW


def build_explainability(
    param_results: dict,
    matched_params: list[str],
    weighted_score: int,
    sanction_result: dict,
    pep_result: dict,
    media_result: dict,
) -> dict:
    reasons = []
    evidence = []

    if "name" in matched_params:
        score = param_results["name"].get("fuzzy_score", 0)
        entry = sanction_result.get("entries", [{}])[0]
        reasons.append("SANCTION_NAME_MATCH")
        evidence.append({
            "param": "name",
            "reason": "SANCTION_NAME_MATCH",
            "detail": f"Matched '{entry.get('matched_name')}' in "
                      f"{entry.get('source', 'OFAC')} list",
            "confidence": f"{score}%",
            "weight_contributed": int((score / 100) * WEIGHTS["name"]),
        })

    if "dob" in matched_params:
        reasons.append("DOB_CONFIRMED")
        evidence.append({
            "param": "dob",
            "reason": "DOB_CONFIRMED",
            "detail": "Date of birth matches sanction entry exactly",
            "confidence": "100%",
            "weight_contributed": WEIGHTS["dob"],
        })

    if "id" in matched_params:
        reasons.append("ID_EXACT_MATCH")
        evidence.append({
            "param": "id",
            "reason": "ID_EXACT_MATCH",
            "detail": "Government ID matched sanction entry",
            "confidence": "100%",
            "weight_contributed": WEIGHTS["id"],
        })

    if "nationality" in matched_params:
        reasons.append("NATIONALITY_MATCH")
        evidence.append({
            "param": "nationality",
            "reason": "NATIONALITY_MATCH",
            "detail": "Nationality matches sanctioned entity",
            "confidence": "100%",
            "weight_contributed": WEIGHTS["nationality"],
        })

    if "occupation" in matched_params:
        reasons.append("SUSPICIOUS_OCCUPATION")
        evidence.append({
            "param": "occupation",
            "reason": "SUSPICIOUS_OCCUPATION",
            "detail": "Occupation flagged as high-risk sector",
            "confidence": "100%",
            "weight_contributed": WEIGHTS["occupation"],
        })

    if "adverse_media" in matched_params:
        reasons.append("ADVERSE_MEDIA_HIT")
        evidence.append({
            "param": "adverse_media",
            "reason": "ADVERSE_MEDIA_HIT",
            "detail": f"{media_result.get('hit_count', 0)} adverse articles found",
            "confidence": "high",
            "weight_contributed": WEIGHTS["adverse_media"],
        })

    if "pep" in matched_params:
        reasons.append("PEP_MATCH")
        evidence.append({
            "param": "pep",
            "reason": "PEP_MATCH",
            "detail": f"{pep_result.get('pep_name')} — "
                      f"{pep_result.get('pep_role')} "
                      f"({pep_result.get('pep_country')})",
            "confidence": f"{pep_result.get('name_score', 0)}%",
            "weight_contributed": WEIGHTS["pep"],
        })

    return {
        "total_score": weighted_score,
        "reasons": reasons,
        "evidence": evidence,
        "auditor_summary": _build_summary(reasons, weighted_score),
    }


def _build_summary(reasons: list[str], score: int) -> str:
    if not reasons:
        return "No matches found. Customer passed all screening parameters."

    parts = []
    if "SANCTION_NAME_MATCH" in reasons:
        parts.append("name matched a sanctioned entity")
    if "DOB_CONFIRMED" in reasons:
        parts.append("date of birth confirmed")
    if "ID_EXACT_MATCH" in reasons:
        parts.append("government ID matched")
    if "NATIONALITY_MATCH" in reasons:
        parts.append("nationality matched")
    if "SUSPICIOUS_OCCUPATION" in reasons:
        parts.append("occupation flagged as high-risk")
    if "ADVERSE_MEDIA_HIT" in reasons:
        parts.append("adverse media found")
    if "PEP_MATCH" in reasons:
        parts.append("identified as politically exposed person")

    return (
        "Customer flagged because: "
        + ", ".join(parts)
        + f". Total risk score: {score}/100."
    )


def determine_alert_type(
    matched_params: list[str],
    pep_result: dict,
    sanction_result: dict,
) -> str:
    if sanction_result.get("found") and "name" in matched_params:
        if len(matched_params) >= 3:
            return "FULL_SANCTION_MATCH"
        return "PARTIAL_MATCH"
    if pep_result.get("is_pep"):
        return "PEP_HIT"
    if "adverse_media" in matched_params:
        return "ADVERSE_MEDIA_HIT"
    return "PARTIAL_MATCH"