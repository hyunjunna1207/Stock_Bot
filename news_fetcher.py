"""news_fetcher.py — 구글 뉴스 RSS로 종목 뉴스 수집"""

import re
import urllib.request
import xml.etree.ElementTree as ET
from urllib.parse import quote

MAX_NEWS = 3


def _decode_google_url(raw_url: str) -> str:
    match = re.search(r"url=([^&]+)", raw_url)
    if match:
        from urllib.parse import unquote
        return unquote(match.group(1))
    return raw_url


def fetch_news(query: str) -> list[dict]:
    encoded_query = quote(query)
    url = (
        f"https://news.google.com/rss/search"
        f"?q={encoded_query}&hl=ko&gl=KR&ceid=KR:ko"
    )

    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (stock-bot/1.0)"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read()

        root = ET.fromstring(content)
        items = root.findall(".//item")

        results = []
        for item in items[:MAX_NEWS]:
            title_el = item.find("title")
            link_el  = item.find("link")
            if title_el is None or link_el is None:
                continue
            title = title_el.text or ""
            link  = _decode_google_url(link_el.text or "")
            results.append({"title": title.strip(), "link": link.strip()})

        return results

    except Exception as e:
        print(f"[news_fetcher] '{query}' 뉴스 오류: {e}")
        return []
