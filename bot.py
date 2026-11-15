import json
import os
import urllib.parse
import urllib.request

TOKEN = os.environ["TELEGRAM_TOKEN"]
BASE = os.environ["TELEGRAM_BASE_URL"].rstrip("/")


def api_request(method, **params):
    url = f"{BASE}/bot{TOKEN}/{method}"

    req = urllib.request.Request(
        url,
        data=json.dumps(params).encode(),
        headers={'Content-Type': 'application/json'},
        method='POST',
    )

    with urllib.request.urlopen(req) as r:
        payload = json.loads(r.read())
    assert payload["ok"]
    return payload


def get_updates(**params):
    return api_request("getUpdates", **params)["result"]


def send_message(**params):
    return api_request("sendMessage", **params)


def main():
    next_update_id = 0
    try:
        while True:
            for update in get_updates(
                offset=next_update_id,
                timeout=30,
                limit=10,
                allowed_updates=["message"],
            ):
                next_update_id = max(next_update_id, update["update_id"] + 1)
                if "text" in update["message"]:
                    send_message(
                        chat_id=update["message"]["chat"]["id"],
                        text=update["message"]["text"],
                    )
                    print(".", end="", flush=True)
    except KeyboardInterrupt:
        print("\nBye!")


if __name__ == "__main__":
    main()
