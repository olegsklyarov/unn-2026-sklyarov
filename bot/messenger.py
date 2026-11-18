from abc import ABC, abstractmethod


class Messenger(ABC):
    @abstractmethod
    def get_updates(self, **params: object) -> list:
        pass

    @abstractmethod
    def send_message(self, **params: object) -> dict:
        pass
