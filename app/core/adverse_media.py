import httpx
from app.config import settings
from app.utils.logger import get_logger

log = get_logger(__name__)

ADVERSE_KEYWORDS = [
    "fraud", "money laundering", "terror", "terrorist", "sanction",
    "arrested", "convicted", "smuggling", "corruption", "bribery",
    "cartel", "hawala", "black money", "benami", "scam", "ponzi",
    "criminal", "indicted", "charged", "fugitive", "wanted",
]


def _contains_adverse_keyword(text: str) -> list[str]:
    text_lower = text.lower()
    return [kw for kw in ADVERSE_KEYWORDS if kw in text_lower]


def check_adverse_media_newsapi(full_name: str) -> dict:
    if not settings.NEWS_API_KEY:
        return {"found": False, "source": "newsapi", "skipped": True}

    try:
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": f'"{full_name}" AND (fraud OR "money laundering" OR terror OR sanction)',
            "language": "en",
            "sortBy": "relevancy",
            "pageSize": 5,
            "apiKey": settings.NEWS_API_KEY,
        }
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()

        articles = data.get("articles", [])
        hits = []
        for art in articles:
            text = f"{art.get('title', '')} {art.get('description', '')}"
            keywords_found = _contains_adverse_keyword(text)
            if keywords_found:
                hits.append({
                    "title": art.get("title"),
                    "url": art.get("url"),
                    "published_at": art.get("publishedAt"),
                    "keywords": keywords_found,
                })

        return {
            "found": bool(hits),
            "source": "newsapi",
            "articles": hits,
            "hit_count": len(hits),
        }

    except Exception as e:
        log.error(f"NewsAPI error for {full_name}: {e}")
        return {"found": False, "source": "newsapi", "error": str(e)}


def check_adverse_media_gdelt(full_name: str) -> dict:
    if not settings.GDELT_ENABLED:
        return {"found": False, "source": "gdelt", "skipped": True}

    try:
        url = "https://api.gdeltproject.org/api/v2/doc/doc"
        params = {
            "query": f'"{full_name}" (fraud OR terror OR sanction OR corruption)',
            "mode": "ArtList",
            "maxrecords": 10,
            "format": "json",
        }
        with httpx.Client(timeout=15.0) as client:
            resp = client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()

        articles = data.get("articles", [])
        hits = []
        for art in articles:
            text = f"{art.get('title', '')} {art.get('seendate', '')}"
            keywords_found = _contains_adverse_keyword(text)
            hits.append({
                "title": art.get("title"),
                "url": art.get("url"),
                "keywords": keywords_found,
            })

        return {
            "found": bool(hits),
            "source": "gdelt",
            "articles": hits[:5],
            "hit_count": len(hits),
        }

    except Exception as e:
        log.error(f"GDELT error for {full_name}: {e}")
        return {"found": False, "source": "gdelt", "error": str(e)}


def check_adverse_media(full_name: str) -> dict:
    result = check_adverse_media_newsapi(full_name)
    if result.get("skipped") or result.get("error"):
        result = check_adverse_media_gdelt(full_name)
    return result