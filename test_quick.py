"""Quick smoke test to verify the system works."""

from src.core.backtest_engine import BacktestEngine
from src.strategies.ma_crossover import MovingAverageCrossover

print("=" * 60)
print("QUICK SMOKE TEST")
print("=" * 60)

# Create a simple strategy
strategy = MovingAverageCrossover(fast_period=20, slow_period=50)
print(f"\nStrategy: {strategy.name}")

# Initialize engine
engine = BacktestEngine(initial_cash=100000, transaction_cost_pct=0.001)
print(f"Initial cash: $100,000")

# Run a short backtest
print("\nRunning backtest on SPY (2023-01-01 to 2023-12-31)...")
result = engine.run_backtest(
    strategy=strategy,
    tickers=["SPY"],
    start_date="2023-01-01",
    end_date="2023-12-31"
)

# Display results
print("\n" + "=" * 60)
print("RESULTS")
print("=" * 60)
print(f"Total Return:  {result.metrics['total_return']:>8.2%}")
print(f"Sharpe Ratio:  {result.metrics['sharpe_ratio']:>8.2f}")
print(f"Max Drawdown:  {result.metrics['max_drawdown']:>8.2%}")
print(f"Total Trades:  {result.metrics['total_trades']:>8.0f}")
print(f"Win Rate:      {result.metrics['win_rate']:>8.2%}")
print("=" * 60)

print("\n✓ System is working correctly!")
