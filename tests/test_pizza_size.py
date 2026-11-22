import unittest
from typing import Any

from fake import Fake

from bot.catalog import (
    WAITING_FOR_DRINK,
    WAITING_FOR_PIZZA_SIZE,
    WAITING_FOR_PIZZA_TYPE,
)
from bot.clock import Clock
from bot.handlers.handler import HandlerStatus
from bot.handlers.pizza_size import PizzaSizeHandler
from bot.messenger import Messenger
from bot.storage import Storage, User


def _clock(now: int) -> Clock:
    return Fake({"now": lambda: now})


def _user() -> User:
    return User(
        id=1,
        telegram_user_id=7,
        telegram_first_name="Ivan",
        telegram_last_name=None,
        telegram_username=None,
        created_at=1,
        updated_at=1,
        state=WAITING_FOR_PIZZA_SIZE,
        order={"type": "pepperoni"},
    )


def _text() -> dict[str, Any]:
    return {
        "update_id": 1,
        "message": {
            "message_id": 1,
            "from": {"id": 7, "first_name": "Ivan"},
            "chat": {"id": 99, "type": "private"},
            "text": "средняя",
        },
    }


def _column(message: dict[str, Any], field: str) -> list[Any]:
    keyboard = message["reply_markup"]["inline_keyboard"]
    return [row[0][field] for row in keyboard]


def _callback(data: str) -> dict[str, Any]:
    return {
        "update_id": 2,
        "callback_query": {
            "id": "cb-2",
            "from": {"id": 7, "first_name": "Ivan"},
            "message": {"message_id": 1, "chat": {"id": 99, "type": "private"}},
            "data": data,
        },
    }


class PizzaSizeHandlerTest(unittest.TestCase):
    def test_can_handle_only_size_state(self) -> None:
        handler = PizzaSizeHandler(_clock(0))

        self.assertTrue(handler.can_handle(_text(), WAITING_FOR_PIZZA_SIZE))
        self.assertFalse(handler.can_handle(_text(), WAITING_FOR_PIZZA_TYPE))
        self.assertFalse(handler.can_handle({"update_id": 1}, WAITING_FOR_PIZZA_SIZE))

    def test_size_callback_keeps_pizza_and_asks_for_drink(self) -> None:
        sent: list[dict[str, Any]] = []
        answered: list[dict[str, Any]] = []
        deleted: list[dict[str, Any]] = []
        saved: list[dict[str, Any]] = []
        messenger: Messenger = Fake(
            {
                "send_message": lambda **kwargs: sent.append(kwargs),
                "answer_callback_query": lambda **kwargs: answered.append(kwargs),
                "delete_message": lambda **kwargs: deleted.append(kwargs),
            }
        )
        storage: Storage = Fake(
            {
                "get_user": lambda _telegram_user_id: _user(),
                "save_order": lambda **kwargs: saved.append(kwargs),
            }
        )

        status = PizzaSizeHandler(_clock(400)).handle(
            _callback("large"), WAITING_FOR_PIZZA_SIZE, messenger, storage
        )

        self.assertEqual(status, HandlerStatus.STOP)
        self.assertEqual(
            saved,
            [
                {
                    "telegram_user_id": 7,
                    "state": WAITING_FOR_DRINK,
                    "order": {"type": "pepperoni", "size": "large"},
                    "updated_at": 400,
                }
            ],
        )
        self.assertEqual(sent[0]["chat_id"], 99)
        self.assertEqual(sent[0]["text"], "Выберите напиток")
        self.assertEqual(
            _column(sent[0], "callback_data"),
            ["juice", "mors", "tea", "cola", "none"],
        )
        self.assertEqual(
            _column(sent[0], "text"),
            ["Сок", "Морс", "Чай", "Кола", "Без напитка"],
        )
        self.assertEqual(answered, [{"callback_query_id": "cb-2"}])
        self.assertEqual(deleted, [{"chat_id": 99, "message_id": 1}])

    def test_text_repeats_size_menu(self) -> None:
        sent: list[dict[str, Any]] = []
        saved: list[dict[str, Any]] = []
        messenger: Messenger = Fake(
            {"send_message": lambda **kwargs: sent.append(kwargs)}
        )
        storage: Storage = Fake(
            {
                "get_user": lambda _telegram_user_id: _user(),
                "save_order": lambda **kwargs: saved.append(kwargs),
            }
        )

        PizzaSizeHandler(_clock(0)).handle(
            _text(), WAITING_FOR_PIZZA_SIZE, messenger, storage
        )

        self.assertEqual(saved, [])
        self.assertEqual(sent[0]["text"], "Выберите размер")
        self.assertEqual(
            _column(sent[0], "text"),
            ["Маленькая (25 см)", "Средняя (33 см)", "Большая (40 см)"],
        )
