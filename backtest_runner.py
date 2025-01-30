# backtesting/backtest_runner.py

import logging
import pandas as pd
from typing import Callable, Dict, Any

class BacktestRunner:
    """
    백테스트 실행을 담당하는 클래스
    """

    def __init__(
        self,
        strategy_func: Callable[[pd.DataFrame, Dict[str, Any]], pd.DataFrame],
        logger=None
    ):
        """
        :param strategy_func: 사용자 정의 전략 함수
               - 입력: (price_data: pd.DataFrame, params: dict)
               - 출력: 트레이드 결과 or 시뮬레이션 결과가 포함된 DataFrame
        """
        self.strategy_func = strategy_func
        self.logger = logger or logging.getLogger(self.__class__.__name__)

    def run(self, price_data: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
        """
        백테스트 실행:
        1) price_data (과거 시세) & params(전략 파라미터)로 전략 수행
        2) 해당 결과(진입/청산 기록, PnL, 지표 등)를 포함한 DataFrame 반환
        """
        self.logger.info(f"Starting backtest with params={params}")
        result_df = self.strategy_func(price_data, params)
        return result_df


def example_strategy(price_data: pd.DataFrame, params: dict) -> pd.DataFrame:
    """
    간단한 이동평균 전략 예시:
    params: {"short_window": 5, "long_window": 20}
    - 짧은 이동평균이 긴 이동평균을 상향 돌파하면 매수, 하향 돌파하면 매도
    - 결과 DataFrame에 (signal, position, pnl 등) 칼럼을 추가
    """
    short_window = params.get("short_window", 5)
    long_window = params.get("long_window", 20)

    df = price_data.copy()
    df["ma_short"] = df["close"].rolling(window=short_window).mean()
    df["ma_long"] = df["close"].rolling(window=long_window).mean()

    df["signal"] = 0
    df.loc[df["ma_short"] > df["ma_long"], "signal"] = 1
    df.loc[df["ma_short"] < df["ma_long"], "signal"] = -1

    # 포지션 계산(shift로 종가 다음날 진입 가정)
    df["position"] = df["signal"].shift(1).fillna(0)

    # 단순 일일 수익률
    df["returns"] = df["close"].pct_change()
    # 전략 수익률
    df["strategy_returns"] = df["position"] * df["returns"]

    # 누적 수익률
    df["cum_strategy_returns"] = (1 + df["strategy_returns"]).cumprod()
    return df
