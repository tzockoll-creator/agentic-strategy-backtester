"""Example: Backtest multiple strategies on SPY (2020-2024)."""

from src.core.backtest_engine import BacktestEngine
from src.strategies.ma_crossover import MovingAverageCrossover
from src.strategies.rsi_reversion import RSIMeanReversion
from src.strategies.bollinger_breakout import BollingerBandBreakout
from src.cli.visualizer import plot_comparison, save_plots


def main():
    """Run example backtests on SPY."""
    print("=" * 70)
    print("SPY BACKTEST EXAMPLE (2020-2024)")
    print("=" * 70)

    # Configuration
    tickers = ["SPY"]
    start_date = "2020-01-01"
    end_date = "2024-12-31"
    initial_cash = 100000

    # Create strategies
    strategies = [
        MovingAverageCrossover(fast_period=20, slow_period=50),
        RSIMeanReversion(rsi_period=14, oversold=30, overbought=70),
        BollingerBandBreakout(period=20, num_std=2.0),
    ]

    # Initialize backtest engine
    engine = BacktestEngine(initial_cash=initial_cash)

    # Run backtests
    results = []
    for strategy in strategies:
        print(f"\n{'=' * 70}")
        print(f"Testing: {strategy.name}")
        print(f"{'=' * 70}")

        result = engine.run_backtest(strategy, tickers, start_date, end_date)
        results.append(result)

        # Save plots for this strategy
        save_plots(result, output_dir="results")

    # Compare all strategies
    print(f"\n{'=' * 70}")
    print("STRATEGY COMPARISON")
    print(f"{'=' * 70}\n")

    # Print comparison table
    print(f"{'Strategy':<40} {'Total Return':<15} {'Sharpe':<10} {'Max DD':<10} {'Trades':<10}")
    print("-" * 85)

    for result in results:
        print(
            f"{result.strategy_name:<40} "
            f"{result.metrics['total_return']:>13.2%}  "
            f"{result.metrics['sharpe_ratio']:>8.2f}  "
            f"{result.metrics['max_drawdown']:>8.2%}  "
            f"{result.metrics['total_trades']:>8.0f}"
        )

    # Plot comparison
    plot_comparison(results, metric="equity_curve", save_path="results/comparison_equity.png", show=True)
    plot_comparison(results, metric="drawdown", save_path="results/comparison_drawdown.png", show=True)

    print("\n" + "=" * 70)
    print("Backtest complete! Results saved to 'results/' directory.")
    print("=" * 70)


if __name__ == "__main__":
    main()
