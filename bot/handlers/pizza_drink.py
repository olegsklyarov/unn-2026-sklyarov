from typing import Any

from bot.catalog import (
    DRINK_PROMPT,
    DRINKS,
    FINISHED,
    WAITING_FOR_DRINK,
    choice,
    format_order,
)
from bot.clock import Clock
from bot.handlers.handler import Handler, HandlerStatus
from bot.handlers.reply import acknowledge, remembered_order, send_menu
from bot.messenger import Messenger
from bot.storage import Storage
from bot.telegram_update import callback_data, chat_id, telegram_user, telegram_user_id


class PizzaDrinkHandler(Handler):
    def __init__(self, clock: Clock) -> None:
        self._clock = clock

    def can_handle(self, update: dict[str, Any], state: str | None) -> bool:
        return state == WAITING_FOR_DRINK and telegram_user(update) is not None

    def handle(
        self,
        update: dict[str, Any],
        _state: str | None,
        messenger: Messenger,
        storage: Storage,
    ) -> HandlerStatus:
        user_id = telegram_user_id(update)
        target_chat = chat_id(update)
        if user_id is None or target_chat is None:
            return HandlerStatus.STOP
        selected = choice(DRINKS, callback_data(update))
        if selected is not None:
            order = remembered_order(storage, user_id)
            order["drink"] = selected
            storage.save_order(
                telegram_user_id=user_id,
                state=FINISHED,
                order=order,
                updated_at=self._clock.now(),
            )
            messenger.send_message(chat_id=target_chat, text=format_order(order))
            acknowledge(update, messenger)
            return HandlerStatus.STOP
        send_menu(messenger, target_chat, DRINK_PROMPT, DRINKS)
        acknowledge(update, messenger)
        return HandlerStatus.STOP
