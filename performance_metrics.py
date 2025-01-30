# backtesting/performance_metrics.py

import numpy as np
import pandas as pd
import logging

class PerformanceMetrics:
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(self.__class__.__name__)

    def calculate_metrics(self, result_df: pd.DataFrame) -> dict:
        """
        result_df에는 최소한 'strategy_returns' 혹은 'cum_strategy_returns'가 있어야 함
        """
        if "strategy_returns" not in result_df.columns:
            self.logger.warning("No 'strategy_returns' column found in result DataFrame.")
            return {}

        daily_returns = result_df["strategy_returns"].dropna()
        if len(daily_returns) < 2:
            self.logger.warning("Insufficient data for performance metrics.")
            return {}

        # 승률 (signal 기반으로 계산 가능. 여기서는 단순히 수익 양/음 비율로 예시)
        win_trades = daily_returns[daily_returns > 0].count()
        total_trades = daily_returns[daily_returns != 0].count()
        win_rate = win_trades / total_trades if total_trades else 0

        # 샤프 비율 (연율화 가정, 일봉 기준)
        sharpe_ratio = self._sharpe_ratio(daily_returns, periods_per_year=252)

        # 최대 낙폭 (MDD)
        cum_returns = (1 + daily_returns).cumprod()
        rolling_max = cum_returns.cummax()
        drawdown = (cum_returns - rolling_max) / rolling_max
        max_drawdown = drawdown.min()

        metrics = {
            "win_rate": win_rate,
            "sharpe_ratio": sharpe_ratio,
            "max_drawdown": max_drawdown
        }
        self.logger.debug(f"Performance Metrics: {metrics}")
        return metrics

    def _sharpe_ratio(self, returns: pd.Series, risk_free_rate=0.0, periods_per_year=252) -> float:
        """
        샤프 비율 계산: (mean(returns) - risk_free_rate) / std(returns) * sqrt(periods_per_year)
        """
        mean_return = returns.mean()
        std_return = returns.std()
        if std_return == 0:
            return 0
        sharpe = (mean_return - risk_free_rate) / std_return * np.sqrt(periods_per_year)
        return sharpe
