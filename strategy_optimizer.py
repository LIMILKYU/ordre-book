# backtesting/strategy_optimizer.py

import logging
import itertools
import multiprocessing

from typing import Dict, Any, List
import pandas as pd

from .backtest_runner import BacktestRunner
from .performance_metrics import PerformanceMetrics

def _worker_task(args):
    """
    멀티프로세싱에서 사용할 Worker 함수
    :param args: (runner, price_data, params)
    """
    runner, price_data, params_dict = args
    result_df = runner.run(price_data, params_dict)
    metrics_calculator = PerformanceMetrics(logger=runner.logger)
    metrics = metrics_calculator.calculate_metrics(result_df)
    return (params_dict, metrics)

class StrategyOptimizer:
    """
    다양한 파라미터 조합으로 백테스트를 수행하고,
    성능 지표가 가장 우수한 파라미터를 찾는 클래스
    """

    def __init__(
        self,
        runner: BacktestRunner,
        logger=None
    ):
        """
        :param runner: 이미 설정된 BacktestRunner (strategy_func 포함)
        """
        self.runner = runner
        self.logger = logger or logging.getLogger(self.__class__.__name__)

    def grid_search(
        self,
        price_data: pd.DataFrame,
        param_grid: Dict[str, List[Any]],
        max_workers: int = 4
    ) -> pd.DataFrame:
        """
        param_grid 예시: {
          "short_window": [5, 10, 20],
          "long_window": [20, 50]
        }
        """
        # 1) 모든 파라미터 조합 생성
        keys = list(param_grid.keys())
        all_combinations = list(itertools.product(*[param_grid[k] for k in keys]))

        # 2) 멀티프로세싱으로 병렬 백테스트
        self.logger.info(f"Starting grid search with {len(all_combinations)} combinations...")
        pool = multiprocessing.Pool(processes=max_workers)

        tasks = []
        for combo in all_combinations:
            params_dict = {k: combo[i] for i, k in enumerate(keys)}
            tasks.append((self.runner, price_data, params_dict))

        results = pool.map(_worker_task, tasks)
        pool.close()
        pool.join()

        # 3) 결과 정리 (DataFrame 형태)
        rows = []
        for (params_dict, metrics) in results:
            row = {**params_dict, **metrics}
            rows.append(row)

        df_results = pd.DataFrame(rows)
        return df_results

    def find_best_params(self, df_results: pd.DataFrame, metric: str = "sharpe_ratio") -> Dict[str, Any]:
        """
        metric 기준으로 가장 좋은 파라미터 찾기
        (예: 샤프 비율 최고)
        """
        if len(df_results) == 0 or metric not in df_results.columns:
            self.logger.warning(f"No results or metric '{metric}' not found.")
            return {}

        best_row = df_results.loc[df_results[metric].idxmax()]
        best_params = best_row.to_dict()
        self.logger.info(f"Best Params by {metric}: {best_params}")
        return best_params
