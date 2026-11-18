import json
import urllib.request
from typing import Any

from bot.messenger import Messenger

# Должен быть больше timeout, который long polling передаёт в getUpdates.
REQUEST_TIMEOUT = 40


class TelegramMessenger(Messenger):
    def __init__(self, token: str, base_url: str) -> None:
        self._url = f"{base_url.rstrip('/')}/bot{token}"

    def get_updates(self, **params: object) -> list[dict[str, Any]]:
        updates: list[dict[str, Any]] = self._request("getUpdates", params)["result"]
        return updates

    def send_message(self, **params: object) -> dict[str, Any]:
        return self._request("sendMessage", params)

    def send_sticker(self, **params: object) -> dict[str, Any]:
        return self._request("sendSticker", params)

    def _request(self, method: str, params: dict[str, object]) -> dict[str, Any]:
        request = urllib.request.Request(
            f"{self._url}/{method}",
            data=json.dumps(params).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT) as response:
            payload: dict[str, Any] = json.loads(response.read())

        if not payload["ok"]:
            raise RuntimeError(payload.get("description"))
        return payload
