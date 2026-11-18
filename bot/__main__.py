from bot.dispatcher import Dispatcher
from bot.handlers import get_handlers
from bot.long_polling import start_long_polling
from bot.telegram_messenger import TelegramMessenger


def main() -> None:
    messenger = TelegramMessenger()
    dispatcher = Dispatcher(messenger)
    dispatcher.add_handlers(*get_handlers())
    try:
        start_long_polling(dispatcher, messenger)
    except KeyboardInterrupt:
        print("\nBye!")


if __name__ == "__main__":
    main()
