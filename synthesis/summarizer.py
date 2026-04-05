import os
from datetime import datetime

import anthropic

MODEL      = "claude-haiku-4-5-20251001"
MAX_TOKENS = 1000


def _client() -> anthropic.Anthropic:
    return anthropic.Anthropic(api_key=os.environ["CLAUDE_API_KEY"])


def _call(prompt: str) -> str:
    response = _client().messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


# ─────────────────────────────────────────────
# Function 1 — Markets + Calendar + News
# ─────────────────────────────────────────────

def synthesize_markets(markets: str, calendar: str, news: str) -> str:
    now        = datetime.now()
    day        = now.strftime("%A")
    date_str   = now.strftime("%B %d, %Y")

    prompt = f"""You are a professional NQ futures trader writing a morning briefing for other traders.

Use ONLY the data provided below — never invent numbers, prices, or levels.
If a piece of data is missing or marked unavailable, write "unavailable" for that field.

Output this EXACT format — no deviations, no extra sections:

☀️ MORNING INTEL — {day} {date_str}
─────────────────────────
⚠️ MACRO RISK METER: [🟢 LOW / 🟡 MEDIUM / 🔴 HIGH — pick one]
[One line: why this risk level + trade size recommendation]
─────────────────────────
📊 US INDICES

US100 (NQ):
- Price + % change
- Driver: [one sentence, specific, from the news/calendar data]
- Key level: [support or resistance — from market data only]
- Bias: [BULLISH / BEARISH / NEUTRAL] — [one reason]

US500 (ES):
- Price + % change
- Driver: [one sentence, specific]
- Key level: [support or resistance]
- Bias: [BULLISH / BEARISH / NEUTRAL] — [one reason]

US30 (YM):
- Price + % change
- Driver: [one sentence, specific]
- Key level: [support or resistance]
- Bias: [BULLISH / BEARISH / NEUTRAL] — [one reason]

NQ priority today: [one actionable sentence for NQ traders]
─────────────────────────
🗓 MACRO CALENDAR
[List only HIGH and MEDIUM impact USD events. Format each as:]
[🔴 for HIGH / 🟡 for MEDIUM] [time ET] — [event name]
Consensus: [value] | Previous: [value]
NQ impact: [one sentence]

[If no events: write "No high-impact USD events today."]

Rules:
- Max 300 words total
- Direct trader language
- No invented numbers — use only provided data

---
MARKET DATA:
{markets}

ECONOMIC CALENDAR:
{calendar}

NEWS:
{news}
"""
    return _call(prompt)


# ─────────────────────────────────────────────
# Function 2 — Crypto
# ─────────────────────────────────────────────

def synthesize_crypto(crypto: str) -> str:
    prompt = f"""You are a crypto-aware futures trader. Write a concise crypto briefing for NQ/SOL traders.

Use ONLY the data provided. Never invent numbers.
If data is missing write "unavailable".

Output this EXACT format:

₿ CRYPTO INTEL

BTC: [price] | [% change]
SOL: [price] | [% change]

😱 Fear & Greed: [value] — [classification]
[One sentence: what this means for position sizing right now]

BTC Dominance: [%]
[One sentence: what this means for altcoins today]

Funding Rates:
BTC: [rate] — [neutral / elevated / extreme]
SOL: [rate] — [neutral / elevated / extreme]

Sentiment: [2-3 sentences connecting crypto momentum to NQ correlation and SOL trade setup]
Watch: [one specific actionable alert — price level, rate threshold, or divergence]

Rules: max 150 words, no fluff, trader language only.

---
CRYPTO DATA:
{crypto}
"""
    return _call(prompt)


# ─────────────────────────────────────────────
# Function 3 — Conflicts
# ─────────────────────────────────────────────

def synthesize_conflicts(conflicts: str) -> str:
    prompt = f"""You are a geopolitical risk analyst writing for futures traders.

Use ONLY the data provided. Do not invent events or details.
Select the 3-5 most market-relevant conflicts or tensions from the data.

Output this EXACT format:

⚔️ GLOBAL CONFLICT INTEL

[For each conflict:]
📍 [Location] — [Parties involved]
Status: [one sentence — what happened this week]
Market impact: [which assets are affected: oil, gold, bonds, equities, crypto]
Risk: [🟢 LOW / 🟡 MEDIUM / 🔴 HIGH]

Geopolitical risk this week: [🟢 LOW / 🟡 MEDIUM / 🔴 HIGH] — [one sentence reason]

Rules: max 200 words, neutral tone, only include conflicts with clear market relevance.

---
CONFLICT DATA:
{conflicts}
"""
    return _call(prompt)


# ─────────────────────────────────────────────
# Function 4 — Daily Edge
# ─────────────────────────────────────────────

def synthesize_edge(day_of_week: str) -> str:
    day_context = {
        "Monday":    "liquidity sweep, stop hunts from weekend gaps, Asian session range",
        "Tuesday":   "trend day setup, NY open momentum, institutional order flow",
        "Wednesday": "continuation of weekly trend, mid-week liquidity, FOMC if scheduled",
        "Thursday":  "reversal watch, exhaustion signals, Thursday liquidity run",
        "Friday":    "weekly close, profit taking, reduced size, avoid late entries",
    }.get(day_of_week, "standard session rules apply")

    prompt = f"""You are an ICT-trained NQ futures trader writing a daily edge briefing.
Today is {day_of_week}. Day context: {day_context}.

Output this EXACT format — nothing before or after:

⚡ DAILY EDGE — {day_of_week}

📈 ICT Insight:
[One specific ICT concept most relevant to {day_of_week} — e.g. liquidity voids, OTE entries, FVG fills, BSL/SSL sweeps, killzone timing. Be specific, not generic.]

🌍 Macro Insight:
[One specific macro concept relevant to current market conditions — e.g. rate expectations, dollar correlation, risk-on/risk-off, yield curve. Actionable.]

🧠 Mindset:
"[One sharp quote — trading-focused, not generic motivation. Attribute if real, otherwise no attribution.]"

Rules: max 150 words total, every sentence must be actionable or specific.
"""
    return _call(prompt)


# ─────────────────────────────────────────────
# Convenience wrapper used by main.py
# ─────────────────────────────────────────────

def generate_brief(markets: str, crypto: str, news: str, conflicts: str, calendar: str) -> str:
    day = datetime.now().strftime("%A")
    sections = [
        synthesize_markets(markets, calendar, news),
        synthesize_crypto(crypto),
        synthesize_conflicts(conflicts),
        synthesize_edge(day),
    ]
    return "\n\n".join(sections)
