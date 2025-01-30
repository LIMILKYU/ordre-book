# signal_generator/market_depth_analyzer.py

import logging
import random

class MarketDepthAnalyzer:
    """
    시장 깊이(호가 레벨이 얼마나 빡빡한가, 유동성은 풍부한가)를 평가해
    매매 신호에 참고하는 분석 모듈 예시
    """

    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(self.__class__.__name__)

    def analyze(self, order_book_data: dict) -> dict:
        """
        order_book_data로부터 유동성 지표(depth_metric)를 구해 시그널 생성
        """
        depth_metric = random.uniform(0, 1)
        # depth_metric이 낮으면 시장 유동성이 낮거나, 특정 쏠림이 발생 중이라 가정
        recommendation = "SELL" if depth_metric < 0.2 else "HOLD"

        signal = {
            "type": "market_depth",
            "depth_metric": depth_metric,
            "recommendation": recommendation
        }
        self.logger.debug(f"[MarketDepthAnalyzer] signal={signal}")
        return signal
