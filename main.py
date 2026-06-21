"""main.py — 주가 + 뉴스 수집 후 카카오톡 전송"""

import json
import os
import sys
from datetime import datetime, timezone, timedelta

from price_fetcher import fetch_price
from news_fetcher import fetch_news
from kakao_sender import send_message

KST = timezone(timedelta(hours=9))
STOCKS_FILE = os.path.join(os.path.dirname(__file__), "stocks.json")
MARKET = os.environ.get("MARKET", "KR").upper()


def load_stocks() -> list[dict]:
    with open(STOCKS_FILE, encoding="utf-8") as f:
        data = json.load(f)
    return data["korean"] if MARKET == "KR" else data["us"]


def build_stock_section(stock: dict) -> str:
    is_korean = MARKET == "KR"
    ticker    = stock["ticker"]
    name      = stock["name"]
    code      = stock["code"]

    price_data = fetch_price(ticker, is_korean)
    if price_data:
        arrow      = "▲" if price_data["is_up"] else "▼"
        price_line = f"현재가: {price_data['price']} ({arrow}{price_data['change_pct']})"
    else:
        price_line = "현재가: 데이터 없음"

    news_list = fetch_news(f"{name} 주식")
    news_lines = []
    for i, news in enumerate(news_list, 1):
        news_lines.append(f"  {i}. {news['title']}\n     🔗 {news['link']}")

    news_block = "\n".join(news_lines) if news_lines else "  관련 뉴스 없음"

    return (
        f"■ {name} ({code})\n"
        f"- {price_line}\n"
        f"- 주요 뉴스:\n{news_block}"
    )


def build_message(stocks: list[dict]) -> str:
    now  = datetime.now(KST).strftime("%Y-%m-%d %H:%M")
    tag  = "🇰🇷 국장" if MARKET == "KR" else "🇺🇸 미장"
    header = f"[🤖 오늘의 {tag} 주식&뉴스 요약]\n📅 {now} 기준\n\n"

    sections = []
    for stock in stocks:
        print(f"[main] {stock['name']} 수집 중...")
        sections.append(build_stock_section(stock))

    return header + "\n\n".join(sections)


def main():
    stocks = load_stocks()
    if not stocks:
        print("[main] 종목 없음. stocks.json을 확인하세요.")
        sys.exit(1)

    message = build_message(stocks)
    print("\n──────── 전송할 메시지 미리보기 ────────")
    print(message)
    print("────────────────────────────────────────\n")

    success = send_message(message)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
