# signal_generator/vwap_obv_analyzer.py

import logging
import random

class VWAPOBVAnalyzer:
    """
    체결 데이터(Trade Data)를 이용해 VWAP, OBV 등을 계산하고
    시그널을 생성하는 예시
    """

    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(self.__class__.__name__)

    def analyze(self, trade_data: list) -> dict:
        """
        trade_data를 바탕으로 VWAP, OBV 등을 계산
        여기서는 간단히 랜덤값을 예시로 계산
        """
        vwap = random.uniform(80, 120)  # 실제로는 Σ(가격*거래량) / Σ(거래량)
        obv = random.uniform(-1000, 1000)  # 실제로는 OBV = 이전 OBV ± 거래량 (가격 상승/하락)
        recommendation = "BUY" if (vwap < 90 and obv > 0) else "HOLD"

        signal = {
            "type": "vwap_obv",
            "vwap": vwap,
            "obv": obv,
            "recommendation": recommendation
        }
        self.logger.debug(f"[VWAPOBVAnalyzer] signal={signal}")
        return signal
