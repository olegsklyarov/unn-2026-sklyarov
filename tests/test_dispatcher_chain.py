import unittest
from typing import Any, override

from fake import Fake

from bot.dispatcher import Dispatcher
from bot.handlers.handler import Handler, HandlerStatus
from bot.messenger import Messenger


class RecordingHandler(Handler):
    def __init__(
        self, name: str, can_handle: bool, status: HandlerStatus, calls: list[str]
    ) -> None:
        self._name = name
        self._can_handle = can_handle
        self._status = status
        self._calls = calls

    @override
    def can_handle(self, update: dict[str, Any]) -> bool:
        return self._can_handle

    @override
    def handle(self, update: dict[str, Any], messenger: Messenger) -> HandlerStatus:
        self._calls.append(self._name)
        return self._status


class DispatcherChainTest(unittest.TestCase):
    def dispatch(self, first: RecordingHandler, second: RecordingHandler) -> None:
        dispatcher = Dispatcher(Fake({}))
        dispatcher.add_handlers(first, second)
        dispatcher.dispatch({"update_id": 1})

    def test_stop_breaks_chain(self) -> None:
        calls: list[str] = []
        self.dispatch(
            RecordingHandler(
                name="first",
                can_handle=True,
                status=HandlerStatus.STOP,
                calls=calls,
            ),
            RecordingHandler(
                name="second",
                can_handle=True,
                status=HandlerStatus.STOP,
                calls=calls,
            ),
        )

        self.assertEqual(calls, ["first"])

    def test_continue_passes_to_next_handler(self) -> None:
        calls: list[str] = []
        self.dispatch(
            RecordingHandler(
                name="first",
                can_handle=True,
                status=HandlerStatus.CONTINUE,
                calls=calls,
            ),
            RecordingHandler(
                name="second",
                can_handle=True,
                status=HandlerStatus.STOP,
                calls=calls,
            ),
        )

        self.assertEqual(calls, ["first", "second"])

    def test_handler_that_cannot_handle_is_skipped(self) -> None:
        calls: list[str] = []
        self.dispatch(
            RecordingHandler(
                name="first",
                can_handle=False,
                status=HandlerStatus.STOP,
                calls=calls,
            ),
            RecordingHandler(
                name="second",
                can_handle=True,
                status=HandlerStatus.STOP,
                calls=calls,
            ),
        )

        self.assertEqual(calls, ["second"])
