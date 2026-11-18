from bot.handlers.handler import Handler, HandlerStatus
from bot.messenger import Messenger


class MessageTextHandler(Handler):
    def can_handle(self, update: dict, messenger: Messenger) -> bool:
        message = update.get("message")
        return isinstance(message, dict) and "text" in message

    def handle(self, update: dict, messenger: Messenger) -> HandlerStatus:
        message = update["message"]
        messenger.send_message(
            chat_id=message["chat"]["id"],
            text=message["text"],
        )
        return HandlerStatus.STOP
