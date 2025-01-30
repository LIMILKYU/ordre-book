# notification/discord_alerts.py

import logging
import requests

class DiscordAlerts:
    """
    디스코드 웹훅(Discord Webhook)으로 메시지를 보내는 클래스 예시
    """

    def __init__(self, webhook_url: str, logger=None):
        """
        :param webhook_url: 디스코드 웹훅 URL
        """
        self.webhook_url = webhook_url
        self.logger = logger or logging.getLogger(self.__class__.__name__)

    def send_message(self, content: str):
        """
        간단히 content 문자열을 디스코드 채널에 전송
        """
        if not self.webhook_url:
            self.logger.warning("No Discord Webhook URL configured.")
            return

        payload = {
            "content": content
        }
        try:
            resp = requests.post(self.webhook_url, json=payload)
            if resp.status_code != 204 and resp.status_code != 200:
                self.logger.error(f"Discord message failed: {resp.text}")
        except Exception as e:
            self.logger.exception(f"Error sending Discord message: {e}")
