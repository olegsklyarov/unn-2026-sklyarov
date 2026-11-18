from abc import ABC, abstractmethod
from enum import Enum, auto

from bot.messenger import Messenger


class HandlerStatus(Enum):
    CONTINUE = auto()
    STOP = auto()


class Handler(ABC):
    @abstractmethod
    def can_handle(self, update: dict, messenger: Messenger) -> bool:
        pass

    @abstractmethod
    def handle(self, update: dict, messenger: Messenger) -> HandlerStatus:
        pass
