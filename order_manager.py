# order_execution/order_manager.py

import logging
import time

class OrderManager:
    """
    주문 상태 조회 및 관리
    """

    def __init__(self, exchange_api, logger=None):
        """
        :param exchange_api: 거래소 API 객체 (ex: BinanceFuturesAPI)
        """
        self.exchange_api = exchange_api
        self.logger = logger or logging.getLogger(self.__class__.__name__)

    def wait_for_fill(self, symbol: str, order_id: int, timeout: float = 30.0) -> bool:
        """
        주문 체결 대기 (최대 timeout초까지), 체결되면 True, 실패하면 False
        """
        start_time = time.time()
        while True:
            orders = self.exchange_api.get_open_orders(symbol)
            if isinstance(orders, list):
                if not any(o for o in orders if o.get("orderId") == order_id):
                    self.logger.info(f"Order {order_id} is filled or canceled.")
                    return True
            else:
                self.logger.error(f"Error fetching orders: {orders}")
                return False

            if time.time() - start_time > timeout:
                self.logger.warning(f"Order {order_id} not filled within {timeout} seconds.")
                return False

            time.sleep(1)

    def cancel_order(self, symbol: str, order_id: int):
        """
        주문 취소
        """
        result = self.exchange_api.cancel_order(symbol, order_id)
        self.logger.info(f"Canceled order {order_id}: {result}")
        return result
