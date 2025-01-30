# data_feed/trade_data_ws.py

import json
import logging
from .websocket_manager import WebSocketManager

class BinanceTradeWS(WebSocketManager):
    """
    바이낸스 선물 LTCUSDT 체결 데이터(Trade) 실시간 수집 클래스
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
        웹소켓 연결된 후, 체결 데이터 구독 요청
        """
        self.logger.info("Connected. Subscribing to LTCUSDT Trade stream.")

        subscribe_payload = {
            "method": "SUBSCRIBE",
            "params": [
                "ltcusdt@trade",
            ],
            "id": 201
        }
        await self.send_message(subscribe_payload)

    async def on_message(self, message: str):
        """
        체결(trade) 메시지 처리
        """
        try:
            data = json.loads(message)
        except json.JSONDecodeError:
            self.logger.error(f"JSON Decode Error: {message}")
            return

        # 구독 응답 ({"result": null, "id": 201}) 처리
        if "result" in data and "id" in data:
            self.logger.info(f"Subscription Response: {data}")
            return

        # trade 이벤트인지 확인
        event_type = data.get("e")
        if event_type == "trade":
            await self.handle_trade(data)
        else:
            self.logger.debug(f"Unknown event type: {data}")

    async def handle_trade(self, data: dict):
        """
        체결 데이터 처리
        예시:
        {
          "e": "trade",
          "E": 123456789,   // Event time
          "T": 123456785,   // Trade time
          "s": "LTCUSDT",   // Symbol
          "t": 12345,       // Trade ID
          "p": "90.1",      // Price
          "q": "0.5",       // Quantity
          "b": 88,          // Buyer order ID
          "a": 50,          // Seller order ID
          "m": true,        // Is the buyer the market maker?
          "R": true         // Is this trade the best match?
        }
        """
        price = float(data.get("p", 0))
        quantity = float(data.get("q", 0))
        maker_side = "maker" if data.get("m") else "taker"

        self.logger.debug(
            f"[TRADE] Symbol={data.get('s')} Price={price} "
            f"Qty={quantity} Side={maker_side}"
        )
        # TODO: 실시간 체결 기록, 백테스트, 전략 분석, 주문 연계 등

