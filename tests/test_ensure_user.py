import unittest
from typing import Any

from fake import Fake

from bot.clock import Clock
from bot.handlers.ensure_user import EnsureUserHandler
from bot.handlers.handler import HandlerStatus
from bot.messenger import Messenger
from bot.storage import Storage, User


def _clock(now: int) -> Clock:
    return Fake({"now": lambda: now})


def _message(user: dict[str, Any]) -> dict[str, Any]:
    return {
        "update_id": 1,
        "message": {
            "message_id": 1,
            "from": user,
            "chat": {"id": user["id"], "type": "private"},
            "text": "Привет",
        },
    }


def _callback(user: dict[str, Any], data: str) -> dict[str, Any]:
    return {
        "update_id": 2,
        "callback_query": {
            "id": "cb-1",
            "from": user,
            "message": {"message_id": 1, "chat": {"id": user["id"], "type": "private"}},
            "data": data,
        },
    }


class EnsureUserHandlerTest(unittest.TestCase):
    def test_can_handle_message_and_callback_with_user(self) -> None:
        user = {"id": 7, "first_name": "Ivan"}
        handler = EnsureUserHandler(_clock(0))

        self.assertTrue(handler.can_handle(_message(user), None))
        self.assertTrue(handler.can_handle(_callback(user, "pepperoni"), "finished"))
        self.assertFalse(handler.can_handle({"update_id": 3}, None))
        self.assertFalse(
            handler.can_handle({"update_id": 4, "message": {"text": "hi"}}, None)
        )

    def test_creates_user_and_continues(self) -> None:
        created: list[dict[str, Any]] = []
        storage: Storage = Fake(
            {
                "get_user": lambda _telegram_user_id: None,
                "create_user": lambda **kwargs: created.append(kwargs),
            }
        )
        messenger: Messenger = Fake({})
        update = _message(
            {
                "id": 7,
                "first_name": "Ivan",
                "last_name": "Petrov",
                "username": "ivan",
            }
        )

        status = EnsureUserHandler(_clock(1_700_000_000)).handle(
            update, None, messenger, storage
        )

        self.assertEqual(status, HandlerStatus.CONTINUE)
        self.assertEqual(
            created,
            [
                {
                    "telegram_user_id": 7,
                    "telegram_first_name": "Ivan",
                    "telegram_last_name": "Petrov",
                    "telegram_username": "ivan",
                    "created_at": 1_700_000_000,
                    "updated_at": 1_700_000_000,
                    "state": "waiting_for_pizza_type",
                    "order": {},
                }
            ],
        )

    def test_creates_user_from_callback_without_optional_names(self) -> None:
        created: list[dict[str, Any]] = []
        storage: Storage = Fake(
            {
                "get_user": lambda _telegram_user_id: None,
                "create_user": lambda **kwargs: created.append(kwargs),
            }
        )

        EnsureUserHandler(_clock(50)).handle(
            _callback({"id": 8, "first_name": "Anna"}, "cola"),
            None,
            Fake({}),
            storage,
        )

        self.assertEqual(created[0]["telegram_user_id"], 8)
        self.assertEqual(created[0]["telegram_first_name"], "Anna")
        self.assertIsNone(created[0]["telegram_last_name"])
        self.assertIsNone(created[0]["telegram_username"])
        self.assertEqual(created[0]["state"], "waiting_for_pizza_type")

    def test_updates_profile_and_keeps_order(self) -> None:
        existing = User(
            id=1,
            telegram_user_id=7,
            telegram_first_name="Old",
            telegram_last_name="Name",
            telegram_username="old",
            created_at=10,
            updated_at=10,
            state="waiting_for_drink",
            order={"type": "pepperoni", "size": "large"},
        )
        updated: list[dict[str, Any]] = []
        created: list[dict[str, Any]] = []
        saved: list[dict[str, Any]] = []
        storage: Storage = Fake(
            {
                "get_user": lambda _telegram_user_id: existing,
                "update_profile": lambda **kwargs: updated.append(kwargs),
                "create_user": lambda **kwargs: created.append(kwargs),
                "save_order": lambda **kwargs: saved.append(kwargs),
            }
        )
        update = _message({"id": 7, "first_name": "Ivan", "username": "ivan"})

        status = EnsureUserHandler(_clock(80)).handle(
            update, existing.state, Fake({}), storage
        )

        self.assertEqual(status, HandlerStatus.CONTINUE)
        self.assertEqual(created, [])
        self.assertEqual(saved, [])
        self.assertEqual(
            updated,
            [
                {
                    "telegram_user_id": 7,
                    "telegram_first_name": "Ivan",
                    "telegram_last_name": None,
                    "telegram_username": "ivan",
                    "updated_at": 80,
                }
            ],
        )
