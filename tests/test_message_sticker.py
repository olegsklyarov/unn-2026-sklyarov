import unittest

from fake import Fake

from bot.handlers.handler import HandlerStatus
from bot.handlers.message_sticker import MessageStickerHandler
from bot.messenger import Messenger


class MessageStickerHandlerTest(unittest.TestCase):
    def test_can_handle_message_with_sticker(self) -> None:
        update = {
            "update_id": 1,
            "message": {
                "message_id": 1,
                "chat": {"id": 42, "type": "private"},
                "sticker": {"file_id": "sticker-file-id"},
            },
        }

        self.assertTrue(MessageStickerHandler().can_handle(update))

    def test_can_handle_rejects_text_message(self) -> None:
        update = {
            "update_id": 1,
            "message": {
                "message_id": 1,
                "chat": {"id": 42, "type": "private"},
                "text": "Hello world",
            },
        }

        self.assertFalse(MessageStickerHandler().can_handle(update))

    def test_handle_echoes_sticker_and_stops(self) -> None:
        update = {
            "update_id": 1,
            "message": {
                "message_id": 1,
                "chat": {"id": 42, "type": "private"},
                "sticker": {"file_id": "sticker-file-id"},
            },
        }
        sent = []

        def fake_send_sticker(**params):
            sent.append(params)

        messenger: Messenger = Fake({"send_sticker": fake_send_sticker})

        status = MessageStickerHandler().handle(update, messenger)

        self.assertEqual(status, HandlerStatus.STOP)
        self.assertEqual(sent, [{"chat_id": 42, "sticker": "sticker-file-id"}])
