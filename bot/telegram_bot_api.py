import json
import os
import urllib.request


def api_request(method: str, **params: object) -> dict:
    token = os.environ["TELEGRAM_TOKEN"]
    base = os.environ["TELEGRAM_BASE_URL"].rstrip("/")
    url = f"{base}/bot{token}/{method}"

    req = urllib.request.Request(
        url,
        data=json.dumps(params).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(req) as r:
        payload = json.loads(r.read())
    assert payload["ok"]
    return payload


def get_updates(**params: object) -> list:
    return api_request("getUpdates", **params)["result"]


def send_message(**params: object) -> dict:
    return api_request("sendMessage", **params)
