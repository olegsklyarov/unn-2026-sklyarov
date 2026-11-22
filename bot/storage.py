from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class User:
    id: int
    telegram_user_id: int
    telegram_first_name: str
    telegram_last_name: str | None
    telegram_username: str | None
    created_at: int
    updated_at: int
    state: str
    order: dict[str, str]


class Storage(ABC):
    @abstractmethod
    def add_update(self, update: dict[str, Any], created_at: int) -> None:
        pass

    @abstractmethod
    def get_user(self, telegram_user_id: int) -> User | None:
        pass

    @abstractmethod
    def create_user(
        self,
        telegram_user_id: int,
        telegram_first_name: str,
        telegram_last_name: str | None,
        telegram_username: str | None,
        created_at: int,
        updated_at: int,
        state: str,
        order: dict[str, str],
    ) -> User:
        pass

    @abstractmethod
    def update_profile(
        self,
        telegram_user_id: int,
        telegram_first_name: str,
        telegram_last_name: str | None,
        telegram_username: str | None,
        updated_at: int,
    ) -> None:
        pass

    @abstractmethod
    def save_order(
        self,
        telegram_user_id: int,
        state: str,
        order: dict[str, str],
        updated_at: int,
    ) -> None:
        pass
