"""Strategy factory for generating and testing parameter variations."""

from typing import List, Dict, Type
import pandas as pd
from itertools import product
import random

from src.strategies.base import Strategy
from src.strategies.ma_crossover import MovingAverageCrossover
from src.strategies.rsi_reversion import RSIMeanReversion
from src.strategies.bollinger_breakout import BollingerBandBreakout
from src.core.backtest_engine import BacktestEngine, BacktestResult


# Predefined parameter grids for each strategy
MA_CROSSOVER_PARAMS = {
    "fast_period": [10, 20, 30, 50],
    "slow_period": [50, 100, 150, 200],
}

RSI_REVERSION_PARAMS = {
    "rsi_period": [7, 14, 21, 28],
    "oversold": [20, 25, 30, 35],
    "overbought": [65, 70, 75, 80],
}

BOLLINGER_BREAKOUT_PARAMS = {
    "period": [10, 20, 30, 40, 50],
    "num_std": [1.5, 2.0, 2.5, 3.0],
}


class StrategyFactory:
    """Factory for generating strategy variations and running parameter sweeps."""

    def __init__(self, initial_cash: float = 100000.0, transaction_cost_pct: float = 0.001):
        """
        Initialize strategy factory.

        Args:
            initial_cash: Initial cash for backtests
            transaction_cost_pct: Transaction cost percentage
        """
        self.initial_cash = initial_cash
        self.transaction_cost_pct = transaction_cost_pct
        self.engine = BacktestEngine(initial_cash, transaction_cost_pct)

    def generate_strategy_variations(
        self,
        strategy_class: Type[Strategy],
        param_grid: Dict = None,
        max_variations: int = 10,
    ) -> List[Strategy]:
        """
        Generate parameter variations for a strategy.

        Args:
            strategy_class: Strategy class to generate variations for
            param_grid: Dictionary of parameter -> list of values
            max_variations: Maximum number of variations to generate

        Returns:
            List of strategy instances with different parameters
        """
        # Use default param grid if not provided
        if param_grid is None:
            param_grid = self._get_default_param_grid(strategy_class)

        # Generate all combinations of parameters
        param_names = list(param_grid.keys())
        param_values = list(param_grid.values())
        all_combinations = list(product(*param_values))

        # Limit to max_variations
        if len(all_combinations) > max_variations:
            # Randomly sample if too many combinations
            all_combinations = random.sample(all_combinations, max_variations)

        # Create strategy instances
        strategies = []
        for combination in all_combinations:
            params = dict(zip(param_names, combination))

            try:
                # Special validation for MA Crossover
                if strategy_class == MovingAverageCrossover:
                    if params["fast_period"] >= params["slow_period"]:
                        continue  # Skip invalid combinations

                # Special validation for RSI
                if strategy_class == RSIMeanReversion:
                    if params["oversold"] >= params["overbought"]:
                        continue  # Skip invalid combinations

                strategy = strategy_class(**params)
                strategies.append(strategy)
            except (ValueError, TypeError):
                # Skip invalid parameter combinations
                continue

        return strategies

    def _get_default_param_grid(self, strategy_class: Type[Strategy]) -> Dict:
        """Get default parameter grid for a strategy class."""
        if strategy_class == MovingAverageCrossover:
            return MA_CROSSOVER_PARAMS
        elif strategy_class == RSIMeanReversion:
            return RSI_REVERSION_PARAMS
        elif strategy_class == BollingerBandBreakout:
            return BOLLINGER_BREAKOUT_PARAMS
        else:
            raise ValueError(f"No default parameter grid for {strategy_class.__name__}")

    def run_strategy_sweep(
        self,
        strategy_class: Type[Strategy],
        tickers: List[str],
        start_date: str,
        end_date: str,
        param_grid: Dict = None,
        max_variations: int = 10,
        rank_by: str = "sharpe_ratio",
    ) -> pd.DataFrame:
        """
        Run backtests for all strategy variations and rank them.

        Args:
            strategy_class: Strategy class to test
            tickers: List of tickers to trade
            start_date: Start date for backtest
            end_date: End date for backtest
            param_grid: Parameter grid (uses default if None)
            max_variations: Maximum number of variations to test
            rank_by: Metric to rank strategies by

        Returns:
            DataFrame with results sorted by ranking metric
        """
        print(f"\n{'=' * 70}")
        print(f"Running strategy sweep for {strategy_class.__name__}")
        print(f"{'=' * 70}")

        # Generate strategy variations
        strategies = self.generate_strategy_variations(
            strategy_class, param_grid, max_variations
        )

        print(f"Generated {len(strategies)} strategy variations")

        # Run backtests for all variations
        results = self.engine.run_multiple_backtests(
            strategies, tickers, start_date, end_date
        )

        # Create comparison DataFrame
        comparison_data = []
        for result in results:
            row = {
                "strategy": result.strategy_name,
                **result.parameters,
                **result.metrics,
            }
            comparison_data.append(row)

        df = pd.DataFrame(comparison_data)

        # Sort by ranking metric (descending for most metrics, ascending for drawdown)
        ascending = rank_by in ["max_drawdown", "volatility"]
        df = df.sort_values(by=rank_by, ascending=ascending)

        print(f"\n{'=' * 70}")
        print(f"Strategy Sweep Complete - Ranked by {rank_by}")
        print(f"{'=' * 70}\n")

        return df

    def run_all_strategies_sweep(
        self,
        tickers: List[str],
        start_date: str,
        end_date: str,
        max_variations_per_strategy: int = 10,
        rank_by: str = "sharpe_ratio",
    ) -> pd.DataFrame:
        """
        Run parameter sweeps for all strategy types.

        Args:
            tickers: List of tickers to trade
            start_date: Start date for backtest
            end_date: End date for backtest
            max_variations_per_strategy: Max variations per strategy type
            rank_by: Metric to rank by

        Returns:
            Combined DataFrame with all results
        """
        all_results = []

        strategy_classes = [
            MovingAverageCrossover,
            RSIMeanReversion,
            BollingerBandBreakout,
        ]

        for strategy_class in strategy_classes:
            df = self.run_strategy_sweep(
                strategy_class,
                tickers,
                start_date,
                end_date,
                max_variations=max_variations_per_strategy,
                rank_by=rank_by,
            )
            all_results.append(df)

        # Combine all results
        combined_df = pd.concat(all_results, ignore_index=True)

        # Sort by ranking metric
        ascending = rank_by in ["max_drawdown", "volatility"]
        combined_df = combined_df.sort_values(by=rank_by, ascending=ascending)

        return combined_df
