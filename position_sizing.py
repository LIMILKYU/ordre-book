# order_execution/position_sizing.py

import logging

class PositionSizing:
    """
    포지션 크기 결정 로직.
    예) 계좌 자본금의 일정 %를 1회 트레이드에 사용
    """

    def __init__(self, risk_per_trade=0.01, logger=None):
        """
        :param risk_per_trade: 계좌 자본금 대비 1회 트레이드에서 허용할 리스크(0.01 = 1%)
        """
        self.risk_per_trade = risk_per_trade
        self.logger = logger or logging.getLogger(self.__class__.__name__)

    def calculate_position_size(self, account_balance: float, entry_price: float, stop_loss_price: float) -> float:
        """
        단순 예시:
        - Risk = (entry_price - stop_loss_price) * position_size
        - Risk <= account_balance * risk_per_trade
        => position_size <= (account_balance * risk_per_trade) / (entry_price - stop_loss_price)
        """
        if stop_loss_price == 0 or entry_price == stop_loss_price:
            self.logger.warning("Invalid stop_loss_price. Using default position size = 0.")
            return 0

        risk_amount = account_balance * self.risk_per_trade
        distance = abs(entry_price - stop_loss_price)
        if distance == 0:
            self.logger.warning("Distance between entry and stop loss is zero.")
            return 0

        position_size = risk_amount / distance
        # 여기서는 단순히 양수만
        self.logger.debug(f"Calculated position size: {position_size}")
        return position_size
