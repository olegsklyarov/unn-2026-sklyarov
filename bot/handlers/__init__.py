from bot.handlers.handler import Handler
from bot.handlers.message_sticker import MessageStickerHandler
from bot.handlers.message_text import MessageTextHandler


def get_handlers() -> list[Handler]:
    return [
        MessageTextHandler(),
        MessageStickerHandler(),
    ]
