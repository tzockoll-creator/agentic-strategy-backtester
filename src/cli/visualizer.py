"""Visualization utilities for backtest results."""

import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
from typing import Optional
from datetime import datetime

from src.core.backtest_engine import BacktestResult
from src.core.metrics import calculate_drawdown_series


def plot_equity_curve(
    backtest_result: BacktestResult,
    benchmark: Optional[pd.Series] = None,
    save_path: Optional[str] = None,
    show: bool = True,
):
    """
    Plot equity curve showing portfolio value over time.

    Args:
        backtest_result: Backtest result object
        benchmark: Optional benchmark series (e.g., buy-and-hold SPY)
        save_path: Path to save plot (optional)
        show: Whether to display plot
    """
    fig, ax = plt.subplots(figsize=(12, 6))

    # Plot strategy equity curve
    equity = backtest_result.equity_curve
    ax.plot(equity.index, equity.values, label=backtest_result.strategy_name, linewidth=2)

    # Plot benchmark if provided
    if benchmark is not None:
        # Normalize benchmark to start at same value as strategy
        normalized_benchmark = benchmark * (equity.iloc[0] / benchmark.iloc[0])
        ax.plot(
            normalized_benchmark.index,
            normalized_benchmark.values,
            label="Buy & Hold",
            linewidth=2,
            alpha=0.7,
            linestyle="--",
        )

    # Formatting
    ax.set_xlabel("Date", fontsize=12)
    ax.set_ylabel("Portfolio Value ($)", fontsize=12)
    ax.set_title(
        f"Equity Curve: {backtest_result.strategy_name}\n"
        f"Total Return: {backtest_result.metrics['total_return']:.2%} | "
        f"Sharpe: {backtest_result.metrics['sharpe_ratio']:.2f} | "
        f"Max DD: {backtest_result.metrics['max_drawdown']:.2%}",
        fontsize=14,
        fontweight="bold",
    )
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    plt.xticks(rotation=45)

    # Add initial and final value annotations
    ax.axhline(
        y=backtest_result.initial_cash,
        color="gray",
        linestyle=":",
        alpha=0.5,
        label="Initial Value",
    )

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"Equity curve saved to {save_path}")

    if show:
        plt.show()
    else:
        plt.close()


def plot_drawdown(
    backtest_result: BacktestResult,
    save_path: Optional[str] = None,
    show: bool = True,
):
    """
    Plot drawdown chart (underwater plot).

    Args:
        backtest_result: Backtest result object
        save_path: Path to save plot (optional)
        show: Whether to display plot
    """
    fig, ax = plt.subplots(figsize=(12, 6))

    # Calculate drawdown series
    drawdown = calculate_drawdown_series(backtest_result.equity_curve)

    # Plot as area chart
    ax.fill_between(
        drawdown.index,
        drawdown.values * 100,
        0,
        color="red",
        alpha=0.3,
        label="Drawdown",
    )
    ax.plot(drawdown.index, drawdown.values * 100, color="darkred", linewidth=1.5)

    # Formatting
    ax.set_xlabel("Date", fontsize=12)
    ax.set_ylabel("Drawdown (%)", fontsize=12)
    ax.set_title(
        f"Drawdown Chart: {backtest_result.strategy_name}\n"
        f"Maximum Drawdown: {backtest_result.metrics['max_drawdown']:.2%}",
        fontsize=14,
        fontweight="bold",
    )
    ax.grid(True, alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    plt.xticks(rotation=45)

    # Set y-axis to show negative values
    ax.set_ylim([drawdown.min() * 100 * 1.1, 5])

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"Drawdown chart saved to {save_path}")

    if show:
        plt.show()
    else:
        plt.close()


def plot_returns_distribution(
    backtest_result: BacktestResult,
    save_path: Optional[str] = None,
    show: bool = True,
):
    """
    Plot distribution of daily returns.

    Args:
        backtest_result: Backtest result object
        save_path: Path to save plot (optional)
        show: Whether to display plot
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    # Calculate daily returns
    returns = backtest_result.equity_curve.pct_change().dropna() * 100

    # Plot histogram
    ax.hist(returns, bins=50, alpha=0.7, color="steelblue", edgecolor="black")

    # Add vertical lines for mean and zero
    ax.axvline(returns.mean(), color="red", linestyle="--", linewidth=2, label=f"Mean: {returns.mean():.3f}%")
    ax.axvline(0, color="black", linestyle="-", linewidth=1, alpha=0.5)

    # Formatting
    ax.set_xlabel("Daily Return (%)", fontsize=12)
    ax.set_ylabel("Frequency", fontsize=12)
    ax.set_title(
        f"Returns Distribution: {backtest_result.strategy_name}\n"
        f"Mean: {returns.mean():.3f}% | Std: {returns.std():.3f}%",
        fontsize=14,
        fontweight="bold",
    )
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3, axis="y")

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"Returns distribution saved to {save_path}")

    if show:
        plt.show()
    else:
        plt.close()


def save_plots(
    backtest_result: BacktestResult,
    output_dir: str = "results",
    benchmark: Optional[pd.Series] = None,
):
    """
    Save all plots for a backtest result.

    Args:
        backtest_result: Backtest result object
        output_dir: Directory to save plots
        benchmark: Optional benchmark series
    """
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Generate timestamp for unique filenames
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    strategy_name = backtest_result.strategy_name.replace(" ", "_")

    # Save equity curve
    equity_path = os.path.join(output_dir, f"{strategy_name}_{timestamp}_equity.png")
    plot_equity_curve(backtest_result, benchmark, equity_path, show=False)

    # Save drawdown chart
    drawdown_path = os.path.join(output_dir, f"{strategy_name}_{timestamp}_drawdown.png")
    plot_drawdown(backtest_result, drawdown_path, show=False)

    # Save returns distribution
    returns_path = os.path.join(output_dir, f"{strategy_name}_{timestamp}_returns.png")
    plot_returns_distribution(backtest_result, returns_path, show=False)

    print(f"\nAll plots saved to {output_dir}/")


def plot_comparison(
    results: list[BacktestResult],
    metric: str = "equity_curve",
    save_path: Optional[str] = None,
    show: bool = True,
):
    """
    Plot comparison of multiple strategies.

    Args:
        results: List of BacktestResult objects
        metric: Metric to compare ('equity_curve' or 'drawdown')
        save_path: Path to save plot
        show: Whether to display plot
    """
    fig, ax = plt.subplots(figsize=(14, 7))

    for result in results:
        if metric == "equity_curve":
            # Normalize to start at 100
            normalized = (result.equity_curve / result.equity_curve.iloc[0]) * 100
            ax.plot(normalized.index, normalized.values, label=result.strategy_name, linewidth=2)
        elif metric == "drawdown":
            drawdown = calculate_drawdown_series(result.equity_curve) * 100
            ax.plot(drawdown.index, drawdown.values, label=result.strategy_name, linewidth=2)

    # Formatting
    if metric == "equity_curve":
        ax.set_ylabel("Portfolio Value (Normalized to 100)", fontsize=12)
        ax.set_title("Strategy Comparison - Equity Curves", fontsize=14, fontweight="bold")
    else:
        ax.set_ylabel("Drawdown (%)", fontsize=12)
        ax.set_title("Strategy Comparison - Drawdowns", fontsize=14, fontweight="bold")

    ax.set_xlabel("Date", fontsize=12)
    ax.legend(fontsize=9, loc="best")
    ax.grid(True, alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    plt.xticks(rotation=45)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"Comparison plot saved to {save_path}")

    if show:
        plt.show()
    else:
        plt.close()
