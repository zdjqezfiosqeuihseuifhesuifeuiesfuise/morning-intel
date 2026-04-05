import os
import requests
from datetime import datetime

NEWSAPI_URL = "https://newsapi.org/v2/everything"
TIMEOUT     = 10

QUERIES = {
    "Market News": (
        "Nasdaq OR S&P500 OR Federal Reserve OR inflation OR earnings"
    ),
    "Geopolitical News": (
        "Ukraine OR Iran OR Taiwan OR Middle East OR sanctions"
    ),
}


def _fetch_articles(query: str, api_key: str) -> list[dict]:
    resp = requests.get(
        NEWSAPI_URL,
        params={
            "q":        query,
            "pageSize": 5,
            "sortBy":   "publishedAt",
            "language": "en",
            "apiKey":   api_key,
        },
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json().get("articles", [])


def _format_article(article: dict) -> str:
    title      = article.get("title") or "No title"
    source     = (article.get("source") or {}).get("name") or "Unknown source"
    published  = article.get("publishedAt") or ""

    # Reformat ISO timestamp -> readable, e.g. "2024-04-05 06:30"
    try:
        dt = datetime.strptime(published, "%Y-%m-%dT%H:%M:%SZ")
        published = dt.strftime("%Y-%m-%d %H:%M UTC")
    except ValueError:
        pass

    return f"  [{source}]  {published}\n  {title}"


def get_news() -> str:
    api_key = os.environ["NEWS_API_KEY"]
    ts      = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines   = ["=== News Snapshot ==="]

    for section, query in QUERIES.items():
        lines.append(f"\n-- {section} --")
        try:
            articles = _fetch_articles(query, api_key)
            if not articles:
                lines.append("  (no results)")
            else:
                for article in articles:
                    lines.append(_format_article(article))
                    lines.append("")
        except Exception:
            lines.append("  unavailable")

    lines.append(f"\nFetched at: {ts}")
    return "\n".join(lines)


if __name__ == "__main__":
    print(get_news())
