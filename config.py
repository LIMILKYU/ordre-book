# config/config.py

import os
import json

class Config:
    """
    애플리케이션 전체에서 사용하는 각종 설정값을 관리하는 클래스.
    예: API 키, 비밀키, 각종 파라미터.
    """
    def __init__(self, config_file=None):
        """
        :param config_file: JSON 등의 설정 파일 경로 (선택)
        """
        # 예: 우선 환경변수에서 불러오고, 설정파일이 있으면 파일값 사용
        self.api_key = os.getenv("BINANCE_API_KEY", "")
        self.api_secret = os.getenv("BINANCE_API_SECRET", "")
        self.telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
        self.discord_webhook_url = os.getenv("DISCORD_WEBHOOK_URL", "")

        self.log_level = os.getenv("LOG_LEVEL", "DEBUG")  # 로깅 레벨
        self.data_dir = os.getenv("DATA_DIR", "./data")   # 데이터 저장 디렉토리 등

        # 필요하다면 더 많은 설정값을 추가

        # 설정 파일에서 값을 덮어쓸 수도 있음
        if config_file:
            self._load_from_file(config_file)

    def _load_from_file(self, config_file):
        """
        JSON 형식의 설정 파일을 읽어서, 해당 값으로 인스턴스 속성을 업데이트
        """
        try:
            with open(config_file, "r") as f:
                file_config = json.load(f)
            for key, value in file_config.items():
                # 예: file_config = { "api_key": "...", "api_secret": "..." }
                setattr(self, key, value)
        except FileNotFoundError:
            print(f"[WARN] Config file not found: {config_file}")
        except json.JSONDecodeError:
            print(f"[ERROR] Invalid JSON in config file: {config_file}")
