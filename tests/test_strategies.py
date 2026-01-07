"""Unit tests for trading strategies."""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from src.strategies.ma_crossover import MovingAverageCrossover
from src.strategies.rsi_reversion import RSIMeanReversion
from src.strategies.bollinger_breakout import BollingerBandBreakout


def create_sample_data(ticker="SPY", periods=100, start_price=100):
    """Create sample OHLCV data for testing."""
    dates = pd.date_range(start="2020-01-01", periods=periods, freq="D")

    # Create synthetic price data with slight upward trend
    np.random.seed(42)
    returns = np.random.normal(0.001, 0.02, periods)
    closes = start_price * np.cumprod(1 + returns)

    data = pd.DataFrame({
        (ticker, "Open"): closes * 0.99,
        (ticker, "High"): closes * 1.01,
        (ticker, "Low"): closes * 0.98,
        (ticker, "Close"): closes,
        (ticker, "Volume"): np.random.randint(1000000, 10000000, periods),
    }, index=dates)

    return data


class TestMovingAverageCrossover:
    """Tests for MA Crossover strategy."""

    def test_initialization(self):
        """Test strategy initialization."""
        strategy = MovingAverageCrossover(fast_period=20, slow_period=50)
        assert strategy.fast_period == 20
        assert strategy.slow_period == 50
        assert strategy.name == "MA_Crossover_20_50"

    def test_invalid_parameters(self):
        """Test that invalid parameters raise errors."""
        with pytest.raises(ValueError):
            MovingAverageCrossover(fast_period=50, slow_period=20)  # Fast > Slow

    def test_signal_generation(self):
        """Test signal generation."""
        strategy = MovingAverageCrossover(fast_period=10, slow_period=20)
        data = create_sample_data(periods=100)

        signals = strategy.generate_signals(data, datetime(2020, 4, 9))

        assert "SPY" in signals
        assert signals["SPY"] in ["buy", "sell", "hold"]

    def test_insufficient_data(self):
        """Test behavior with insufficient data."""
        strategy = MovingAverageCrossover(fast_period=20, slow_period=50)
        data = create_sample_data(periods=30)  # Less than slow_period

        signals = strategy.generate_signals(data, datetime(2020, 1, 31))

        assert signals["SPY"] == "hold"  # Should hold when not enough data


class TestRSIMeanReversion:
    """Tests for RSI Mean Reversion strategy."""

    def test_initialization(self):
        """Test strategy initialization."""
        strategy = RSIMeanReversion(rsi_period=14, oversold=30, overbought=70)
        assert strategy.rsi_period == 14
        assert strategy.oversold == 30
        assert strategy.overbought == 70
        assert "RSI_Reversion" in strategy.name

    def test_invalid_parameters(self):
        """Test that invalid parameters raise errors."""
        with pytest.raises(ValueError):
            RSIMeanReversion(rsi_period=14, oversold=80, overbought=70)  # Oversold > Overbought

        with pytest.raises(ValueError):
            RSIMeanReversion(rsi_period=14, oversold=-10, overbought=70)  # Negative

    def test_rsi_calculation(self):
        """Test RSI calculation."""
        strategy = RSIMeanReversion(rsi_period=14, oversold=30, overbought=70)

        # Create data with clear trend
        dates = pd.date_range(start="2020-01-01", periods=50, freq="D")
        # Uptrend data
        closes = pd.Series([100 + i for i in range(50)], index=dates)

        rsi = strategy._calculate_rsi(closes)

        # RSI should be between 0 and 100
        assert rsi.dropna().min() >= 0
        assert rsi.dropna().max() <= 100

        # In strong uptrend, RSI should be relatively high
        assert rsi.iloc[-1] > 50

    def test_signal_generation(self):
        """Test signal generation."""
        strategy = RSIMeanReversion(rsi_period=14, oversold=30, overbought=70)
        data = create_sample_data(periods=100)

        signals = strategy.generate_signals(data, datetime(2020, 4, 9))

        assert "SPY" in signals
        assert signals["SPY"] in ["buy", "sell", "hold"]


class TestBollingerBandBreakout:
    """Tests for Bollinger Band Breakout strategy."""

    def test_initialization(self):
        """Test strategy initialization."""
        strategy = BollingerBandBreakout(period=20, num_std=2.0)
        assert strategy.period == 20
        assert strategy.num_std == 2.0
        assert "Bollinger_Breakout" in strategy.name

    def test_invalid_parameters(self):
        """Test that invalid parameters raise errors."""
        with pytest.raises(ValueError):
            BollingerBandBreakout(period=1, num_std=2.0)  # Period too small

        with pytest.raises(ValueError):
            BollingerBandBreakout(period=20, num_std=-1.0)  # Negative std

    def test_bollinger_bands_calculation(self):
        """Test Bollinger Bands calculation."""
        strategy = BollingerBandBreakout(period=20, num_std=2.0)

        # Create simple data
        dates = pd.date_range(start="2020-01-01", periods=50, freq="D")
        closes = pd.Series([100] * 50, index=dates)  # Flat prices

        middle, upper, lower = strategy._calculate_bollinger_bands(closes)

        # With flat prices, std should be 0, so bands should converge to middle
        assert abs(middle.iloc[-1] - 100) < 0.01
        assert abs(upper.iloc[-1] - lower.iloc[-1]) < 0.01  # Bands should be tight

    def test_signal_generation(self):
        """Test signal generation."""
        strategy = BollingerBandBreakout(period=20, num_std=2.0)
        data = create_sample_data(periods=100)

        signals = strategy.generate_signals(data, datetime(2020, 4, 9))

        assert "SPY" in signals
        assert signals["SPY"] in ["buy", "sell", "hold"]

    def test_multiple_tickers(self):
        """Test signal generation with multiple tickers."""
        strategy = BollingerBandBreakout(period=20, num_std=2.0)

        # Create data for multiple tickers
        dates = pd.date_range(start="2020-01-01", periods=100, freq="D")
        np.random.seed(42)

        data = pd.DataFrame({
            ("SPY", "Close"): 100 * np.cumprod(1 + np.random.normal(0.001, 0.02, 100)),
            ("AAPL", "Close"): 150 * np.cumprod(1 + np.random.normal(0.001, 0.02, 100)),
        }, index=dates)

        signals = strategy.generate_signals(data, datetime(2020, 4, 9))

        assert "SPY" in signals
        assert "AAPL" in signals
        assert len(signals) == 2
