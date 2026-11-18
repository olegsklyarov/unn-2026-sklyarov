import unittest
from typing import Any

from fake import Fake

from bot.dispatcher import Dispatcher
from bot.handlers.message_sticker import MessageStickerHandler
from bot.handlers.message_text import MessageTextHandler
from bot.messenger import Messenger


class DispatcherRoutingTest(unittest.TestCase):
    def setUp(self) -> None:
        self.sent_messages: list[dict[str, Any]] = []
        self.sent_stickers: list[dict[str, Any]] = []

        def fake_send_message(**params):
            self.sent_messages.append(params)

        def fake_send_sticker(**params):
            self.sent_stickers.append(params)

        messenger: Messenger = Fake(
            {"send_message": fake_send_message, "send_sticker": fake_send_sticker}
        )
        self.dispatcher = Dispatcher(messenger)
        self.dispatcher.add_handlers(MessageTextHandler(), MessageStickerHandler())

    def test_text_goes_to_text_handler(self) -> None:
        update = {"update_id": 1, "message": {"chat": {"id": 42}, "text": "Hello"}}

        self.dispatcher.dispatch(update)

        self.assertEqual(self.sent_messages, [{"chat_id": 42, "text": "Hello"}])
        self.assertEqual(self.sent_stickers, [])

    def test_sticker_goes_to_sticker_handler(self) -> None:
        update = {
            "update_id": 1,
            "message": {"chat": {"id": 42}, "sticker": {"file_id": "sticker-file-id"}},
        }

        self.dispatcher.dispatch(update)

        self.assertEqual(self.sent_messages, [])
        self.assertEqual(
            self.sent_stickers, [{"chat_id": 42, "sticker": "sticker-file-id"}]
        )

    def test_unsupported_update_is_ignored(self) -> None:
        update = {"update_id": 1, "message": {"chat": {"id": 42}, "photo": []}}

        self.dispatcher.dispatch(update)

        self.assertEqual(self.sent_messages, [])
        self.assertEqual(self.sent_stickers, [])
