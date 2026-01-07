"""Moving Average Crossover strategy."""

from datetime import datetime
from typing import Dict
import pandas as pd

from src.strategies.base import Strategy


class MovingAverageCrossover(Strategy):
    """
    Moving Average Crossover strategy.

    Generates buy signals when fast MA crosses above slow MA.
    Generates sell signals when fast MA crosses below slow MA.
    """

    def __init__(self, fast_period: int = 20, slow_period: int = 50):
        """
        Initialize MA Crossover strategy.

        Args:
            fast_period: Period for fast moving average
            slow_period: Period for slow moving average
        """
        if fast_period >= slow_period:
            raise ValueError("Fast period must be less than slow period")

        super().__init__({
            "fast_period": fast_period,
            "slow_period": slow_period,
        })
        self.fast_period = fast_period
        self.slow_period = slow_period

    @property
    def name(self) -> str:
        """Return strategy name."""
        return f"MA_Crossover_{self.fast_period}_{self.slow_period}"

    def generate_signals(
        self,
        data: pd.DataFrame,
        current_date: datetime,
    ) -> Dict[str, str]:
        """
        Generate trading signals based on MA crossover.

        Args:
            data: Historical OHLCV data
            current_date: Current date

        Returns:
            Dictionary of ticker -> signal
        """
        signals = {}

        # Get all tickers from MultiIndex columns
        tickers = data.columns.get_level_values(0).unique().tolist()

        for ticker in tickers:
            try:
                # Get close prices for this ticker
                close_prices = data[ticker]["Close"]

                # Need enough data for slow MA
                if len(close_prices) < self.slow_period:
                    signals[ticker] = "hold"
                    continue

                # Calculate moving averages
                fast_ma = close_prices.rolling(window=self.fast_period).mean()
                slow_ma = close_prices.rolling(window=self.slow_period).mean()

                # Get current and previous MA values
                current_fast = fast_ma.iloc[-1]
                current_slow = slow_ma.iloc[-1]
                prev_fast = fast_ma.iloc[-2] if len(fast_ma) >= 2 else current_fast
                prev_slow = slow_ma.iloc[-2] if len(slow_ma) >= 2 else current_slow

                # Check for crossover
                if pd.isna(current_fast) or pd.isna(current_slow):
                    signals[ticker] = "hold"
                elif prev_fast <= prev_slow and current_fast > current_slow:
                    # Bullish crossover: buy signal
                    signals[ticker] = "buy"
                elif prev_fast >= prev_slow and current_fast < current_slow:
                    # Bearish crossover: sell signal
                    signals[ticker] = "sell"
                else:
                    # No crossover: hold
                    signals[ticker] = "hold"

            except (KeyError, IndexError) as e:
                # If data is not available, hold
                signals[ticker] = "hold"

        return signals
