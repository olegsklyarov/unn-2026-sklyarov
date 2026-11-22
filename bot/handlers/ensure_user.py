from typing import Any

from bot.catalog import WAITING_FOR_PIZZA_TYPE
from bot.clock import Clock
from bot.handlers.handler import Handler, HandlerStatus
from bot.messenger import Messenger
from bot.storage import Storage
from bot.telegram_update import telegram_user


class EnsureUserHandler(Handler):
    def __init__(self, clock: Clock) -> None:
        self._clock = clock

    def can_handle(self, update: dict[str, Any], _state: str | None) -> bool:
        return telegram_user(update) is not None

    def handle(
        self,
        update: dict[str, Any],
        _state: str | None,
        _messenger: Messenger,
        storage: Storage,
    ) -> HandlerStatus:
        user_id, first_name, last_name, username = _profile(update)
        now = self._clock.now()
        if storage.get_user(user_id) is None:
            storage.create_user(
                telegram_user_id=user_id,
                telegram_first_name=first_name,
                telegram_last_name=last_name,
                telegram_username=username,
                created_at=now,
                updated_at=now,
                state=WAITING_FOR_PIZZA_TYPE,
                order={},
            )
        else:
            storage.update_profile(
                telegram_user_id=user_id,
                telegram_first_name=first_name,
                telegram_last_name=last_name,
                telegram_username=username,
                updated_at=now,
            )
        return HandlerStatus.CONTINUE


def _profile(update: dict[str, Any]) -> tuple[int, str, str | None, str | None]:
    user = telegram_user(update)
    if user is None:
        raise RuntimeError("update has no telegram user")
    user_id = user.get("id")
    if not isinstance(user_id, int):
        raise RuntimeError("update has no telegram user id")
    first_name = user.get("first_name")
    return (
        user_id,
        first_name if isinstance(first_name, str) else "",
        _optional_str(user, "last_name"),
        _optional_str(user, "username"),
    )


def _optional_str(user: dict[str, Any], key: str) -> str | None:
    value = user.get(key)
    if isinstance(value, str):
        return value
    return None
