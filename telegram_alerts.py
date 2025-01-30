# notification/telegram_alerts.py

import logging
import requests

class TelegramAlerts:
    """
    텔레그램 봇(채팅방)에 메시지를 전송하는 클래스 예시
    """

    def __init__(self, bot_token: str, chat_id: str, logger=None):
        """
        :param bot_token: 텔레그램 봇 API 토큰
        :param chat_id: 전송할 채팅방/채널 ID
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.logger = logger or logging.getLogger(self.__class__.__name__)

    def send_message(self, text: str):
        """
        텔레그램 채팅방에 메시지 전송
        """
        if not self.bot_token or not self.chat_id:
            self.logger.warning("No Telegram bot token or chat_id configured.")
            return

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        data = {
            "chat_id": self.chat_id,
            "text": text
        }

        try:
            resp = requests.post(url, data=data)
            if resp.status_code != 200:
                self.logger.error(f"Telegram message failed: {resp.text}")
        except Exception as e:
            self.logger.exception(f"Error sending Telegram message: {e}")
