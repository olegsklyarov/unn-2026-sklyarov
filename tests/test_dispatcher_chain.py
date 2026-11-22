import unittest
from typing import Any, override

from fake import Fake

from bot.dispatcher import Dispatcher
from bot.handlers.handler import Handler, HandlerStatus
from bot.messenger import Messenger
from bot.storage import Storage, User


class RecordingHandler(Handler):
    def __init__(
        self, name: str, can_handle: bool, status: HandlerStatus, calls: list[str]
    ) -> None:
        self._name = name
        self._can_handle = can_handle
        self._status = status
        self._calls = calls

    @override
    def can_handle(self, _update: dict[str, Any], _state: str | None) -> bool:
        return self._can_handle

    @override
    def handle(
        self,
        _update: dict[str, Any],
        _state: str | None,
        _messenger: Messenger,
        _storage: Storage,
    ) -> HandlerStatus:
        self._calls.append(self._name)
        return self._status


class StateReadingHandler(Handler):
    def __init__(self, states: list[str | None], holder: list[User | None]) -> None:
        self._states = states
        self._holder = holder

    @override
    def can_handle(self, _update: dict[str, Any], state: str | None) -> bool:
        self._states.append(state)
        return True

    @override
    def handle(
        self,
        _update: dict[str, Any],
        _state: str | None,
        _messenger: Messenger,
        _storage: Storage,
    ) -> HandlerStatus:
        self._holder[0] = User(
            id=1,
            telegram_user_id=7,
            telegram_first_name="Ivan",
            telegram_last_name=None,
            telegram_username=None,
            created_at=1,
            updated_at=1,
            state="waiting_for_pizza_size",
            order={"type": "pepperoni"},
        )
        return HandlerStatus.CONTINUE


class DispatcherChainTest(unittest.TestCase):
    def dispatch(self, first: RecordingHandler, second: RecordingHandler) -> None:
        dispatcher = Dispatcher(Fake({}), Fake({}))
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

    def test_state_is_read_once(self) -> None:
        holder: list[User | None] = [
            User(
                id=1,
                telegram_user_id=7,
                telegram_first_name="Ivan",
                telegram_last_name=None,
                telegram_username=None,
                created_at=1,
                updated_at=1,
                state="waiting_for_pizza_type",
                order={},
            )
        ]
        seen: list[str | None] = []
        reads: list[int] = []

        def get_user(telegram_user_id: int) -> User | None:
            reads.append(telegram_user_id)
            return holder[0]

        storage: Storage = Fake({"get_user": get_user})
        dispatcher = Dispatcher(Fake({}), storage)
        dispatcher.add_handlers(
            StateReadingHandler(seen, holder),
            StateReadingHandler(seen, holder),
        )
        dispatcher.dispatch(
            {
                "update_id": 1,
                "message": {
                    "from": {"id": 7, "first_name": "Ivan"},
                    "chat": {"id": 7},
                    "text": "hi",
                },
            }
        )

        self.assertEqual(reads, [7])
        self.assertEqual(seen, ["waiting_for_pizza_type", "waiting_for_pizza_type"])
