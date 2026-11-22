import unittest
from typing import Any

from fake import Fake

from bot.catalog import FINISHED, WAITING_FOR_DRINK, WAITING_FOR_PIZZA_SIZE
from bot.clock import Clock
from bot.handlers.handler import HandlerStatus
from bot.handlers.pizza_drink import PizzaDrinkHandler
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
        state=WAITING_FOR_DRINK,
        order={"type": "pepperoni", "size": "large"},
    )


def _text() -> dict[str, Any]:
    return {
        "update_id": 1,
        "message": {
            "message_id": 1,
            "from": {"id": 7, "first_name": "Ivan"},
            "chat": {"id": 99, "type": "private"},
            "text": "кола",
        },
    }


def _callback(data: str) -> dict[str, Any]:
    return {
        "update_id": 2,
        "callback_query": {
            "id": "cb-3",
            "from": {"id": 7, "first_name": "Ivan"},
            "message": {"message_id": 1, "chat": {"id": 99, "type": "private"}},
            "data": data,
        },
    }


class PizzaDrinkHandlerTest(unittest.TestCase):
    def test_can_handle_only_drink_state(self) -> None:
        handler = PizzaDrinkHandler(_clock(0))

        self.assertTrue(handler.can_handle(_text(), WAITING_FOR_DRINK))
        self.assertFalse(handler.can_handle(_text(), WAITING_FOR_PIZZA_SIZE))
        self.assertFalse(handler.can_handle({"update_id": 1}, WAITING_FOR_DRINK))

    def test_drink_callback_finishes_order(self) -> None:
        sent: list[dict[str, Any]] = []
        answered: list[dict[str, Any]] = []
        saved: list[dict[str, Any]] = []
        messenger: Messenger = Fake(
            {
                "send_message": lambda **kwargs: sent.append(kwargs),
                "answer_callback_query": lambda **kwargs: answered.append(kwargs),
            }
        )
        storage: Storage = Fake(
            {
                "get_user": lambda _telegram_user_id: _user(),
                "save_order": lambda **kwargs: saved.append(kwargs),
            }
        )

        status = PizzaDrinkHandler(_clock(500)).handle(
            _callback("cola"), WAITING_FOR_DRINK, messenger, storage
        )

        self.assertEqual(status, HandlerStatus.STOP)
        self.assertEqual(
            saved,
            [
                {
                    "telegram_user_id": 7,
                    "state": FINISHED,
                    "order": {"type": "pepperoni", "size": "large", "drink": "cola"},
                    "updated_at": 500,
                }
            ],
        )
        self.assertEqual(
            sent[0]["text"],
            "Заказ оформлен:\nПицца: Пепперони\nРазмер: Большая (40 см)\nНапиток: Кола",
        )
        self.assertNotIn("reply_markup", sent[0])
        self.assertEqual(answered, [{"callback_query_id": "cb-3"}])

    def test_no_drink_is_stored(self) -> None:
        sent: list[dict[str, Any]] = []
        saved: list[dict[str, Any]] = []
        messenger: Messenger = Fake(
            {
                "send_message": lambda **kwargs: sent.append(kwargs),
                "answer_callback_query": lambda **_kwargs: None,
            }
        )
        storage: Storage = Fake(
            {
                "get_user": lambda _telegram_user_id: _user(),
                "save_order": lambda **kwargs: saved.append(kwargs),
            }
        )

        PizzaDrinkHandler(_clock(500)).handle(
            _callback("none"), WAITING_FOR_DRINK, messenger, storage
        )

        self.assertEqual(saved[0]["order"]["drink"], "none")
        self.assertIn("Без напитка", sent[0]["text"])

    def test_text_repeats_drink_menu(self) -> None:
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

        PizzaDrinkHandler(_clock(0)).handle(
            _text(), WAITING_FOR_DRINK, messenger, storage
        )

        self.assertEqual(saved, [])
        self.assertEqual(sent[0]["text"], "Выберите напиток")
