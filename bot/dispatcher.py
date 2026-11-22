from typing import Any

from bot.handlers.handler import Handler, HandlerStatus
from bot.messenger import Messenger
from bot.storage import Storage
from bot.telegram_update import telegram_user_id


class Dispatcher:
    def __init__(self, messenger: Messenger, storage: Storage) -> None:
        self._messenger = messenger
        self._storage = storage
        self._handlers: list[Handler] = []

    def add_handlers(self, *handlers: Handler) -> None:
        self._handlers.extend(handlers)

    def dispatch(self, update: dict[str, Any]) -> None:
        state = self._user_state(update)
        for handler in self._handlers:
            if not handler.can_handle(update, state):
                continue
            status = handler.handle(update, state, self._messenger, self._storage)
            if status == HandlerStatus.STOP:
                break

    def _user_state(self, update: dict[str, Any]) -> str | None:
        user_id = telegram_user_id(update)
        if user_id is None:
            return None
        user = self._storage.get_user(user_id)
        if user is None:
            return None
        return user.state
