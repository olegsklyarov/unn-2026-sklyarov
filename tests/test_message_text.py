from mock import Mock

from bot.handlers.handler import HandlerStatus
from bot.handlers.message_text import MessageTextHandler
from bot.messenger import Messenger


def test_can_handle_message_with_text():
    update = {
        "update_id": 1,
        "message": {
            "message_id": 1,
            "chat": {"id": 42, "type": "private"},
            "text": "Hello world",
        },
    }
    messenger: Messenger = Mock({})
    handler = MessageTextHandler()

    assert handler.can_handle(update, messenger) is True


def test_can_handle_rejects_update_without_text():
    update = {
        "update_id": 1,
        "message": {
            "message_id": 1,
            "chat": {"id": 42, "type": "private"},
        },
    }
    messenger: Messenger = Mock({})
    handler = MessageTextHandler()

    assert handler.can_handle(update, messenger) is False


def test_handle_echoes_text_and_stops():
    update = {
        "update_id": 1,
        "message": {
            "message_id": 1,
            "chat": {"id": 42, "type": "private"},
            "text": "Hello world",
        },
    }
    sent = []

    def mock_send_message(**params):
        sent.append(params)

    messenger: Messenger = Mock({"send_message": mock_send_message})
    handler = MessageTextHandler()

    status = handler.handle(update, messenger)

    assert status == HandlerStatus.STOP
    assert sent == [{"chat_id": 42, "text": "Hello world"}]


if __name__ == "__main__":
    test_can_handle_message_with_text()
    test_can_handle_rejects_update_without_text()
    test_handle_echoes_text_and_stops()
