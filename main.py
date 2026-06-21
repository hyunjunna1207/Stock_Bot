"""main.py — 주가 + 뉴스 수집 후 카카오톡 전송 (종목별 분리)"""

import json
import os
import sys
import time
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


def build_stock_message(stock: dict) -> str:
    is_korean = MARKET == "KR"
    ticker = stock["ticker"]
    name   = stock["name"]
    code   = stock["code"]

    # 주가 (가장 최근 거래일 종가)
    price_data = fetch_price(ticker, is_korean)
    if price_data:
        arrow = "▲" if price_data["is_up"] else "▼"
        price_line = f"{price_data['price']} ({arrow}{price_data['change_pct']}) [{price_data['date']} 종가]"
    else:
        price_line = "데이터 없음"

    # 뉴스
    news_list = fetch_news(f"{name} 주식")
    news_lines = []
    for i, news in enumerate(news_list, 1):
        news_lines.append(f"  {i}. {news['title']}\n     🔗 {news['link']}")

    news_block = "\n".join(news_lines) if news_lines else "  관련 뉴스 없음"

    tag = "🇰🇷" if MARKET == "KR" else "🇺🇸"
    now = datetime.now(KST).strftime("%m/%d %H:%M")

    return (
        f"{tag} [{now}] 장 시작 전 리포트\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"■ {name} ({code})\n"
        f"💰 전일 종가: {price_line}\n\n"
        f"📰 주요 뉴스\n"
        f"{news_block}"
    )


def main():
    stocks = load_stocks()
    if not stocks:
        print("[main] 종목 없음. stocks.json을 확인하세요.")
        sys.exit(1)

    failed = 0
    for stock in stocks:
        print(f"[main] {stock['name']} 처리 중...")
        msg = build_stock_message(stock)

        print(msg)
        print("─" * 30)

        ok = send_message(msg)
        if not ok:
            failed += 1

        time.sleep(1)

    if failed:
        print(f"[main] {failed}개 종목 전송 실패")
        sys.exit(1)
    else:
        print(f"[main] 전체 {len(stocks)}개 종목 전송 완료 ✅")


if __name__ == "__main__":
    main()
