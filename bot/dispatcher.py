from typing import Any

from bot.handlers.handler import Handler, HandlerStatus
from bot.messenger import Messenger


class Dispatcher:
    def __init__(self, messenger: Messenger) -> None:
        self._messenger = messenger
        self._handlers: list[Handler] = []

    def add_handlers(self, *handlers: Handler) -> None:
        self._handlers.extend(handlers)

    def dispatch(self, update: dict[str, Any]) -> None:
        for handler in self._handlers:
            if not handler.can_handle(update):
                continue
            if handler.handle(update, self._messenger) == HandlerStatus.STOP:
                break
