import logging
import os

from bot.dispatcher import Dispatcher
from bot.handlers import get_handlers
from bot.long_polling import start_long_polling
from bot.telegram_messenger import TelegramMessenger

logger = logging.getLogger(__name__)


def main() -> None:
    logging.basicConfig(level=logging.INFO)

    messenger = TelegramMessenger(
        token=os.environ["TELEGRAM_TOKEN"],
        base_url=os.environ["TELEGRAM_BASE_URL"],
    )
    dispatcher = Dispatcher(messenger)
    dispatcher.add_handlers(*get_handlers())
    try:
        start_long_polling(dispatcher, messenger)
    except KeyboardInterrupt:
        logger.info("Bye!")


if __name__ == "__main__":
    main()
