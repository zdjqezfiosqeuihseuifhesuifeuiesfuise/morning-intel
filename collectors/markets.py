import yfinance as yf
from datetime import datetime


TICKERS = {
    "Nasdaq 100 Futures": "NQ=F",
    "S&P 500":            "^GSPC",
    "Nasdaq Composite":   "^IXIC",
    "Dow Jones":          "^DJI",
    "VIX":                "^VIX",
    "10Y Treasury Yield": "^TNX",
    "US Dollar Index":    "DX-Y.NYB",
}


def _fetch_ticker(symbol: str) -> dict:
    ticker = yf.Ticker(symbol)
    fi = ticker.fast_info

    price = fi.last_price
    prev_close = fi.previous_close

    if prev_close and prev_close != 0:
        change_pct = ((price - prev_close) / prev_close) * 100
    else:
        change_pct = None

    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return {
        "price": round(price, 4),
        "change_pct": round(change_pct, 2) if change_pct is not None else None,
        "timestamp": ts,
    }


def get_market_data() -> str:
    lines = ["=== Market Snapshot ==="]

    for name, symbol in TICKERS.items():
        try:
            data = _fetch_ticker(symbol)
            price = data["price"]
            pct = data["change_pct"]
            ts = data["timestamp"]

            if pct is not None:
                arrow = "+" if pct >= 0 else ""
                change_str = f"{arrow}{pct:.2f}%"
            else:
                change_str = "n/a"

            lines.append(f"{name:<24} {price:>12.4f}   {change_str:>8}   [{ts}]")

        except Exception:
            lines.append(f"{name:<24} {'unavailable':>12}")

    lines.append(f"\nFetched at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return "\n".join(lines)


if __name__ == "__main__":
    print(get_market_data())
