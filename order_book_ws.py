# data_feed/order_book_ws.py

import json
import logging
from .websocket_manager import WebSocketManager

class BinanceOrderBookWS(WebSocketManager):
    """
    바이낸스 선물 LTCUSDT의 오더북(호가) 실시간 수집 클래스
    """

    def __init__(
        self,
        uri="wss://fstream.binance.com/ws",
        max_retries=5,
        base_retry_delay=1.0,
        logger: logging.Logger = None,
    ):
        super().__init__(uri, max_retries, base_retry_delay, logger)

    async def on_connect(self):
        """
        웹소켓 연결된 후, 오더북 구독 요청
        """
        self.logger.info("Connected. Subscribing to LTCUSDT OrderBook streams.")

        # 여러 스트림 구독 (Top5, Top20, 100ms)
        subscribe_payload = {
            "method": "SUBSCRIBE",
            "params": [
                "ltcusdt@depth5@100ms",
                "ltcusdt@depth20@100ms",
                # 필요에 따라 전체 depth, 10, 20, 50 레벨 등 추가 가능
            ],
            "id": 101
        }
        await self.send_message(subscribe_payload)

    async def on_message(self, message: str):
        """
        오더북 메시지(depthUpdate) 처리
        """
        try:
            data = json.loads(message)
        except json.JSONDecodeError:
            self.logger.error(f"JSON Decode Error: {message}")
            return

        # 구독 응답 ({"result": null, "id": 101}) 등은 여기서 처리할 수 있음
        if "result" in data and "id" in data:
            self.logger.info(f"Subscription Response: {data}")
            return

        # depthUpdate 이벤트인지 확인
        event_type = data.get("e")
        if event_type == "depthUpdate":
            await self.handle_depth(data)
        else:
            self.logger.debug(f"Unknown event type: {data}")

    async def handle_depth(self, data: dict):
        """
        오더북 데이터 처리
        예시:
        {
          "e": "depthUpdate",
          "E": 123456789,   
          "T": 123456788,  
          "s": "LTCUSDT",   
          "U": 1234,        
          "u": 1235,        
          "b": [["90.1", "10.5"], ...],
          "a": [["90.2", "0.1"], ...]
        }
        """
        symbol = data.get("s", "")
        bids = data.get("b", [])
        asks = data.get("a", [])
        event_time = data.get("E", 0)

        # TODO: 깊은 레벨 vs 빠른 레벨 구분하려면 (ex. params 구독 스트림명)까지 추적하거나,
        #       혹은 b, a의 호가 개수 등으로 판별 가능.
        self.logger.debug(
            f"[ORDER_BOOK] Symbol={symbol} EventTime={event_time}\n"
            f"  Bids={bids}\n"
            f"  Asks={asks}"
        )

        # 여기서 수집 데이터를 저장/가공/큐(queue)에 넣는 등 확장 가능
