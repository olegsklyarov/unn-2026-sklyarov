from typing import Any

from bot.clock import Clock
from bot.handlers.handler import Handler, HandlerStatus
from bot.messenger import Messenger
from bot.storage import Storage


class UpdateLoggerHandler(Handler):
    def __init__(self, clock: Clock) -> None:
        self._clock = clock

    def can_handle(self, _update: dict[str, Any], _state: str | None) -> bool:
        return True

    def handle(
        self,
        update: dict[str, Any],
        _state: str | None,
        _messenger: Messenger,
        storage: Storage,
    ) -> HandlerStatus:
        storage.add_update(update, self._clock.now())
        return HandlerStatus.CONTINUE
