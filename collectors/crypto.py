import requests
from datetime import datetime

TIMEOUT = 10

COINGECKO_PRICE_URL = (
    "https://api.coingecko.com/api/v3/simple/price"
    "?ids=bitcoin,solana"
    "&vs_currencies=usd"
    "&include_24hr_change=true"
    "&include_market_cap=true"
)
COINGECKO_GLOBAL_URL = "https://api.coingecko.com/api/v3/global"
FEAR_GREED_URL       = "https://api.alternative.me/fng/"
BINANCE_FUNDING_URL  = "https://fapi.binance.com/fapi/v1/fundingRate"


def _fetch_prices() -> dict:
    """BTC and SOL price, 24h change, market cap from CoinGecko."""
    resp = requests.get(COINGECKO_PRICE_URL, timeout=TIMEOUT)
    resp.raise_for_status()
    data = resp.json()

    result = {}
    for coin_id, label in [("bitcoin", "BTC"), ("solana", "SOL")]:
        coin = data.get(coin_id, {})
        result[label] = {
            "price":      coin.get("usd"),
            "change_24h": coin.get("usd_24h_change"),
            "market_cap": coin.get("usd_market_cap"),
        }
    return result


def _fetch_fear_greed() -> dict:
    """Fear & Greed index value and classification."""
    resp = requests.get(FEAR_GREED_URL, timeout=TIMEOUT)
    resp.raise_for_status()
    entry = resp.json()["data"][0]
    return {
        "value":          int(entry["value"]),
        "classification": entry["value_classification"],
    }


def _fetch_btc_dominance() -> float:
    """BTC dominance % from CoinGecko global endpoint."""
    resp = requests.get(COINGECKO_GLOBAL_URL, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()["data"]["market_cap_percentage"]["btc"]


def _fetch_funding_rate(symbol: str) -> float:
    """Latest perpetual funding rate for a Binance USDT-margined symbol."""
    resp = requests.get(
        BINANCE_FUNDING_URL,
        params={"symbol": symbol, "limit": 1},
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    return float(resp.json()[0]["fundingRate"])


def get_crypto_data() -> str:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = ["=== Crypto Snapshot ==="]

    # --- Prices, 24h change, market cap ---
    try:
        prices = _fetch_prices()
        for label, d in prices.items():
            price     = f"${d['price']:,.2f}"          if d["price"]      is not None else "n/a"
            chg       = d["change_24h"]
            chg_str   = f"{'+' if chg >= 0 else ''}{chg:.2f}%" if chg is not None else "n/a"
            mcap      = d["market_cap"]
            mcap_str  = f"${mcap / 1e9:.1f}B"          if mcap is not None else "n/a"
            lines.append(
                f"{label:<6}  Price: {price:>12}   24h: {chg_str:>8}   MCap: {mcap_str}"
            )
    except Exception:
        lines.append("BTC/SOL prices: unavailable")

    lines.append("")

    # --- Fear & Greed ---
    try:
        fg = _fetch_fear_greed()
        lines.append(f"Fear & Greed Index:  {fg['value']} / 100  ({fg['classification']})")
    except Exception:
        lines.append("Fear & Greed Index:  unavailable")

    # --- BTC Dominance ---
    try:
        dom = _fetch_btc_dominance()
        lines.append(f"BTC Dominance:       {dom:.1f}%")
    except Exception:
        lines.append("BTC Dominance:       unavailable")

    lines.append("")

    # --- Funding Rates ---
    for symbol, label in [("BTCUSDT", "BTC"), ("SOLUSDT", "SOL")]:
        try:
            rate = _fetch_funding_rate(symbol)
            lines.append(f"{label} Funding Rate:  {rate * 100:.4f}%")
        except Exception:
            lines.append(f"{label} Funding Rate:  unavailable")

    lines.append(f"\nFetched at: {ts}")
    return "\n".join(lines)


if __name__ == "__main__":
    print(get_crypto_data())
