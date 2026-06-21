"""price_fetcher.py — yfinance로 가장 최근 거래일 종가 수집"""

import yfinance as yf


def fetch_price(ticker: str, is_korean: bool) -> dict | None:
    """
    가장 최근 거래일의 종가와 전일 대비 등락률 반환.
    주말/공휴일에도 마지막 거래일 데이터를 가져옴.
    """
    try:
        # 최근 5거래일 데이터 가져오기 (주말/공휴일 고려)
        hist = yf.Ticker(ticker).history(period="5d")

        if hist.empty or len(hist) < 2:
            print(f"[price_fetcher] {ticker} 데이터 부족")
            return None

        # 가장 최근 거래일 종가
        latest = hist.iloc[-1]
        prev   = hist.iloc[-2]

        current    = latest["Close"]
        prev_close = prev["Close"]
        trade_date = hist.index[-1].strftime("%m/%d")

        change_pct = (current - prev_close) / prev_close * 100
        sign = "+" if change_pct >= 0 else ""

        if is_korean:
            price_str = f"{current:,.0f}원"
        else:
            price_str = f"${current:,.2f}"

        return {
            "price":      price_str,
            "change_pct": f"{sign}{change_pct:.1f}%",
            "is_up":      change_pct >= 0,
            "date":       trade_date,
        }

    except Exception as e:
        print(f"[price_fetcher] {ticker} 오류: {e}")
        return None
