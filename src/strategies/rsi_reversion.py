"""RSI Mean Reversion strategy."""

from datetime import datetime
from typing import Dict
import pandas as pd
import numpy as np

from src.strategies.base import Strategy


class RSIMeanReversion(Strategy):
    """
    RSI Mean Reversion strategy.

    Generates buy signals when RSI falls below oversold threshold.
    Generates sell signals when RSI rises above overbought threshold.
    """

    def __init__(
        self,
        rsi_period: int = 14,
        oversold: float = 30,
        overbought: float = 70,
    ):
        """
        Initialize RSI Mean Reversion strategy.

        Args:
            rsi_period: Period for RSI calculation
            oversold: Oversold threshold (buy signal)
            overbought: Overbought threshold (sell signal)
        """
        if not 0 < oversold < overbought < 100:
            raise ValueError("Must have 0 < oversold < overbought < 100")

        super().__init__({
            "rsi_period": rsi_period,
            "oversold": oversold,
            "overbought": overbought,
        })
        self.rsi_period = rsi_period
        self.oversold = oversold
        self.overbought = overbought

    @property
    def name(self) -> str:
        """Return strategy name."""
        return f"RSI_Reversion_{self.rsi_period}_{self.oversold}_{self.overbought}"

    def _calculate_rsi(self, prices: pd.Series) -> pd.Series:
        """
        Calculate RSI indicator.

        Args:
            prices: Series of prices

        Returns:
            Series of RSI values
        """
        # Calculate price changes
        delta = prices.diff()

        # Separate gains and losses
        gains = delta.where(delta > 0, 0)
        losses = -delta.where(delta < 0, 0)

        # Calculate average gains and losses
        avg_gains = gains.rolling(window=self.rsi_period).mean()
        avg_losses = losses.rolling(window=self.rsi_period).mean()

        # Calculate RS and RSI
        rs = avg_gains / avg_losses
        rsi = 100 - (100 / (1 + rs))

        return rsi

    def generate_signals(
        self,
        data: pd.DataFrame,
        current_date: datetime,
    ) -> Dict[str, str]:
        """
        Generate trading signals based on RSI.

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

                # Need enough data for RSI calculation
                if len(close_prices) < self.rsi_period + 1:
                    signals[ticker] = "hold"
                    continue

                # Calculate RSI
                rsi = self._calculate_rsi(close_prices)

                # Get current RSI value
                current_rsi = rsi.iloc[-1]

                # Generate signals
                if pd.isna(current_rsi):
                    signals[ticker] = "hold"
                elif current_rsi < self.oversold:
                    # Oversold: buy signal
                    signals[ticker] = "buy"
                elif current_rsi > self.overbought:
                    # Overbought: sell signal
                    signals[ticker] = "sell"
                else:
                    # Neutral zone: hold
                    signals[ticker] = "hold"

            except (KeyError, IndexError) as e:
                # If data is not available, hold
                signals[ticker] = "hold"

        return signals
