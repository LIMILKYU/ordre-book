# order_execution/risk_management.py

import logging

class RiskManager:
    """
    포지션 모니터링, 손익 계산, 최대 허용 손실(DD) 관리, 트레일링 스탑 등
    """

    def __init__(self, max_drawdown=0.2, logger=None):
        """
        :param max_drawdown: 계좌 자본금 대비 최대 허용 손실 20% 등
        """
        self.max_drawdown = max_drawdown
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        self.initial_balance = None

    def update_initial_balance(self, balance: float):
        """시작 시점 계좌 잔고 기록"""
        self.initial_balance = balance

    def check_drawdown(self, current_balance: float) -> bool:
        """
        최대 손실 한도 초과 여부 판단
        """
        if self.initial_balance is None:
            self.initial_balance = current_balance

        dd = (self.initial_balance - current_balance) / self.initial_balance
        self.logger.debug(f"Current Drawdown: {dd*100:.2f}%")
        return dd > self.max_drawdown

    def calculate_pnl(self, entry_price: float, current_price: float, position_size: float, side: str) -> float:
        """
        단순한 PnL 계산 (선물, 레버리지 고려 x 예시)
        """
        if side.upper() == "BUY":
            return (current_price - entry_price) * position_size
        elif side.upper() == "SELL":
            return (entry_price - current_price) * position_size
        return 0.0
