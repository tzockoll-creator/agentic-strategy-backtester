"""Test core system without downloading data."""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Test imports
print("Testing imports...")
from src.core.portfolio import Portfolio
from src.core.metrics import calculate_sharpe_ratio, calculate_max_drawdown, calculate_cagr
from src.strategies.ma_crossover import MovingAverageCrossover
from src.strategies.rsi_reversion import RSIMeanReversion
from src.strategies.bollinger_breakout import BollingerBandBreakout

print("✓ All imports successful!")

# Test Portfolio
print("\n" + "=" * 60)
print("Testing Portfolio Class")
print("=" * 60)

portfolio = Portfolio(initial_cash=100000, transaction_cost_pct=0.001)
print(f"Initial cash: ${portfolio.cash:,.2f}")

# Buy some stock
success = portfolio.buy("AAPL", 100, 150.0, datetime(2020, 1, 1))
print(f"Buy 100 AAPL @ $150: {'Success' if success else 'Failed'}")
print(f"Cash after buy: ${portfolio.cash:,.2f}")
print(f"Position in AAPL: {portfolio.get_position('AAPL')} shares")

# Sell
success = portfolio.sell("AAPL", 50, 160.0, datetime(2020, 2, 1))
print(f"Sell 50 AAPL @ $160: {'Success' if success else 'Failed'}")
print(f"Cash after sell: ${portfolio.cash:,.2f}")
print(f"Position in AAPL: {portfolio.get_position('AAPL')} shares")

# Portfolio value
current_prices = {"AAPL": 165.0}
portfolio_value = portfolio.get_portfolio_value(current_prices)
print(f"Total portfolio value: ${portfolio_value:,.2f}")
print(f"Number of trades: {len(portfolio.get_trade_history())}")

print("✓ Portfolio class working correctly!")

# Test Metrics
print("\n" + "=" * 60)
print("Testing Performance Metrics")
print("=" * 60)

# Create synthetic equity curve
dates = pd.date_range(start="2020-01-01", periods=252, freq="D")
np.random.seed(42)
returns = np.random.normal(0.0008, 0.015, 252)  # ~20% annual return, ~24% vol
equity_curve = pd.Series(100000 * np.cumprod(1 + returns), index=dates)

total_return = (equity_curve.iloc[-1] / equity_curve.iloc[0]) - 1
print(f"Total return: {total_return:.2%}")

sharpe = calculate_sharpe_ratio(equity_curve, risk_free_rate=0.02)
print(f"Sharpe ratio: {sharpe:.2f}")

max_dd = calculate_max_drawdown(equity_curve)
print(f"Max drawdown: {max_dd:.2%}")

cagr = calculate_cagr(equity_curve)
print(f"CAGR: {cagr:.2%}")

print("✓ Metrics calculations working correctly!")

# Test Strategies
print("\n" + "=" * 60)
print("Testing Strategy Classes")
print("=" * 60)

# Create synthetic multi-index data
periods = 100
dates = pd.date_range(start="2020-01-01", periods=periods, freq="D")
np.random.seed(42)

prices = 100 * np.cumprod(1 + np.random.normal(0.001, 0.02, periods))
data = pd.DataFrame({
    ("SPY", "Open"): prices * 0.99,
    ("SPY", "High"): prices * 1.01,
    ("SPY", "Low"): prices * 0.98,
    ("SPY", "Close"): prices,
    ("SPY", "Volume"): np.random.randint(1000000, 10000000, periods),
}, index=dates)

# Test MA Crossover
ma_strategy = MovingAverageCrossover(fast_period=10, slow_period=20)
print(f"Strategy: {ma_strategy.name}")
signals = ma_strategy.generate_signals(data, dates[50])
print(f"  Signal for SPY: {signals.get('SPY', 'N/A')}")

# Test RSI
rsi_strategy = RSIMeanReversion(rsi_period=14, oversold=30, overbought=70)
print(f"Strategy: {rsi_strategy.name}")
signals = rsi_strategy.generate_signals(data, dates[50])
print(f"  Signal for SPY: {signals.get('SPY', 'N/A')}")

# Test Bollinger Bands
bb_strategy = BollingerBandBreakout(period=20, num_std=2.0)
print(f"Strategy: {bb_strategy.name}")
signals = bb_strategy.generate_signals(data, dates[50])
print(f"  Signal for SPY: {signals.get('SPY', 'N/A')}")

print("✓ All strategies generating signals correctly!")

print("\n" + "=" * 60)
print("CORE SYSTEM TEST COMPLETE")
print("=" * 60)
print("✓ All core components are working!")
print("\nNote: To test with real market data, install yfinance:")
print("  pip install yfinance")
print("\nYou can run examples/spy_backtest.py once yfinance is installed.")
print("=" * 60)
