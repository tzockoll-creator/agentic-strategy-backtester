"""Unit tests for performance metrics calculations."""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.core.metrics import (
    calculate_total_return,
    calculate_cagr,
    calculate_sharpe_ratio,
    calculate_max_drawdown,
    calculate_win_rate,
    calculate_volatility,
)


def test_total_return():
    """Test total return calculation."""
    # Simple doubling
    equity = pd.Series([100, 150, 200])
    total_return = calculate_total_return(equity)
    assert abs(total_return - 1.0) < 0.001  # 100% return

    # 50% gain
    equity = pd.Series([100, 120, 150])
    total_return = calculate_total_return(equity)
    assert abs(total_return - 0.5) < 0.001  # 50% return

    # Loss
    equity = pd.Series([100, 80, 75])
    total_return = calculate_total_return(equity)
    assert abs(total_return - (-0.25)) < 0.001  # -25% return


def test_cagr():
    """Test CAGR calculation."""
    # Create 252 trading days (1 year) with 10% total return
    dates = pd.date_range(start="2020-01-01", periods=252, freq="D")
    equity = pd.Series([100 * (1.1 ** (i / 251)) for i in range(252)], index=dates)

    cagr = calculate_cagr(equity, annual_periods=252)
    assert abs(cagr - 0.10) < 0.01  # Should be approximately 10%


def test_volatility():
    """Test volatility calculation."""
    # Create series with known standard deviation
    np.random.seed(42)
    returns = np.random.normal(0.001, 0.02, 252)  # Daily returns
    equity = pd.Series(100 * np.cumprod(1 + returns))

    volatility = calculate_volatility(equity, annual_periods=252)

    # Volatility should be approximately 0.02 * sqrt(252) ≈ 0.317
    assert 0.25 < volatility < 0.40


def test_sharpe_ratio():
    """Test Sharpe ratio calculation."""
    # Create series with positive returns
    dates = pd.date_range(start="2020-01-01", periods=252, freq="D")

    # Constant 10% annual return, low volatility
    daily_return = 0.10 / 252
    equity = pd.Series([100 * (1 + daily_return) ** i for i in range(252)], index=dates)

    sharpe = calculate_sharpe_ratio(equity, risk_free_rate=0.02, annual_periods=252)

    # Should have positive Sharpe ratio (returns > risk-free rate)
    assert sharpe > 0


def test_max_drawdown():
    """Test maximum drawdown calculation."""
    # Create series with known drawdown
    equity = pd.Series([100, 120, 150, 120, 100, 110, 105])  # Peak at 150, trough at 100

    max_dd = calculate_max_drawdown(equity)

    # Drawdown from 150 to 100 is 33.33%
    assert abs(max_dd - 0.3333) < 0.01

    # No drawdown case
    equity_up = pd.Series([100, 110, 120, 130, 140])
    max_dd_up = calculate_max_drawdown(equity_up)
    assert max_dd_up == 0.0


def test_win_rate():
    """Test win rate calculation."""
    # Create trades with known win rate
    trades = [
        {"ticker": "AAPL", "action": "buy", "shares": 10, "price": 100, "date": datetime(2020, 1, 1)},
        {"ticker": "AAPL", "action": "sell", "shares": 10, "price": 110, "date": datetime(2020, 2, 1)},  # Win
        {"ticker": "MSFT", "action": "buy", "shares": 5, "price": 200, "date": datetime(2020, 3, 1)},
        {"ticker": "MSFT", "action": "sell", "shares": 5, "price": 190, "date": datetime(2020, 4, 1)},  # Loss
        {"ticker": "GOOGL", "action": "buy", "shares": 2, "price": 1000, "date": datetime(2020, 5, 1)},
        {"ticker": "GOOGL", "action": "sell", "shares": 2, "price": 1100, "date": datetime(2020, 6, 1)},  # Win
    ]

    win_rate = calculate_win_rate(trades)

    # 2 wins out of 3 trades = 66.67%
    assert abs(win_rate - 0.6667) < 0.01


def test_win_rate_no_trades():
    """Test win rate with no completed trades."""
    trades = []
    win_rate = calculate_win_rate(trades)
    assert win_rate == 0.0

    # Only buy trades, no sells
    trades_buy_only = [
        {"ticker": "AAPL", "action": "buy", "shares": 10, "price": 100, "date": datetime(2020, 1, 1)},
    ]
    win_rate = calculate_win_rate(trades_buy_only)
    assert win_rate == 0.0


def test_empty_series():
    """Test metrics with empty series."""
    empty = pd.Series([])

    assert calculate_total_return(empty) == 0.0
    assert calculate_cagr(empty) == 0.0
    assert calculate_sharpe_ratio(empty) == 0.0
    assert calculate_max_drawdown(empty) == 0.0
    assert calculate_volatility(empty) == 0.0


def test_single_value_series():
    """Test metrics with single value series."""
    single = pd.Series([100])

    # Most metrics should handle single-value series gracefully
    assert calculate_cagr(single) == 0.0
    assert calculate_sharpe_ratio(single) == 0.0
    assert calculate_volatility(single) == 0.0
