from typing import Any

from bot.catalog import (
    FINISHED,
    PIZZA_PROMPT,
    PIZZAS,
    SIZE_PROMPT,
    SIZES,
    WAITING_FOR_PIZZA_SIZE,
    WAITING_FOR_PIZZA_TYPE,
    choice,
)
from bot.clock import Clock
from bot.handlers.handler import Handler, HandlerStatus
from bot.handlers.reply import acknowledge, send_menu
from bot.messenger import Messenger
from bot.storage import Storage
from bot.telegram_update import callback_data, chat_id, telegram_user, telegram_user_id


class PizzaTypeHandler(Handler):
    def __init__(self, clock: Clock) -> None:
        self._clock = clock

    def can_handle(self, update: dict[str, Any], state: str | None) -> bool:
        tracked = state in {None, WAITING_FOR_PIZZA_TYPE, FINISHED}
        return tracked and telegram_user(update) is not None

    def handle(
        self,
        update: dict[str, Any],
        state: str | None,
        messenger: Messenger,
        storage: Storage,
    ) -> HandlerStatus:
        user_id = telegram_user_id(update)
        target_chat = chat_id(update)
        if user_id is None or target_chat is None:
            return HandlerStatus.STOP
        if state == FINISHED:
            storage.save_order(
                telegram_user_id=user_id,
                state=WAITING_FOR_PIZZA_TYPE,
                order={},
                updated_at=self._clock.now(),
            )
            send_menu(messenger, target_chat, PIZZA_PROMPT, PIZZAS)
            acknowledge(update, messenger)
            return HandlerStatus.STOP
        selected = choice(PIZZAS, callback_data(update))
        if selected is not None:
            storage.save_order(
                telegram_user_id=user_id,
                state=WAITING_FOR_PIZZA_SIZE,
                order={"type": selected},
                updated_at=self._clock.now(),
            )
            send_menu(messenger, target_chat, SIZE_PROMPT, SIZES)
            acknowledge(update, messenger)
            return HandlerStatus.STOP
        send_menu(messenger, target_chat, PIZZA_PROMPT, PIZZAS)
        acknowledge(update, messenger)
        return HandlerStatus.STOP
