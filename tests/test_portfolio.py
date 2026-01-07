"""Unit tests for Portfolio class."""

import pytest
from datetime import datetime
from src.core.portfolio import Portfolio


def test_portfolio_initialization():
    """Test portfolio initialization."""
    portfolio = Portfolio(initial_cash=100000, transaction_cost_pct=0.001)
    assert portfolio.cash == 100000
    assert portfolio.initial_cash == 100000
    assert portfolio.transaction_cost_pct == 0.001
    assert len(portfolio.positions) == 0
    assert len(portfolio.trades) == 0


def test_portfolio_invalid_initialization():
    """Test portfolio initialization with invalid values."""
    with pytest.raises(ValueError):
        Portfolio(initial_cash=-1000)

    with pytest.raises(ValueError):
        Portfolio(initial_cash=100000, transaction_cost_pct=-0.1)


def test_buy_stock():
    """Test buying stock."""
    portfolio = Portfolio(initial_cash=100000, transaction_cost_pct=0.001)
    date = datetime(2020, 1, 1)

    success = portfolio.buy("AAPL", 100, 150.0, date)

    assert success is True
    assert portfolio.get_position("AAPL") == 100
    assert portfolio.cash == 100000 - (100 * 150.0 * 1.001)  # Cost + transaction cost
    assert len(portfolio.trades) == 1
    assert portfolio.trades[0]["action"] == "buy"
    assert portfolio.trades[0]["ticker"] == "AAPL"


def test_buy_insufficient_funds():
    """Test buying with insufficient funds."""
    portfolio = Portfolio(initial_cash=1000, transaction_cost_pct=0.001)
    date = datetime(2020, 1, 1)

    success = portfolio.buy("AAPL", 100, 150.0, date)

    assert success is False
    assert portfolio.get_position("AAPL") == 0
    assert portfolio.cash == 1000  # Unchanged
    assert len(portfolio.trades) == 0


def test_sell_stock():
    """Test selling stock."""
    portfolio = Portfolio(initial_cash=100000, transaction_cost_pct=0.001)
    buy_date = datetime(2020, 1, 1)
    sell_date = datetime(2020, 2, 1)

    # First buy
    portfolio.buy("AAPL", 100, 150.0, buy_date)
    cash_after_buy = portfolio.cash

    # Then sell
    success = portfolio.sell("AAPL", 100, 160.0, sell_date)

    assert success is True
    assert portfolio.get_position("AAPL") == 0
    expected_proceeds = 100 * 160.0 * (1 - 0.001)
    assert portfolio.cash == cash_after_buy + expected_proceeds
    assert len(portfolio.trades) == 2
    assert portfolio.trades[1]["action"] == "sell"


def test_sell_insufficient_shares():
    """Test selling more shares than owned."""
    portfolio = Portfolio(initial_cash=100000, transaction_cost_pct=0.001)
    date = datetime(2020, 1, 1)

    # Buy 50 shares
    portfolio.buy("AAPL", 50, 150.0, date)

    # Try to sell 100 shares
    success = portfolio.sell("AAPL", 100, 160.0, date)

    assert success is False
    assert portfolio.get_position("AAPL") == 50  # Unchanged
    assert len(portfolio.trades) == 1  # Only buy trade


def test_portfolio_value():
    """Test portfolio value calculation."""
    portfolio = Portfolio(initial_cash=100000, transaction_cost_pct=0.001)
    date = datetime(2020, 1, 1)

    # Buy stocks
    portfolio.buy("AAPL", 100, 150.0, date)
    portfolio.buy("MSFT", 50, 200.0, date)

    # Calculate portfolio value
    current_prices = {"AAPL": 160.0, "MSFT": 210.0}
    portfolio_value = portfolio.get_portfolio_value(current_prices)

    expected_value = portfolio.cash + (100 * 160.0) + (50 * 210.0)
    assert abs(portfolio_value - expected_value) < 0.01


def test_multiple_positions():
    """Test managing multiple positions."""
    portfolio = Portfolio(initial_cash=100000, transaction_cost_pct=0.001)
    date = datetime(2020, 1, 1)

    # Buy multiple stocks
    portfolio.buy("AAPL", 100, 150.0, date)
    portfolio.buy("MSFT", 50, 200.0, date)
    portfolio.buy("GOOGL", 25, 1000.0, date)

    assert portfolio.get_position("AAPL") == 100
    assert portfolio.get_position("MSFT") == 50
    assert portfolio.get_position("GOOGL") == 25
    assert len(portfolio.positions) == 3


def test_trade_history():
    """Test trade history tracking."""
    portfolio = Portfolio(initial_cash=100000, transaction_cost_pct=0.001)

    portfolio.buy("AAPL", 100, 150.0, datetime(2020, 1, 1))
    portfolio.sell("AAPL", 50, 160.0, datetime(2020, 2, 1))

    history = portfolio.get_trade_history()

    assert len(history) == 2
    assert history[0]["action"] == "buy"
    assert history[0]["shares"] == 100
    assert history[1]["action"] == "sell"
    assert history[1]["shares"] == 50
