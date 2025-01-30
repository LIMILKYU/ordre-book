# signal_generator/signal_manager.py

import logging
import multiprocessing

from .bid_ask_imbalance import BidAskImbalanceAnalyzer
from .iceberg_detector import IcebergDetector
from .vwap_obv_analyzer import VWAPOBVAnalyzer
from .market_depth_analyzer import MarketDepthAnalyzer
from .order_flow_analyzer import OrderFlowAnalyzer

class SignalManager:
    """
    여러 분석 모듈을 호출하여 최종 매매 신호를 생성
    """

    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(self.__class__.__name__)

        # 하위 분석 모듈들 초기화
        self.bid_ask_analyzer = BidAskImbalanceAnalyzer(logger=self.logger)
        self.iceberg_detector = IcebergDetector(logger=self.logger)
        self.vwap_obv_analyzer = VWAPOBVAnalyzer(logger=self.logger)
        self.market_depth_analyzer = MarketDepthAnalyzer(logger=self.logger)
        self.order_flow_analyzer = OrderFlowAnalyzer(logger=self.logger)

    def generate_signals(self, order_book_data: dict, trade_data: list) -> dict:
        """
        개별 분석 모듈들의 신호를 취합하여 최종 매매 신호를 반환
        """
        # 1) 각 모듈에서 시그널 수집
        imbalance_signal = self.bid_ask_analyzer.analyze(order_book_data)
        iceberg_signal = self.iceberg_detector.detect(order_book_data)
        vwap_obv_signal = self.vwap_obv_analyzer.analyze(trade_data)
        depth_signal = self.market_depth_analyzer.analyze(order_book_data)
        flow_signal = self.order_flow_analyzer.analyze(order_book_data, trade_data)

        # 2) 종합
        final_signal = self._combine_signals([
            imbalance_signal,
            iceberg_signal,
            vwap_obv_signal,
            depth_signal,
            flow_signal
        ])

        return final_signal

    def _combine_signals(self, signals: list) -> dict:
        """
        간단히 majority vote(혹은 조건부 가중치 등)로 최종 매매 신호 도출
        """
        recommendations = [s.get("recommendation", "HOLD") for s in signals]
        buy_count = recommendations.count("BUY")
        sell_count = recommendations.count("SELL")

        final_rec = "HOLD"
        if buy_count > sell_count and buy_count >= 2:
            final_rec = "BUY"
        elif sell_count > buy_count and sell_count >= 2:
            final_rec = "SELL"

        return {
            "signals": signals,
            "final_recommendation": final_rec
        }


def run_signal_manager(input_queue, output_queue):
    """
    멀티프로세싱에서 별도 프로세스로 실행될 Worker 함수 예시

    - input_queue: { "order_book": ..., "trade": ... } 형태로 데이터가 들어옴
    - output_queue: { "signals": [...], "final_recommendation": ... } 형태의 결과를 반환
    """
    logger = logging.getLogger("SignalManagerProcess")
    manager = SignalManager(logger=logger)

    while True:
        data = input_queue.get()
        if data is None:
            # 종료 신호
            break

        order_book_data = data.get("order_book", {})
        trade_data = data.get("trade", [])

        # 시그널 생성
        final_signal = manager.generate_signals(order_book_data, trade_data)
        logger.info(f"Final Signal: {final_signal}")

        # 결과를 output_queue에 넣어 다른 프로세스/모듈이 활용 가능
        output_queue.put(final_signal)
