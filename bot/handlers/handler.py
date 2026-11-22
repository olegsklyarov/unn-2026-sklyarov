from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Any

from bot.messenger import Messenger
from bot.storage import Storage


class HandlerStatus(Enum):
    CONTINUE = auto()
    STOP = auto()


class Handler(ABC):
    @abstractmethod
    def can_handle(self, update: dict[str, Any], state: str | None) -> bool:
        pass

    @abstractmethod
    def handle(
        self,
        update: dict[str, Any],
        state: str | None,
        messenger: Messenger,
        storage: Storage,
    ) -> HandlerStatus:
        pass
