import unittest

from fake import Fake

from bot.handlers.handler import HandlerStatus
from bot.handlers.message_text import MessageTextHandler
from bot.messenger import Messenger


class MessageTextHandlerTest(unittest.TestCase):
    def test_can_handle_message_with_text(self) -> None:
        update = {
            "update_id": 1,
            "message": {
                "message_id": 1,
                "chat": {"id": 42, "type": "private"},
                "text": "Hello world",
            },
        }

        self.assertTrue(MessageTextHandler().can_handle(update))

    def test_can_handle_rejects_update_without_text(self) -> None:
        update = {
            "update_id": 1,
            "message": {
                "message_id": 1,
                "chat": {"id": 42, "type": "private"},
            },
        }

        self.assertFalse(MessageTextHandler().can_handle(update))

    def test_handle_echoes_text_and_stops(self) -> None:
        update = {
            "update_id": 1,
            "message": {
                "message_id": 1,
                "chat": {"id": 42, "type": "private"},
                "text": "Hello world",
            },
        }
        sent = []

        def fake_send_message(**params):
            sent.append(params)

        messenger: Messenger = Fake({"send_message": fake_send_message})

        status = MessageTextHandler().handle(update, messenger)

        self.assertEqual(status, HandlerStatus.STOP)
        self.assertEqual(sent, [{"chat_id": 42, "text": "Hello world"}])
