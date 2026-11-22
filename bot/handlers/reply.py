from typing import Any

from bot.catalog import inline_keyboard
from bot.messenger import Messenger
from bot.storage import Storage
from bot.telegram_update import callback_message_id, callback_query_id, chat_id


def send_menu(
    messenger: Messenger,
    chat_id: int,
    text: str,
    options: tuple[tuple[str, str], ...],
) -> None:
    messenger.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=inline_keyboard(options),
    )


def drop_keyboard(update: dict[str, Any], messenger: Messenger) -> None:
    message_id = callback_message_id(update)
    target_chat = chat_id(update)
    if message_id is None or target_chat is None:
        return
    messenger.delete_message(chat_id=target_chat, message_id=message_id)


def acknowledge(update: dict[str, Any], messenger: Messenger) -> None:
    query_id = callback_query_id(update)
    if query_id is None:
        return
    messenger.answer_callback_query(callback_query_id=query_id)


def remembered_order(storage: Storage, telegram_user_id: int) -> dict[str, str]:
    user = storage.get_user(telegram_user_id)
    if user is None:
        return {}
    return dict(user.order)
