import unittest
from typing import Any

from fake import Fake

from bot.catalog import FINISHED, WAITING_FOR_PIZZA_SIZE, WAITING_FOR_PIZZA_TYPE
from bot.clock import Clock
from bot.handlers.handler import HandlerStatus
from bot.handlers.pizza_type import PizzaTypeHandler
from bot.messenger import Messenger
from bot.storage import Storage, User


def _clock(now: int) -> Clock:
    return Fake({"now": lambda: now})


def _user(state: str, order: dict[str, str] | None = None) -> User:
    return User(
        id=1,
        telegram_user_id=7,
        telegram_first_name="Ivan",
        telegram_last_name=None,
        telegram_username=None,
        created_at=1,
        updated_at=1,
        state=state,
        order={} if order is None else order,
    )


def _text(text: str) -> dict[str, Any]:
    return {
        "update_id": 1,
        "message": {
            "message_id": 1,
            "from": {"id": 7, "first_name": "Ivan"},
            "chat": {"id": 99, "type": "private"},
            "text": text,
        },
    }


def _column(message: dict[str, Any], field: str) -> list[Any]:
    keyboard = message["reply_markup"]["inline_keyboard"]
    return [row[0][field] for row in keyboard]


def _callback(data: str) -> dict[str, Any]:
    return {
        "update_id": 2,
        "callback_query": {
            "id": "cb-1",
            "from": {"id": 7, "first_name": "Ivan"},
            "message": {"message_id": 1, "chat": {"id": 99, "type": "private"}},
            "data": data,
        },
    }


class PizzaTypeHandlerTest(unittest.TestCase):
    def test_can_handle_type_and_finished_only(self) -> None:
        handler = PizzaTypeHandler(_clock(0))
        update = _text("привет")

        self.assertTrue(handler.can_handle(update, None))
        self.assertTrue(handler.can_handle(update, WAITING_FOR_PIZZA_TYPE))
        self.assertTrue(handler.can_handle(update, FINISHED))
        self.assertFalse(handler.can_handle(update, WAITING_FOR_PIZZA_SIZE))
        self.assertFalse(handler.can_handle({"update_id": 1}, WAITING_FOR_PIZZA_TYPE))

    def test_text_shows_pizza_menu(self) -> None:
        sent: list[dict[str, Any]] = []
        saved: list[dict[str, Any]] = []
        messenger: Messenger = Fake(
            {"send_message": lambda **kwargs: sent.append(kwargs)}
        )
        storage: Storage = Fake({"save_order": lambda **kwargs: saved.append(kwargs)})

        status = PizzaTypeHandler(_clock(0)).handle(
            _text("привет"), WAITING_FOR_PIZZA_TYPE, messenger, storage
        )

        self.assertEqual(status, HandlerStatus.STOP)
        self.assertEqual(saved, [])
        self.assertEqual(sent[0]["chat_id"], 99)
        self.assertEqual(sent[0]["text"], "Выберите пиццу")
        self.assertEqual(
            _column(sent[0], "callback_data"),
            ["margherita", "pepperoni", "four_cheese", "hawaiian", "napoletano"],
        )
        self.assertEqual(
            _column(sent[0], "text"),
            ["Маргарита", "Пепперони", "Четыре сыра", "Гавайская", "Неаполетано"],
        )

    def test_pizza_callback_advances_to_size(self) -> None:
        sent: list[dict[str, Any]] = []
        answered: list[dict[str, Any]] = []
        saved: list[dict[str, Any]] = []
        messenger: Messenger = Fake(
            {
                "send_message": lambda **kwargs: sent.append(kwargs),
                "answer_callback_query": lambda **kwargs: answered.append(kwargs),
            }
        )
        storage: Storage = Fake({"save_order": lambda **kwargs: saved.append(kwargs)})

        status = PizzaTypeHandler(_clock(200)).handle(
            _callback("pepperoni"), WAITING_FOR_PIZZA_TYPE, messenger, storage
        )

        self.assertEqual(status, HandlerStatus.STOP)
        self.assertEqual(
            saved,
            [
                {
                    "telegram_user_id": 7,
                    "state": WAITING_FOR_PIZZA_SIZE,
                    "order": {"type": "pepperoni"},
                    "updated_at": 200,
                }
            ],
        )
        self.assertEqual(sent[0]["text"], "Выберите размер")
        self.assertEqual(
            _column(sent[0], "callback_data"), ["small", "medium", "large"]
        )
        self.assertEqual(answered, [{"callback_query_id": "cb-1"}])

    def test_unknown_callback_repeats_pizza_menu(self) -> None:
        sent: list[dict[str, Any]] = []
        saved: list[dict[str, Any]] = []
        messenger: Messenger = Fake(
            {
                "send_message": lambda **kwargs: sent.append(kwargs),
                "answer_callback_query": lambda **_kwargs: None,
            }
        )
        storage: Storage = Fake({"save_order": lambda **kwargs: saved.append(kwargs)})

        PizzaTypeHandler(_clock(0)).handle(
            _callback("large"), WAITING_FOR_PIZZA_TYPE, messenger, storage
        )

        self.assertEqual(saved, [])
        self.assertEqual(sent[0]["text"], "Выберите пиццу")

    def test_finished_starts_new_order(self) -> None:
        sent: list[dict[str, Any]] = []
        saved: list[dict[str, Any]] = []
        messenger: Messenger = Fake(
            {
                "send_message": lambda **kwargs: sent.append(kwargs),
                "answer_callback_query": lambda **_kwargs: None,
            }
        )
        storage: Storage = Fake({"save_order": lambda **kwargs: saved.append(kwargs)})

        PizzaTypeHandler(_clock(300)).handle(
            _callback("pepperoni"), FINISHED, messenger, storage
        )

        self.assertEqual(saved[0]["state"], WAITING_FOR_PIZZA_TYPE)
        self.assertEqual(saved[0]["order"], {})
        self.assertEqual(saved[0]["updated_at"], 300)
        self.assertEqual(sent[0]["text"], "Выберите пиццу")
