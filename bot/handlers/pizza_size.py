from typing import Any

from bot.catalog import (
    DRINK_PROMPT,
    DRINKS,
    SIZE_PROMPT,
    SIZES,
    WAITING_FOR_DRINK,
    WAITING_FOR_PIZZA_SIZE,
    choice,
)
from bot.clock import Clock
from bot.handlers.handler import Handler, HandlerStatus
from bot.handlers.reply import acknowledge, remembered_order, send_menu
from bot.messenger import Messenger
from bot.storage import Storage
from bot.telegram_update import callback_data, chat_id, telegram_user, telegram_user_id


class PizzaSizeHandler(Handler):
    def __init__(self, clock: Clock) -> None:
        self._clock = clock

    def can_handle(self, update: dict[str, Any], state: str | None) -> bool:
        return state == WAITING_FOR_PIZZA_SIZE and telegram_user(update) is not None

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
        selected = choice(SIZES, callback_data(update))
        if selected is not None:
            order = remembered_order(storage, user_id)
            order["size"] = selected
            storage.save_order(
                telegram_user_id=user_id,
                state=WAITING_FOR_DRINK,
                order=order,
                updated_at=self._clock.now(),
            )
            send_menu(messenger, target_chat, DRINK_PROMPT, DRINKS)
            acknowledge(update, messenger)
            return HandlerStatus.STOP
        send_menu(messenger, target_chat, SIZE_PROMPT, SIZES)
        acknowledge(update, messenger)
        return HandlerStatus.STOP
