"""price_fetcher.py — yfinance로 주가 데이터 수집"""

import yfinance as yf


def fetch_price(ticker: str, is_korean: bool) -> dict | None:
    try:
        info = yf.Ticker(ticker).fast_info
        current = info.last_price
        prev    = info.previous_close

        if not current or not prev:
            return None

        change_pct = (current - prev) / prev * 100
        sign = "+" if change_pct >= 0 else ""

        if is_korean:
            price_str = f"{current:,.0f}원"
        else:
            price_str = f"${current:,.2f}"

        return {
            "price":      price_str,
            "change_pct": f"{sign}{change_pct:.1f}%",
            "is_up":      change_pct >= 0,
        }

    except Exception as e:
        print(f"[price_fetcher] {ticker} 오류: {e}")
        return None
