from typing import Any


def telegram_user(update: dict[str, Any]) -> dict[str, Any] | None:
    message = update.get("message")
    if isinstance(message, dict):
        user = message.get("from")
        if _is_user(user):
            return user
    callback = update.get("callback_query")
    if isinstance(callback, dict):
        user = callback.get("from")
        if _is_user(user):
            return user
    return None


def telegram_user_id(update: dict[str, Any]) -> int | None:
    user = telegram_user(update)
    if user is None:
        return None
    user_id = user.get("id")
    if isinstance(user_id, int):
        return user_id
    return None


def chat_id(update: dict[str, Any]) -> int | None:
    message = update.get("message")
    if isinstance(message, dict):
        found = _chat_id(message)
        if found is not None:
            return found
    callback = update.get("callback_query")
    if isinstance(callback, dict):
        origin = callback.get("message")
        if isinstance(origin, dict):
            return _chat_id(origin)
    return None


def callback_message_id(update: dict[str, Any]) -> int | None:
    callback = update.get("callback_query")
    if not isinstance(callback, dict):
        return None
    message = callback.get("message")
    if not isinstance(message, dict):
        return None
    value = message.get("message_id")
    if isinstance(value, int):
        return value
    return None


def callback_query_id(update: dict[str, Any]) -> str | None:
    callback = update.get("callback_query")
    if not isinstance(callback, dict):
        return None
    value = callback.get("id")
    if isinstance(value, str):
        return value
    return None


def callback_data(update: dict[str, Any]) -> str | None:
    callback = update.get("callback_query")
    if not isinstance(callback, dict):
        return None
    value = callback.get("data")
    if isinstance(value, str):
        return value
    return None


def _chat_id(message: dict[str, Any]) -> int | None:
    chat = message.get("chat")
    if not isinstance(chat, dict):
        return None
    value = chat.get("id")
    if isinstance(value, int):
        return value
    return None


def _is_user(user: object) -> bool:
    return isinstance(user, dict) and isinstance(user.get("id"), int)
