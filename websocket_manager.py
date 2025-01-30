# data_feed/websocket_manager.py

import asyncio
import json
import logging
import websockets

class WebSocketManager:
    """
    WebSocket 연결 및 재연결 로직을 공통으로 제공하는 추상(기반) 클래스.
    구체적인 구독/해석 로직은 자식 클래스에서 구현합니다.
    """

    def __init__(
        self,
        uri: str,
        max_retries: int = 5,
        base_retry_delay: float = 1.0,
        logger: logging.Logger = None,
    ):
        """
        :param uri: 웹소켓 서버 주소
        :param max_retries: 재연결 최대 시도 횟수 (0 이하이면 무제한)
        :param base_retry_delay: 재연결 시도 간격의 기본값(초)
        :param logger: 로거(없으면 기본 로거 사용)
        """
        self.uri = uri
        self.max_retries = max_retries
        self.base_retry_delay = base_retry_delay
        self.logger = logger if logger else logging.getLogger(self.__class__.__name__)

        # 내부 상태
        self._websocket = None
        self._connected = False
        self._running = True

    async def connect(self):
        """
        웹소켓 연결 시도
        """
        self.logger.info(f"Attempting to connect to {self.uri}")
        self._websocket = await websockets.connect(self.uri)
        self._connected = True
        self.logger.info("Connected to WebSocket server")
        await self.on_connect()

    async def close(self):
        """
        웹소켓 연결 종료
        """
        self._running = False
        if self._websocket is not None:
            await self._websocket.close()
            self._connected = False
            self.logger.info("WebSocket connection closed")
        await self.on_disconnect()

    async def listen(self):
        """
        메인 루프: 메시지 수신 및 재연결 관리
        """
        retry_count = 0
        while self._running:
            try:
                if not self._connected:
                    await self.connect()

                async for message in self._websocket:
                    await self.on_message(message)

            except (websockets.ConnectionClosed, ConnectionError) as e:
                self.logger.warning(f"Connection lost: {e}")
                self._connected = False

                if self.max_retries > 0 and retry_count >= self.max_retries:
                    self.logger.error("Max retries reached. Stopping reconnection.")
                    break

                retry_count += 1
                delay = self._get_retry_delay(retry_count)
                self.logger.info(f"Reconnecting in {delay:.1f} seconds... (Retry {retry_count})")
                await asyncio.sleep(delay)

            except Exception as e:
                self.logger.exception(f"Unexpected error: {e}")
                await asyncio.sleep(1)
            else:
                # 정상 종료
                self.logger.info("WebSocket connection closed normally.")
                break

        await self.close()

    def _get_retry_delay(self, retry_count: int) -> float:
        """
        지수 백오프(Exponential Backoff) 계산
        """
        return self.base_retry_delay * (2 ** (retry_count - 1))

    async def on_connect(self):
        """
        웹소켓 연결 후, 구독(subscribe) 등 필요한 초기화 로직.
        자식 클래스에서 오버라이드하여 사용.
        """
        self.logger.info("Performing on_connect actions. (Override me in child class)")

    async def on_disconnect(self):
        """
        웹소켓 연결이 끊어졌을 때 처리할 후속 작업.
        자식 클래스에서 오버라이드하여 사용.
        """
        self.logger.info("Performing on_disconnect actions. (Override me in child class)")

    async def on_message(self, message: str):
        """
        서버 메시지 수신 시 호출.
        자식 클래스에서 파싱/처리 로직 오버라이드.
        """
        self.logger.debug(f"Received message: {message}")

    async def send_message(self, message: dict):
        """
        서버로 메시지 전송
        """
        if self._websocket and self._connected:
            await self._websocket.send(json.dumps(message))
        else:
            self.logger.warning("Cannot send message - WebSocket not connected.")
