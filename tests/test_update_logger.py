import unittest
from typing import Any

from fake import Fake

from bot.clock import Clock
from bot.handlers.handler import HandlerStatus
from bot.handlers.update_logger import UpdateLoggerHandler
from bot.messenger import Messenger
from bot.storage import Storage


def _clock(now: int) -> Clock:
    return Fake({"now": lambda: now})


class UpdateLoggerHandlerTest(unittest.TestCase):
    def test_can_handle_any_update(self) -> None:
        handler = UpdateLoggerHandler(_clock(0))

        self.assertTrue(handler.can_handle({"update_id": 1}, None))
        self.assertTrue(
            handler.can_handle({"update_id": 2, "message": {"text": "hi"}}, "finished")
        )

    def test_handle_stores_update_and_continues(self) -> None:
        update = {"update_id": 5, "message": {"text": "Привет"}}
        stored: list[tuple[dict[str, Any], int]] = []

        def add_update(update: dict[str, Any], created_at: int) -> None:
            stored.append((update, created_at))

        storage: Storage = Fake({"add_update": add_update})
        messenger: Messenger = Fake({})

        status = UpdateLoggerHandler(_clock(1_700_000_000)).handle(
            update, None, messenger, storage
        )

        self.assertEqual(status, HandlerStatus.CONTINUE)
        self.assertEqual(stored, [(update, 1_700_000_000)])
