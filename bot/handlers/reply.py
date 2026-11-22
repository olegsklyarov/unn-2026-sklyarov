from typing import Any

from bot.catalog import inline_keyboard
from bot.messenger import Messenger
from bot.storage import Storage
from bot.telegram_update import callback_query_id


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
