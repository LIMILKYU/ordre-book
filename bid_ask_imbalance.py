# signal_generator/bid_ask_imbalance.py

import logging
import random

class BidAskImbalanceAnalyzer:
    """
    Bid-Ask Imbalance(호가창 매수량 vs 매도량 차이)를 분석하여
    불균형이 큰 경우 매수/매도 시그널을 낼 수 있음.
    여기서는 간단히 ratio만 계산하는 예시.
    """

    def __init__(self, threshold=1.2, logger=None):
        """
        :param threshold: 매수 우위(ratio) 기준값
        """
        self.threshold = threshold
        self.logger = logger or logging.getLogger(self.__class__.__name__)

    def analyze(self, order_book_data: dict) -> dict:
        """
        order_book_data를 받아서 Bid-Ask 비율을 계산하고,
        시그널을 반환하는 메서드
        """
        # 실제로는 order_book_data["bids"], order_book_data["asks"] 등에서 
        # 호가 총합(수량)을 구해 비율을 계산해야 합니다.
        # 여기서는 랜덤으로 ratio 생성
        ratio = random.uniform(0.8, 1.5)

        signal = {
            "type": "bid_ask_imbalance",
            "ratio": ratio,
            "recommendation": "BUY" if ratio > self.threshold else "HOLD"
        }
        self.logger.debug(f"[BidAskImbalance] signal={signal}")
        return signal
