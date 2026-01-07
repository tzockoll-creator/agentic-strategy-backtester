"""Abstract base class for trading strategies."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict
import pandas as pd


class Strategy(ABC):
    """Abstract base class for all trading strategies."""

    def __init__(self, parameters: Dict):
        """
        Initialize strategy with parameters.

        Args:
            parameters: Dictionary of strategy-specific parameters
        """
        self.parameters = parameters

    @abstractmethod
    def generate_signals(
        self,
        data: pd.DataFrame,
        current_date: datetime,
    ) -> Dict[str, str]:
        """
        Generate trading signals for all tickers.

        Args:
            data: Historical OHLCV data up to current_date (MultiIndex: ticker, field)
            current_date: Current date for signal generation

        Returns:
            Dictionary mapping ticker -> signal ('buy', 'sell', or 'hold')
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the strategy name."""
        pass

    def __repr__(self) -> str:
        """String representation of the strategy."""
        params_str = ", ".join(f"{k}={v}" for k, v in self.parameters.items())
        return f"{self.name}({params_str})"
