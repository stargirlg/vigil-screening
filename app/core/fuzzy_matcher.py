from rapidfuzz import fuzz, process
from app.config import settings
from app.utils.logger import get_logger

log = get_logger(__name__)

THRESHOLD = settings.FUZZY_NAME_THRESHOLD


def normalize(name: str) -> str:
    return " ".join(name.lower().strip().split())


def match_name(customer_name: str, candidate_name: str) -> tuple[bool, int]:
    cn = normalize(customer_name)
    cd = normalize(candidate_name)

    scores = [
        fuzz.token_sort_ratio(cn, cd),
        fuzz.token_set_ratio(cn, cd),
        fuzz.partial_ratio(cn, cd),
        fuzz.ratio(cn, cd),
    ]
    best = max(scores)
    return (best >= THRESHOLD, best)


def match_name_against_list(
    customer_name: str,
    sanction_names: list[str],
    limit: int = 5,
) -> list[dict]:
    cn = normalize(customer_name)
    results = process.extract(
        cn,
        [normalize(n) for n in sanction_names],
        scorer=fuzz.token_sort_ratio,
        limit=limit,
        score_cutoff=THRESHOLD,
    )
    return [
        {"name": sanction_names[idx], "score": score}
        for _, score, idx in results
    ]


def match_aliases(
    customer_name: str,
    aliases: list[str]
) -> tuple[bool, int]:
    if not aliases:
        return False, 0

    best_score = 0
    for alias in aliases:
        matched, score = match_name(customer_name, alias)
        if score > best_score:
            best_score = score
        if matched:
            return True, best_score

    return False, best_score