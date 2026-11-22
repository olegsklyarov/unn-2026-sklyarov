import logging
import os

from bot.clock import Clock, SystemClock
from bot.dispatcher import Dispatcher
from bot.handlers import get_handlers
from bot.long_polling import start_long_polling
from bot.messenger import Messenger
from bot.sqlite_storage import SqliteStorage
from bot.storage import Storage
from bot.telegram_messenger import TelegramMessenger

logger = logging.getLogger(__name__)


def main() -> None:
    logging.basicConfig(level=logging.INFO)

    messenger: Messenger = TelegramMessenger(
        token=os.environ["TELEGRAM_TOKEN"],
        base_url=os.environ["TELEGRAM_BASE_URL"],
    )
    storage: Storage = SqliteStorage(
        path=os.environ.get("DATABASE_PATH", "database.sqlite"),
        migrations_dir=os.environ.get("MIGRATIONS_DIR", "migrations"),
    )
    clock: Clock = SystemClock()
    dispatcher = Dispatcher(messenger, storage)
    dispatcher.add_handlers(*get_handlers(clock))
    try:
        start_long_polling(dispatcher, messenger)
    except KeyboardInterrupt:
        logger.info("Bye!")


if __name__ == "__main__":
    main()
