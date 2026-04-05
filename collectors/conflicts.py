import os
import requests
from datetime import datetime

NEWSAPI_URL = "https://newsapi.org/v2/everything"
TIMEOUT     = 10
MAX_TOTAL   = 10

TOPICS = [
    ("Ukraine Russia war",       "Ukraine/Russia"),
    ("Iran Israel tensions",     "Iran/Israel"),
    ("Taiwan China military",    "Taiwan/China"),
    ("Middle East conflict",     "Middle East"),
    ("North Korea",              "North Korea"),
]


def _fetch_top2(query: str, api_key: str) -> list[dict]:
    resp = requests.get(
        NEWSAPI_URL,
        params={
            "q":        query,
            "pageSize": 2,
            "sortBy":   "publishedAt",
            "language": "en",
            "apiKey":   api_key,
        },
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json().get("articles", [])


def _format_date(iso: str) -> str:
    try:
        dt = datetime.strptime(iso, "%Y-%m-%dT%H:%M:%SZ")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        return iso


def get_conflict_updates() -> str:
    api_key = os.environ["NEWS_API_KEY"]
    ts      = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines   = ["=== Conflict & Geopolitical Watch ==="]

    collected = 0
    for query, topic_label in TOPICS:
        if collected >= MAX_TOTAL:
            break
        try:
            articles = _fetch_top2(query, api_key)
            for article in articles:
                if collected >= MAX_TOTAL:
                    break
                title   = (article.get("title") or "No title").strip()
                source  = (article.get("source") or {}).get("name") or "Unknown"
                date    = _format_date(article.get("publishedAt") or "")
                lines.append(f"[{topic_label}] {title} — {source} ({date})")
                collected += 1
        except Exception:
            lines.append(f"[{topic_label}] unavailable")

    if collected == 0:
        lines.append("No conflict updates available.")

    lines.append(f"\nFetched at: {ts}")
    return "\n".join(lines)


if __name__ == "__main__":
    print(get_conflict_updates())
