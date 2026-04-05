import feedparser
from datetime import datetime

FF_RSS_URL = "https://forexfactory.com/ff_calendar_thisweek.xml"
USER_AGENT = "Mozilla/5.0"
MAX_EVENTS = 5

HIGH_IMPACT_VALUES = {"High", "Medium"}

# ForexFactory tags its entries with impact and currency in the summary/tags.
# The RSS feed exposes these as <impact> and <currency> custom elements under
# the "forexfactory" namespace — accessible via entry["ff_impact"] etc.
# We also fall back to scanning the raw summary string for robustness.


def _get_tag(entry: dict, field: str) -> str:
    """Read a ForexFactory namespace field, falling back to empty string."""
    return (entry.get(f"ff_{field}") or entry.get(field) or "").strip()


def _parse_date(entry: dict) -> str:
    """Return a readable date string from the entry, or empty string."""
    published = entry.get("published", "")
    for fmt in ("%a, %d %b %Y %H:%M:%S %z", "%a, %d %b %Y %H:%M:%S %Z"):
        try:
            dt = datetime.strptime(published, fmt)
            return dt.strftime("%a %b %d, %H:%M UTC")
        except ValueError:
            continue
    return published


def get_economic_events() -> str:
    try:
        feed = feedparser.parse(
            FF_RSS_URL,
            request_headers={"User-Agent": USER_AGENT},
        )

        events = []
        for entry in feed.entries:
            impact   = _get_tag(entry, "impact")
            currency = _get_tag(entry, "currency")

            if impact not in HIGH_IMPACT_VALUES:
                continue
            if currency.upper() != "USD":
                continue

            events.append({
                "title":    entry.get("title", "").strip(),
                "impact":   impact,
                "date":     _parse_date(entry),
                "forecast": _get_tag(entry, "forecast") or "—",
                "previous": _get_tag(entry, "previous") or "—",
            })

            if len(events) >= MAX_EVENTS:
                break

        if not events:
            return "Clean calendar today — no high impact USD events."

        lines = ["=== Economic Calendar (USD, High/Medium Impact) ==="]
        for e in events:
            impact_tag = f"[{e['impact'].upper()}]"
            lines.append(
                f"{impact_tag:<8} {e['date']:<24} {e['title']}"
                f"\n         Forecast: {e['forecast']}   Previous: {e['previous']}"
            )

        lines.append(f"\nFetched at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        return "\n".join(lines)

    except Exception:
        return "unavailable"


if __name__ == "__main__":
    print(get_economic_events())
