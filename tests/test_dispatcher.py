import os
import sqlite3
import tempfile
import unittest
from pathlib import Path
from typing import Any

from fake import Fake

from bot.catalog import (
    FINISHED,
    WAITING_FOR_DRINK,
    WAITING_FOR_PIZZA_SIZE,
    WAITING_FOR_PIZZA_TYPE,
)
from bot.clock import Clock
from bot.dispatcher import Dispatcher
from bot.handlers import get_handlers
from bot.handlers.ensure_user import EnsureUserHandler
from bot.handlers.pizza_drink import PizzaDrinkHandler
from bot.handlers.pizza_size import PizzaSizeHandler
from bot.handlers.pizza_type import PizzaTypeHandler
from bot.handlers.update_logger import UpdateLoggerHandler
from bot.messenger import Messenger
from bot.sqlite_storage import SqliteStorage

MIGRATIONS = str(Path(__file__).resolve().parents[1] / "migrations")
USER = {"id": 7, "first_name": "Ivan", "last_name": "Petrov", "username": "ivan"}


def _text(update_id: int, text: str) -> dict[str, Any]:
    return {
        "update_id": update_id,
        "message": {
            "message_id": update_id,
            "from": USER,
            "chat": {"id": 7, "type": "private"},
            "text": text,
        },
    }


def _callback(update_id: int, data: str) -> dict[str, Any]:
    return {
        "update_id": update_id,
        "callback_query": {
            "id": f"cb-{update_id}",
            "from": USER,
            "message": {"message_id": 1, "chat": {"id": 7, "type": "private"}},
            "data": data,
        },
    }


class IncrementalClock(Clock):
    def __init__(self) -> None:
        self._now = 1_000

    def now(self) -> int:
        self._now += 10
        return self._now


class DispatcherOrderTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self._tmp.name, "database.sqlite")
        self.sent: list[dict[str, Any]] = []
        self.answered: list[dict[str, Any]] = []
        self.deleted: list[dict[str, Any]] = []
        messenger: Messenger = Fake(
            {
                "send_message": lambda **kwargs: self.sent.append(kwargs),
                "answer_callback_query": lambda **kwargs: self.answered.append(kwargs),
                "delete_message": lambda **kwargs: self.deleted.append(kwargs),
            }
        )
        self.storage = SqliteStorage(self.path, MIGRATIONS)
        self.dispatcher = Dispatcher(messenger, self.storage)
        self.dispatcher.add_handlers(*get_handlers(IncrementalClock()))

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_handlers_are_registered_in_order(self) -> None:
        handlers = get_handlers(IncrementalClock())

        self.assertEqual(len(handlers), 5)
        self.assertIsInstance(handlers[0], UpdateLoggerHandler)
        self.assertIsInstance(handlers[1], EnsureUserHandler)
        self.assertIsInstance(handlers[2], PizzaTypeHandler)
        self.assertIsInstance(handlers[3], PizzaSizeHandler)
        self.assertIsInstance(handlers[4], PizzaDrinkHandler)

    def test_order_flow(self) -> None:
        self.dispatcher.dispatch(_text(1, "привет"))
        created = self.storage.get_user(7)
        self.dispatcher.dispatch(_callback(2, "pepperoni"))
        sized = self.storage.get_user(7)
        self.dispatcher.dispatch(_callback(3, "large"))
        drinking = self.storage.get_user(7)
        self.dispatcher.dispatch(_callback(4, "cola"))
        finished = self.storage.get_user(7)
        self.dispatcher.dispatch(_text(5, "ещё"))
        restarted = self.storage.get_user(7)

        assert created is not None
        assert sized is not None
        assert drinking is not None
        assert finished is not None
        assert restarted is not None
        self.assertEqual(created.state, WAITING_FOR_PIZZA_TYPE)
        self.assertEqual(created.order, {})
        self.assertEqual(created.telegram_first_name, "Ivan")
        self.assertEqual(created.telegram_last_name, "Petrov")
        self.assertEqual(created.telegram_username, "ivan")
        self.assertEqual(sized.state, WAITING_FOR_PIZZA_SIZE)
        self.assertEqual(sized.order, {"type": "pepperoni"})
        self.assertEqual(drinking.state, WAITING_FOR_DRINK)
        self.assertEqual(drinking.order, {"type": "pepperoni", "size": "large"})
        self.assertEqual(finished.state, FINISHED)
        self.assertEqual(
            finished.order, {"type": "pepperoni", "size": "large", "drink": "cola"}
        )
        self.assertEqual(restarted.state, WAITING_FOR_PIZZA_TYPE)
        self.assertEqual(restarted.order, {})
        self.assertEqual(restarted.created_at, created.created_at)
        self.assertGreater(restarted.updated_at, created.updated_at)
        self.assertEqual(
            [message["text"] for message in self.sent],
            [
                "Выберите пиццу",
                "Выберите размер",
                "Выберите напиток",
                "Заказ оформлен:\n"
                "Пицца: Пепперони\n"
                "Размер: Большая (40 см)\n"
                "Напиток: Кола",
                "Выберите пиццу",
            ],
        )
        self.assertEqual(
            self.answered,
            [
                {"callback_query_id": "cb-2"},
                {"callback_query_id": "cb-3"},
                {"callback_query_id": "cb-4"},
            ],
        )
        self.assertEqual(
            self.deleted,
            [
                {"chat_id": 7, "message_id": 1},
                {"chat_id": 7, "message_id": 1},
                {"chat_id": 7, "message_id": 1},
            ],
        )
        with sqlite3.connect(self.path) as connection:
            logged = connection.execute(
                "SELECT COUNT(*) FROM telegram_updates"
            ).fetchone()
        assert logged is not None
        self.assertEqual(logged[0], 5)

    def test_start_resets_after_pepperoni(self) -> None:
        self.dispatcher.dispatch(_text(1, "/start"))
        self.dispatcher.dispatch(_callback(2, "pepperoni"))
        self.dispatcher.dispatch(_text(3, "/start"))
        user = self.storage.get_user(7)

        assert user is not None
        self.assertEqual(user.state, WAITING_FOR_PIZZA_TYPE)
        self.assertEqual(user.order, {})
        self.assertEqual(
            [message["text"] for message in self.sent],
            ["Выберите пиццу", "Выберите размер", "Выберите пиццу"],
        )
