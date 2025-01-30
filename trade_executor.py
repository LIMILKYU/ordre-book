# order_execution/trade_executor.py

import logging
import threading
import time

from .position_sizing import PositionSizing
from .risk_management import RiskManager
from .order_manager import OrderManager

class TradeExecutor:
    """
    매매 신호를 받아 주문을 실행하고, 주문 체결까지 관리하는 총괄 클래스
    멀티스레딩 예시 - 하나의 Thread에서 신호를 모니터링, 다른 Thread에서 실행 가능
    """

    def __init__(self, exchange_api, initial_balance: float, logger=None):
        self.exchange_api = exchange_api
        self.logger = logger or logging.getLogger(self.__class__.__name__)

        # 하위 모듈
        self.position_sizing = PositionSizing(logger=self.logger)
        self.risk_manager = RiskManager(logger=self.logger)
        self.order_manager = OrderManager(exchange_api=self.exchange_api, logger=self.logger)

        # 리스크 매니저 초기 잔고 세팅
        self.risk_manager.update_initial_balance(initial_balance)

        # 멀티스레딩을 위한 신호 큐
        self.signal_queue = []
        self._lock = threading.Lock()
        self.running = True

    def start(self):
        """
        시작: 별도의 스레드에서 _execution_loop 동작
        """
        self.execution_thread = threading.Thread(target=self._execution_loop, daemon=True)
        self.execution_thread.start()

    def stop(self):
        """
        스레드 중지
        """
        self.running = False
        self.execution_thread.join()

    def add_signal(self, signal: dict):
        """
        외부에서 매매 신호 (예: {"action":"BUY", "price":100.0, "stop_loss":95.0, ...})를 추가
        """
        with self._lock:
            self.signal_queue.append(signal)

    def _execution_loop(self):
        """
        주기적으로 신호 큐를 확인하고, 매매 실행
        """
        while self.running:
            signal = None
            with self._lock:
                if self.signal_queue:
                    signal = self.signal_queue.pop(0)

            if signal:
                self._execute_trade(signal)
            else:
                time.sleep(0.5)

    def _execute_trade(self, signal: dict):
        """
        실제 매매 로직: 포지션 크기 계산 → 주문 → 체결 모니터링
        """
        self.logger.info(f"Executing trade signal: {signal}")
        action = signal.get("action")  # BUY or SELL
        symbol = signal.get("symbol", "LTCUSDT")
        entry_price = float(signal.get("price", 0))
        stop_loss_price = float(signal.get("stop_loss", 0))

        # 1) 현재 계좌잔고 조회
        balance_info = self.exchange_api.get_account_balance()
        # 예) 선물 계정에서 "USDT" 자산 찾기
        usdt_balance = 0
        for b in balance_info:
            if b.get("asset") == "USDT":
                usdt_balance = float(b.get("balance", 0))

        # 2) 리스크 초과 체크
        if self.risk_manager.check_drawdown(usdt_balance):
            self.logger.warning("Max drawdown exceeded. Skipping trade.")
            return

        # 3) 포지션 사이징
        position_size = self.position_sizing.calculate_position_size(
            account_balance=usdt_balance,
            entry_price=entry_price,
            stop_loss_price=stop_loss_price
        )
        if position_size <= 0:
            self.logger.warning("Position size is 0. Skipping trade.")
            return

        # 4) 주문 실행 (Market 주문 예시)
        order_response = self.exchange_api.place_order(
            symbol=symbol,
            side=action,
            order_type="MARKET",
            quantity=position_size
        )
        self.logger.info(f"Order response: {order_response}")

        order_id = order_response.get("orderId")
        if order_id:
            # 5) 체결 대기
            filled = self.order_manager.wait_for_fill(symbol, order_id, timeout=30.0)
            if not filled:
                # 체결되지 않으면 주문 취소 예시
                self.logger.info("Not filled. Canceling order.")
                self.order_manager.cancel_order(symbol, order_id)
        else:
            self.logger.error("No orderId in response. Possibly an error.")
