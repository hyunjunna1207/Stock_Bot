"""kakao_sender.py — 카카오톡 나에게 보내기"""

import json
import os
import urllib.parse
import urllib.request


KAKAO_TOKEN_URL   = "https://kauth.kakao.com/oauth/token"
KAKAO_MESSAGE_URL = "https://kapi.kakao.com/v2/api/talk/memo/default/send"


def _get_access_token(rest_api_key: str, refresh_token: str, client_secret: str) -> str:
    data = urllib.parse.urlencode({
        "grant_type":    "refresh_token",
        "client_id":     rest_api_key,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
    }).encode()

    req = urllib.request.Request(KAKAO_TOKEN_URL, data=data, method="POST")
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())

    if "refresh_token" in result:
        new_rt = result["refresh_token"]
        print(f"[kakao] ⚠️  Refresh Token이 갱신되었습니다.")
        print(f"[kakao] GitHub Secret 'KAKAO_REFRESH_TOKEN' 값을 아래로 교체하세요:")
        print(f"        {new_rt}")

    return result["access_token"]


def send_message(text: str) -> bool:
    rest_api_key  = os.environ["KAKAO_REST_API_KEY"]
    refresh_token = os.environ["KAKAO_REFRESH_TOKEN"]
    client_secret = os.environ["KAKAO_CLIENT_SECRET"]

    try:
        access_token = _get_access_token(rest_api_key, refresh_token, client_secret)
    except Exception as e:
        print(f"[kakao] 토큰 발급 실패: {e}")
        return False

    template = {
        "object_type": "text",
        "text": text[:2000],
        "link": {
            "web_url":        "https://finance.naver.com",
            "mobile_web_url": "https://finance.naver.com",
        },
    }

    data = urllib.parse.urlencode({
        "template_object": json.dumps(template, ensure_ascii=False),
    }).encode()

    req = urllib.request.Request(
        KAKAO_MESSAGE_URL,
        data=data,
        headers={"Authorization": f"Bearer {access_token}"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
        if result.get("result_code") == 0:
            print("[kakao] 메시지 전송 성공 ✅")
            return True
        else:
            print(f"[kakao] 전송 실패: {result}")
            return False
    except Exception as e:
        print(f"[kakao] 전송 오류: {e}")
        return False
