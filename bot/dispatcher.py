from bot.handlers.handler import Handler, HandlerStatus
from bot.messenger import Messenger


class Dispatcher:
    def __init__(self, messenger: Messenger) -> None:
        self._messenger = messenger
        self._handlers: list[Handler] = []

    def add_handlers(self, *handlers: Handler) -> None:
        for handler in handlers:
            self._handlers.append(handler)

    def dispatch(self, update: dict) -> None:
        for handler in self._handlers:
            if handler.can_handle(update, self._messenger) and (
                handler.handle(update, self._messenger) == HandlerStatus.STOP
            ):
                break
