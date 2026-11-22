from bot.clock import Clock
from bot.handlers.ensure_user import EnsureUserHandler
from bot.handlers.handler import Handler
from bot.handlers.pizza_drink import PizzaDrinkHandler
from bot.handlers.pizza_size import PizzaSizeHandler
from bot.handlers.pizza_type import PizzaTypeHandler
from bot.handlers.update_logger import UpdateLoggerHandler


def get_handlers(clock: Clock) -> list[Handler]:
    return [
        UpdateLoggerHandler(clock),
        EnsureUserHandler(clock),
        PizzaTypeHandler(clock),
        PizzaSizeHandler(clock),
        PizzaDrinkHandler(clock),
    ]
