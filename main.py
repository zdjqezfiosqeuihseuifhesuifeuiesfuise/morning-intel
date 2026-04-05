import asyncio
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()

from collectors.markets import get_market_data
from collectors.crypto import get_crypto_data
from collectors.economic_calendar import get_economic_events
from collectors.news import get_news
from collectors.conflicts import get_conflict_updates
from synthesis.summarizer import (
    synthesize_markets,
    synthesize_crypto,
    synthesize_conflicts,
    synthesize_edge,
)
from delivery.telegram import send_message


def _step(msg: str) -> None:
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}")


async def run() -> None:
    # ── 1. Collect ────────────────────────────────────────────
    _step("Collecting markets...")
    markets = get_market_data()

    _step("Collecting crypto...")
    crypto = get_crypto_data()

    _step("Collecting economic calendar...")
    calendar = get_economic_events()

    _step("Collecting news...")
    news = get_news()

    _step("Collecting conflict updates...")
    conflicts = get_conflict_updates()

    # ── 2. Day of week ────────────────────────────────────────
    day_of_week = datetime.now().strftime("%A")
    _step(f"Day of week: {day_of_week}")

    # ── 3-6. Synthesize ───────────────────────────────────────
    _step("Synthesizing markets report...")
    markets_report = synthesize_markets(markets, calendar, news)

    _step("Synthesizing crypto report...")
    crypto_report = synthesize_crypto(crypto)

    _step("Synthesizing conflicts report...")
    conflicts_report = synthesize_conflicts(conflicts)

    _step("Synthesizing daily edge report...")
    edge_report = synthesize_edge(day_of_week)

    # ── 7-13. Deliver ─────────────────────────────────────────
    _step("Sending markets report to Telegram...")
    await send_message(markets_report)

    _step("Waiting 3 seconds...")
    await asyncio.sleep(3)

    _step("Sending crypto report to Telegram...")
    await send_message(crypto_report)

    _step("Waiting 3 seconds...")
    await asyncio.sleep(3)

    _step("Sending conflicts report to Telegram...")
    await send_message(conflicts_report)

    _step("Waiting 3 seconds...")
    await asyncio.sleep(3)

    _step("Sending edge report to Telegram...")
    await send_message(edge_report)

    _step("Pipeline complete.")


async def main() -> None:
    try:
        await run()
    except Exception as e:
        _step(f"PIPELINE FAILED: {e}")
        await send_message("⚠️ Morning Intel failed — check GitHub Actions logs")
        raise


if __name__ == "__main__":
    asyncio.run(main())
