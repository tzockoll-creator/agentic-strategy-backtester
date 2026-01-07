"""Interactive command-line interface for backtesting."""

import questionary
import json
import os
from datetime import datetime
from tabulate import tabulate
import pandas as pd

from src.core.backtest_engine import BacktestEngine
from src.strategies.ma_crossover import MovingAverageCrossover
from src.strategies.rsi_reversion import RSIMeanReversion
from src.strategies.bollinger_breakout import BollingerBandBreakout
from src.factory.strategy_factory import StrategyFactory
from src.cli.visualizer import (
    plot_equity_curve,
    plot_drawdown,
    plot_returns_distribution,
    save_plots,
)


def export_to_json(backtest_result, output_dir="results"):
    """Export backtest result to JSON file."""
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    strategy_name = backtest_result.strategy_name.replace(" ", "_")
    filename = f"{strategy_name}_{timestamp}.json"
    filepath = os.path.join(output_dir, filename)

    # Convert to dict (with equity curve as list of [date, value] pairs)
    result_dict = {
        "strategy_name": backtest_result.strategy_name,
        "parameters": backtest_result.parameters,
        "metrics": backtest_result.metrics,
        "start_date": backtest_result.start_date,
        "end_date": backtest_result.end_date,
        "tickers": backtest_result.tickers,
        "initial_cash": backtest_result.initial_cash,
        "equity_curve": [
            {"date": str(date), "value": float(value)}
            for date, value in backtest_result.equity_curve.items()
        ],
        "trades": [
            {k: (str(v) if isinstance(v, datetime) else v) for k, v in trade.items()}
            for trade in backtest_result.trades
        ],
    }

    with open(filepath, "w") as f:
        json.dump(result_dict, f, indent=2)

    print(f"\nResults exported to {filepath}")
    return filepath


def display_metrics(backtest_result):
    """Display performance metrics in a formatted table."""
    metrics = backtest_result.metrics

    table_data = [
        ["Total Return", f"{metrics['total_return']:.2%}"],
        ["CAGR", f"{metrics['cagr']:.2%}"],
        ["Sharpe Ratio", f"{metrics['sharpe_ratio']:.2f}"],
        ["Max Drawdown", f"{metrics['max_drawdown']:.2%}"],
        ["Volatility", f"{metrics['volatility']:.2%}"],
        ["Win Rate", f"{metrics['win_rate']:.2%}"],
        ["Total Trades", f"{metrics['total_trades']:.0f}"],
        ["Initial Value", f"${metrics['initial_value']:,.2f}"],
        ["Final Value", f"${metrics['final_value']:,.2f}"],
    ]

    print("\n" + "=" * 50)
    print(f"Performance Metrics: {backtest_result.strategy_name}")
    print("=" * 50)
    print(tabulate(table_data, headers=["Metric", "Value"], tablefmt="grid"))
    print("=" * 50)


def run_single_strategy():
    """Run a single strategy backtest."""
    print("\n" + "=" * 60)
    print("SINGLE STRATEGY BACKTEST")
    print("=" * 60)

    # Strategy selection
    strategy_choice = questionary.select(
        "Select a strategy:",
        choices=[
            "Moving Average Crossover",
            "RSI Mean Reversion",
            "Bollinger Band Breakout",
        ],
    ).ask()

    # Get parameters based on strategy
    if strategy_choice == "Moving Average Crossover":
        fast_period = int(questionary.text("Fast MA period:", default="20").ask())
        slow_period = int(questionary.text("Slow MA period:", default="50").ask())
        strategy = MovingAverageCrossover(fast_period, slow_period)

    elif strategy_choice == "RSI Mean Reversion":
        rsi_period = int(questionary.text("RSI period:", default="14").ask())
        oversold = float(questionary.text("Oversold threshold:", default="30").ask())
        overbought = float(questionary.text("Overbought threshold:", default="70").ask())
        strategy = RSIMeanReversion(rsi_period, oversold, overbought)

    else:  # Bollinger Band Breakout
        period = int(questionary.text("Bollinger period:", default="20").ask())
        num_std = float(questionary.text("Number of std deviations:", default="2.0").ask())
        strategy = BollingerBandBreakout(period, num_std)

    # Get backtest configuration
    tickers_input = questionary.text(
        "Enter tickers (comma-separated):", default="SPY"
    ).ask()
    tickers = [t.strip().upper() for t in tickers_input.split(",")]

    start_date = questionary.text("Start date (YYYY-MM-DD):", default="2020-01-01").ask()
    end_date = questionary.text("End date (YYYY-MM-DD):", default="2024-12-31").ask()

    initial_cash = float(
        questionary.text("Initial cash:", default="100000").ask()
    )

    # Run backtest
    engine = BacktestEngine(initial_cash=initial_cash)
    result = engine.run_backtest(strategy, tickers, start_date, end_date)

    # Display results
    display_metrics(result)

    # Visualization options
    show_plots = questionary.confirm("Show plots?", default=True).ask()
    if show_plots:
        plot_equity_curve(result)
        plot_drawdown(result)

    # Export options
    export = questionary.confirm("Export results to JSON?", default=True).ask()
    if export:
        export_to_json(result)

    save_plots_choice = questionary.confirm("Save plots to files?", default=True).ask()
    if save_plots_choice:
        save_plots(result)


