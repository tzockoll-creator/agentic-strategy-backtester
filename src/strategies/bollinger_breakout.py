"""Bollinger Band Breakout strategy."""

from datetime import datetime
from typing import Dict
import pandas as pd
import numpy as np

from src.strategies.base import Strategy


class BollingerBandBreakout(Strategy):
    """
    Bollinger Band Breakout strategy.

    Generates buy signals when price breaks above upper band.
    Generates sell signals when price breaks below lower band.
    """

    def __init__(self, period: int = 20, num_std: float = 2.0):
        """
        Initialize Bollinger Band Breakout strategy.

        Args:
            period: Period for moving average and standard deviation
            num_std: Number of standard deviations for bands
        """
        if period < 2:
            raise ValueError("Period must be at least 2")
        if num_std <= 0:
            raise ValueError("Number of standard deviations must be positive")

        super().__init__({
            "period": period,
            "num_std": num_std,
        })
        self.period = period
        self.num_std = num_std

    @property
    def name(self) -> str:
        """Return strategy name."""
        return f"Bollinger_Breakout_{self.period}_{self.num_std}"

    def _calculate_bollinger_bands(self, prices: pd.Series) -> tuple:
        """
        Calculate Bollinger Bands.

        Args:
            prices: Series of prices

        Returns:
            Tuple of (middle_band, upper_band, lower_band)
        """
        # Middle band is simple moving average
        middle_band = prices.rolling(window=self.period).mean()

        # Calculate standard deviation
        std = prices.rolling(window=self.period).std()

        # Upper and lower bands
        upper_band = middle_band + (self.num_std * std)
        lower_band = middle_band - (self.num_std * std)

        return middle_band, upper_band, lower_band

    def generate_signals(
        self,
        data: pd.DataFrame,
        current_date: datetime,
    ) -> Dict[str, str]:
        """
        Generate trading signals based on Bollinger Band breakouts.

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

                # Need enough data for Bollinger Bands
                if len(close_prices) < self.period:
                    signals[ticker] = "hold"
                    continue

                # Calculate Bollinger Bands
                middle_band, upper_band, lower_band = self._calculate_bollinger_bands(close_prices)

                # Get current values
                current_price = close_prices.iloc[-1]
                current_upper = upper_band.iloc[-1]
                current_lower = lower_band.iloc[-1]
                prev_price = close_prices.iloc[-2] if len(close_prices) >= 2 else current_price
                prev_upper = upper_band.iloc[-2] if len(upper_band) >= 2 else current_upper
                prev_lower = lower_band.iloc[-2] if len(lower_band) >= 2 else current_lower

                # Check for NaN values
                if pd.isna(current_upper) or pd.isna(current_lower):
                    signals[ticker] = "hold"
                    continue

                # Check for breakouts
                if prev_price <= prev_upper and current_price > current_upper:
                    # Price broke above upper band: buy signal (momentum breakout)
                    signals[ticker] = "buy"
                elif prev_price >= prev_lower and current_price < current_lower:
                    # Price broke below lower band: sell signal
                    signals[ticker] = "sell"
                else:
                    # No breakout: hold
                    signals[ticker] = "hold"

            except (KeyError, IndexError) as e:
                # If data is not available, hold
                signals[ticker] = "hold"

        return signals
