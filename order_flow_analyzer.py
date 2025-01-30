# signal_generator/order_flow_analyzer.py

import logging
import random

class OrderFlowAnalyzer:
    """
    오더북 변화량 + 체결 강도(Order Flow)를 분석해, 
    매수세/매도세가 강하게 들어오는지 판단
    """

    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(self.__class__.__name__)

    def analyze(self, order_book_data: dict, trade_data: list) -> dict:
        """
        order_book_data와 trade_data(최근 체결)에 기반하여
        매수/매도 흐름(Order Flow)를 계산
        """
        # 예시로 -1.0 ~ 1.0 사이의 flow_strength를 랜덤하게 생성
        flow_strength = random.uniform(-1, 1)
        side = "BUY" if flow_strength > 0.5 else ("SELL" if flow_strength < -0.5 else "NONE")

        signal = {
            "type": "order_flow",
            "flow_strength": flow_strength,
            "recommendation": side  # 실제로는 "NONE"이면 HOLD로 처리
        }
        self.logger.debug(f"[OrderFlowAnalyzer] signal={signal}")
        return signal