def run_strategy_sweep():
    """Run parameter sweep for a strategy."""
    print("\n" + "=" * 60)
    print("STRATEGY PARAMETER SWEEP")
    print("=" * 60)

    # Strategy selection
    strategy_choice = questionary.select(
        "Select a strategy:",
        choices=[
            "Moving Average Crossover",
            "RSI Mean Reversion",
            "Bollinger Band Breakout",
            "All Strategies",
        ],
    ).ask()

    # Map choice to class
    strategy_map = {
        "Moving Average Crossover": MovingAverageCrossover,
        "RSI Mean Reversion": RSIMeanReversion,
        "Bollinger Band Breakout": BollingerBandBreakout,
    }

    # Get backtest configuration
    tickers_input = questionary.text(
        "Enter tickers (comma-separated):", default="SPY"
    ).ask()
    tickers = [t.strip().upper() for t in tickers_input.split(",")]

    start_date = questionary.text("Start date (YYYY-MM-DD):", default="2020-01-01").ask()
    end_date = questionary.text("End date (YYYY-MM-DD):", default="2024-12-31").ask()

    max_variations = int(
        questionary.text("Max variations to test:", default="10").ask()
    )

    rank_by = questionary.select(
        "Rank by:",
        choices=["sharpe_ratio", "total_return", "cagr", "max_drawdown", "win_rate"],
    ).ask()

    # Run sweep
    factory = StrategyFactory()

    if strategy_choice == "All Strategies":
        results_df = factory.run_all_strategies_sweep(
            tickers, start_date, end_date, max_variations, rank_by
        )
    else:
        strategy_class = strategy_map[strategy_choice]
        results_df = factory.run_strategy_sweep(
            strategy_class, tickers, start_date, end_date,
            max_variations=max_variations, rank_by=rank_by
        )

    # Display results
    print("\n" + "=" * 80)
    print("STRATEGY SWEEP RESULTS")
    print("=" * 80)

    # Select columns to display
    display_cols = ["strategy"] + list(results_df.columns[1:10])
    display_df = results_df[display_cols].head(15)

    # Format percentages
    pct_cols = ["total_return", "cagr", "max_drawdown", "volatility", "win_rate"]
    for col in pct_cols:
        if col in display_df.columns:
            display_df[col] = display_df[col].apply(lambda x: f"{x:.2%}")

    # Format decimals
    if "sharpe_ratio" in display_df.columns:
        display_df["sharpe_ratio"] = display_df["sharpe_ratio"].apply(lambda x: f"{x:.2f}")

    print(tabulate(display_df, headers="keys", tablefmt="grid", showindex=False))

    # Export option
    export = questionary.confirm("Export results to CSV?", default=True).ask()
    if export:
        os.makedirs("results", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"results/strategy_sweep_{timestamp}.csv"
        results_df.to_csv(filename, index=False)
        print(f"\nResults exported to {filename}")


def main():
    """Main CLI entry point."""
    print("\n" + "=" * 60)
    print("AGENTIC STRATEGY BACKTESTER")
    print("=" * 60)

    while True:
        choice = questionary.select(
            "\nWhat would you like to do?",
            choices=[
                "Run Single Strategy Backtest",
                "Run Strategy Parameter Sweep",
                "Exit",
            ],
        ).ask()

        if choice == "Run Single Strategy Backtest":
            run_single_strategy()
        elif choice == "Run Strategy Parameter Sweep":
            run_strategy_sweep()
        else:
            print("\nExiting. Happy trading!")
            break

        # Ask if user wants to continue
        continue_choice = questionary.confirm("\nRun another backtest?", default=True).ask()
        if not continue_choice:
            print("\nExiting. Happy trading!")
            break


if __name__ == "__main__":
    main()
