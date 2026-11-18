from typing import Any

from bot.handlers.handler import Handler, HandlerStatus
from bot.messenger import Messenger


class MessageStickerHandler(Handler):
    def can_handle(self, update: dict[str, Any]) -> bool:
        message = update.get("message")
        return isinstance(message, dict) and "sticker" in message

    def handle(self, update: dict[str, Any], messenger: Messenger) -> HandlerStatus:
        message = update["message"]
        messenger.send_sticker(
            chat_id=message["chat"]["id"],
            sticker=message["sticker"]["file_id"],
        )
        return HandlerStatus.STOP
