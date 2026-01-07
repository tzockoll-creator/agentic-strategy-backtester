"""Performance metrics calculations for backtesting."""

import numpy as np
import pandas as pd
from typing import List, Dict


def calculate_total_return(equity_curve: pd.Series) -> float:
    """
    Calculate total return.

    Args:
        equity_curve: Series of portfolio values over time

    Returns:
        Total return as decimal (e.g., 0.25 for 25% return)
    """
    if len(equity_curve) == 0:
        return 0.0

    initial_value = equity_curve.iloc[0]
    final_value = equity_curve.iloc[-1]

    if initial_value == 0:
        return 0.0

    return (final_value - initial_value) / initial_value


def calculate_cagr(equity_curve: pd.Series, annual_periods: int = 252) -> float:
    """
    Calculate Compound Annual Growth Rate.

    Args:
        equity_curve: Series of portfolio values over time
        annual_periods: Number of periods per year (252 for daily)

    Returns:
        CAGR as decimal (e.g., 0.15 for 15% annual growth)
    """
    if len(equity_curve) < 2:
        return 0.0

    initial_value = equity_curve.iloc[0]
    final_value = equity_curve.iloc[-1]
    num_periods = len(equity_curve)

    if initial_value <= 0 or final_value <= 0:
        return 0.0

    years = num_periods / annual_periods
    if years == 0:
        return 0.0

    cagr = (final_value / initial_value) ** (1 / years) - 1
    return cagr


def calculate_volatility(equity_curve: pd.Series, annual_periods: int = 252) -> float:
    """
    Calculate annualized volatility.

    Args:
        equity_curve: Series of portfolio values over time
        annual_periods: Number of periods per year (252 for daily)

    Returns:
        Annualized volatility as decimal
    """
    if len(equity_curve) < 2:
        return 0.0

    returns = equity_curve.pct_change().dropna()
    if len(returns) == 0:
        return 0.0

    return returns.std() * np.sqrt(annual_periods)


def calculate_sharpe_ratio(
    equity_curve: pd.Series,
    risk_free_rate: float = 0.02,
    annual_periods: int = 252,
) -> float:
    """
    Calculate Sharpe ratio.

    Args:
        equity_curve: Series of portfolio values over time
        risk_free_rate: Annual risk-free rate (default 2%)
        annual_periods: Number of periods per year (252 for daily)

    Returns:
        Sharpe ratio
    """
    if len(equity_curve) < 2:
        return 0.0

    returns = equity_curve.pct_change().dropna()
    if len(returns) == 0:
        return 0.0

    # Convert annual risk-free rate to per-period rate
    period_risk_free_rate = risk_free_rate / annual_periods

    excess_returns = returns - period_risk_free_rate
    mean_excess_return = excess_returns.mean()
    std_excess_return = excess_returns.std()

    if std_excess_return == 0:
        return 0.0

    sharpe = (mean_excess_return / std_excess_return) * np.sqrt(annual_periods)
    return sharpe


def calculate_max_drawdown(equity_curve: pd.Series) -> float:
    """
    Calculate maximum drawdown.

    Args:
        equity_curve: Series of portfolio values over time

    Returns:
        Maximum drawdown as positive decimal (e.g., 0.20 for 20% drawdown)
    """
    if len(equity_curve) == 0:
        return 0.0

    # Calculate running maximum
    running_max = equity_curve.expanding().max()

    # Calculate drawdown at each point
    drawdown = (equity_curve - running_max) / running_max

    # Return the maximum drawdown as a positive number
    return abs(drawdown.min())


def calculate_drawdown_series(equity_curve: pd.Series) -> pd.Series:
    """
    Calculate drawdown series for plotting.

    Args:
        equity_curve: Series of portfolio values over time

    Returns:
        Series of drawdown values at each point in time
    """
    if len(equity_curve) == 0:
        return pd.Series()

    running_max = equity_curve.expanding().max()
    drawdown = (equity_curve - running_max) / running_max
    return drawdown


def calculate_win_rate(trades: List[Dict]) -> float:
    """
    Calculate win rate from trade history.

    Args:
        trades: List of trade dictionaries

    Returns:
        Win rate as decimal (e.g., 0.65 for 65% win rate)
    """
    if len(trades) == 0:
        return 0.0

    # Group trades into round trips (buy-sell pairs)
    positions = {}  # ticker -> list of (buy_price, shares, buy_date)
    completed_trades = []

    for trade in trades:
        ticker = trade["ticker"]
        action = trade["action"]

        if action == "buy":
            if ticker not in positions:
                positions[ticker] = []
            positions[ticker].append({
                "price": trade["price"],
                "shares": trade["shares"],
                "date": trade["date"],
            })
        elif action == "sell":
            if ticker not in positions or len(positions[ticker]) == 0:
                continue

            shares_to_sell = trade["shares"]
            sell_price = trade["price"]

            # FIFO: sell from oldest purchases first
            while shares_to_sell > 0 and positions[ticker]:
                buy = positions[ticker][0]
                shares_from_this_buy = min(shares_to_sell, buy["shares"])

                # Calculate profit/loss for this portion
                profit = (sell_price - buy["price"]) * shares_from_this_buy
                completed_trades.append({
                    "profit": profit,
                    "return": (sell_price - buy["price"]) / buy["price"],
                })

                shares_to_sell -= shares_from_this_buy
                buy["shares"] -= shares_from_this_buy

                if buy["shares"] == 0:
                    positions[ticker].pop(0)

    if len(completed_trades) == 0:
        return 0.0

    winning_trades = sum(1 for trade in completed_trades if trade["profit"] > 0)
    win_rate = winning_trades / len(completed_trades)

    return win_rate


def calculate_all_metrics(
    equity_curve: pd.Series,
    trades: List[Dict],
    risk_free_rate: float = 0.02,
    annual_periods: int = 252,
) -> Dict[str, float]:
    """
    Calculate all performance metrics at once.

    Args:
        equity_curve: Series of portfolio values over time
        trades: List of trade dictionaries
        risk_free_rate: Annual risk-free rate
        annual_periods: Number of periods per year

    Returns:
        Dictionary of all metrics
    """
    return {
        "total_return": calculate_total_return(equity_curve),
        "cagr": calculate_cagr(equity_curve, annual_periods),
        "sharpe_ratio": calculate_sharpe_ratio(equity_curve, risk_free_rate, annual_periods),
        "max_drawdown": calculate_max_drawdown(equity_curve),
        "volatility": calculate_volatility(equity_curve, annual_periods),
        "win_rate": calculate_win_rate(trades),
        "total_trades": len([t for t in trades if t["action"] == "sell"]),
        "initial_value": equity_curve.iloc[0] if len(equity_curve) > 0 else 0.0,
        "final_value": equity_curve.iloc[-1] if len(equity_curve) > 0 else 0.0,
    }
