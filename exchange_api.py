# order_execution/exchange_api.py

import time
import hmac
import hashlib
import requests
import logging

class BinanceFuturesAPI:
    """
    바이낸스 선물 REST API 연동 예시 스켈레톤
    실제로는 try/except 및 에러 처리, ratelimit 대응 등이 필요
    """

    def __init__(self, api_key: str, api_secret: str, base_url="https://fapi.binance.com", logger=None):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url
        self.logger = logger or logging.getLogger(self.__class__.__name__)

    def _sign(self, params: dict) -> dict:
        """
        파라미터에 timestamp, signature 추가
        """
        params["timestamp"] = int(time.time() * 1000)
        query_string = "&".join([f"{k}={v}" for k,v in params.items()])
        signature = hmac.new(self.api_secret.encode("utf-8"), 
                             query_string.encode("utf-8"), 
                             hashlib.sha256).hexdigest()
        params["signature"] = signature
        return params

    def _headers(self) -> dict:
        return {
            "X-MBX-APIKEY": self.api_key
        }

    def place_order(self, symbol: str, side: str, order_type: str, quantity: float, price: float = None) -> dict:
        """
        주문 발행 (예: MARKET or LIMIT)
        """
        endpoint = "/fapi/v1/order"
        url = self.base_url + endpoint

        params = {
            "symbol": symbol,
            "side": side,       # "BUY" or "SELL"
            "type": order_type, # "MARKET", "LIMIT"
            "quantity": quantity,
        }
        if order_type == "LIMIT" and price:
            params["price"] = price
            params["timeInForce"] = "GTC"

        # 서명
        params = self._sign(params)

        self.logger.debug(f"Placing order: {params}")
        response = requests.post(url, params=params, headers=self._headers())
        return response.json()

    def cancel_order(self, symbol: str, order_id: int) -> dict:
        """
        주문 취소
        """
        endpoint = "/fapi/v1/order"
        url = self.base_url + endpoint

        params = {
            "symbol": symbol,
            "orderId": order_id
        }
        params = self._sign(params)

        response = requests.delete(url, params=params, headers=self._headers())
        return response.json()

    def get_open_orders(self, symbol: str) -> dict:
        """
        미체결 주문 조회
        """
        endpoint = "/fapi/v1/openOrders"
        url = self.base_url + endpoint

        params = {
            "symbol": symbol
        }
        params = self._sign(params)

        response = requests.get(url, params=params, headers=self._headers())
        return response.json()

    def get_account_balance(self) -> dict:
        """
        계좌 잔고(자산) 조회
        """
        endpoint = "/fapi/v2/balance"
        url = self.base_url + endpoint

        params = {}
        params = self._sign(params)

        response = requests.get(url, params=params, headers=self._headers())
        return response.json()
