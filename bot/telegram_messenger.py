from bot import telegram_bot_api
from bot.messenger import Messenger


class TelegramMessenger(Messenger):
    def get_updates(self, **params: object) -> list:
        return telegram_bot_api.get_updates(**params)

    def send_message(self, **params: object) -> dict:
        return telegram_bot_api.send_message(**params)
