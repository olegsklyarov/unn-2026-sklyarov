import time
from abc import ABC, abstractmethod


class Clock(ABC):
    @abstractmethod
    def now(self) -> int:
        pass


class SystemClock(Clock):
    def now(self) -> int:
        return int(time.time())
