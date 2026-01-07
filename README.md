# Agentic Strategy Backtester

A comprehensive backtesting system for algorithmic trading strategies with automatic parameter optimization and performance ranking.

## Features

- **Core Backtesting Engine**: Portfolio tracking, transaction costs, daily rebalancing
- **Performance Metrics**: Sharpe ratio, max drawdown, CAGR, win rate, volatility
- **Three Built-in Strategies**:
  - Moving Average Crossover
  - RSI Mean Reversion
  - Bollinger Band Breakout
- **Strategy Factory**: Auto-generate and test parameter variations
- **Interactive CLI**: Menu-driven interface for strategy testing
- **Visualization**: Equity curves, drawdown charts, returns distribution
- **Export**: Results to JSON, plots to PNG, comparison tables to CSV

## Installation

### Requirements
- Python 3.9+
- pip

### Setup

```bash
# Clone the repository
git clone <repository-url>
cd agentic-strategy-backtester

# Install dependencies
pip install -r requirements.txt

# Or install in development mode
pip install -e .
```

## Quick Start

### 1. Run the Interactive CLI

```bash
python -m src.cli.interface
```

This launches an interactive menu where you can:
- Select a strategy
- Configure parameters
- Set date range and tickers
- View results and plots
- Export data

### 2. Run Example Backtest

```bash
python examples/spy_backtest.py
```

This runs all three strategies on SPY (2020-2024) and generates comparison plots.

### 3. Run Unit Tests

```bash
pytest tests/ -v
```

## Usage Examples

### Basic Backtest

```python
from src.core.backtest_engine import BacktestEngine
from src.strategies.ma_crossover import MovingAverageCrossover

# Create strategy
strategy = MovingAverageCrossover(fast_period=20, slow_period=50)

# Initialize engine
engine = BacktestEngine(initial_cash=100000, transaction_cost_pct=0.001)

# Run backtest
result = engine.run_backtest(
    strategy=strategy,
    tickers=["SPY"],
    start_date="2020-01-01",
    end_date="2024-12-31"
)

# View metrics
print(f"Total Return: {result.metrics['total_return']:.2%}")
print(f"Sharpe Ratio: {result.metrics['sharpe_ratio']:.2f}")
print(f"Max Drawdown: {result.metrics['max_drawdown']:.2%}")
```

### Parameter Sweep

```python
from src.factory.strategy_factory import StrategyFactory
from src.strategies.rsi_reversion import RSIMeanReversion

# Initialize factory
factory = StrategyFactory()

# Run parameter sweep
results_df = factory.run_strategy_sweep(
    strategy_class=RSIMeanReversion,
    tickers=["SPY"],
    start_date="2020-01-01",
    end_date="2024-12-31",
    max_variations=10,
    rank_by="sharpe_ratio"
)

# View top strategies
print(results_df.head(5))
```

### Custom Strategy

```python
from src.strategies.base import Strategy
import pandas as pd

class MyCustomStrategy(Strategy):
    def __init__(self, my_param: int = 10):
        super().__init__({"my_param": my_param})
        self.my_param = my_param

    @property
    def name(self) -> str:
        return f"CustomStrategy_{self.my_param}"

    def generate_signals(self, data: pd.DataFrame, current_date) -> dict:
        signals = {}
        tickers = data.columns.get_level_values(0).unique()

        for ticker in tickers:
            # Your signal logic here
            signals[ticker] = "hold"

        return signals

# Use your custom strategy
strategy = MyCustomStrategy(my_param=20)
result = engine.run_backtest(strategy, ["SPY"], "2020-01-01", "2024-12-31")
```

### Visualization

```python
from src.cli.visualizer import plot_equity_curve, plot_drawdown, save_plots

# Plot equity curve
plot_equity_curve(result, show=True)

# Plot drawdown
plot_drawdown(result, show=True)

# Save all plots
save_plots(result, output_dir="results")
```

### Compare Multiple Strategies

```python
from src.cli.visualizer import plot_comparison

# Run multiple backtests
strategies = [
    MovingAverageCrossover(20, 50),
    RSIMeanReversion(14, 30, 70),
    BollingerBandBreakout(20, 2.0)
]

results = [
    engine.run_backtest(s, ["SPY"], "2020-01-01", "2024-12-31")
    for s in strategies
]

# Compare equity curves
plot_comparison(results, metric="equity_curve")

# Compare drawdowns
plot_comparison(results, metric="drawdown")
```

## Strategy Details

### Moving Average Crossover

Generates buy signals when fast MA crosses above slow MA, sell signals when it crosses below.

**Parameters:**
- `fast_period`: Short MA period (e.g., 10, 20, 50)
- `slow_period`: Long MA period (e.g., 50, 100, 200)

### RSI Mean Reversion

Buys when RSI drops below oversold threshold, sells when it rises above overbought threshold.

**Parameters:**
- `rsi_period`: RSI calculation period (e.g., 7, 14, 21)
- `oversold`: Oversold threshold (e.g., 20, 30)
- `overbought`: Overbought threshold (e.g., 70, 80)

### Bollinger Band Breakout

Buys on breakout above upper band, sells on breakdown below lower band.

**Parameters:**
- `period`: Moving average period (e.g., 20, 30)
- `num_std`: Standard deviations for bands (e.g., 1.5, 2.0, 2.5)

## Performance Metrics

| Metric | Description |
|--------|-------------|
| **Total Return** | Overall percentage gain/loss |
| **CAGR** | Compound Annual Growth Rate |
| **Sharpe Ratio** | Risk-adjusted return (higher is better) |
| **Max Drawdown** | Largest peak-to-trough decline |
| **Volatility** | Annualized standard deviation of returns |
| **Win Rate** | Percentage of profitable trades |

## Project Structure

```
agentic-strategy-backtester/
├── src/
│   ├── core/                  # Core backtesting components
│   │   ├── portfolio.py       # Portfolio management
│   │   ├── backtest_engine.py # Backtesting engine
│   │   ├── data_loader.py     # Historical data fetching
│   │   └── metrics.py         # Performance calculations
│   ├── strategies/            # Trading strategies
│   │   ├── base.py            # Abstract base class
│   │   ├── ma_crossover.py
│   │   ├── rsi_reversion.py
│   │   └── bollinger_breakout.py
│   ├── factory/               # Strategy optimization
│   │   └── strategy_factory.py
│   └── cli/                   # User interface
│       ├── interface.py       # Interactive CLI
│       └── visualizer.py      # Plotting functions
├── tests/                     # Unit tests
├── examples/                  # Example scripts
├── requirements.txt
└── README.md
```

## Configuration

### Transaction Costs

Default: 0.1% (0.001) per trade. Adjust when creating the engine:

```python
engine = BacktestEngine(transaction_cost_pct=0.002)  # 0.2% per trade
```

### Initial Cash

Default: $100,000. Customize:

```python
engine = BacktestEngine(initial_cash=50000)
```

### Data Caching

Market data is cached locally in `.cache/market_data/` to speed up repeated backtests. To clear cache:

```python
from src.core.data_loader import HistoricalDataLoader

loader = HistoricalDataLoader()
loader.clear_cache()  # Clear all cache
loader.clear_cache("SPY")  # Clear specific ticker
```

## Testing

Run all tests:

```bash
pytest tests/ -v
```

Run specific test file:

```bash
pytest tests/test_portfolio.py -v
```

Run with coverage:

```bash
pytest tests/ --cov=src --cov-report=html
```

## Export Formats

### JSON Export

```python
from src.cli.interface import export_to_json

export_to_json(result, output_dir="results")
```

Exports:
- Strategy name and parameters
- All performance metrics
- Equity curve (date, value pairs)
- Complete trade history

### CSV Export (Strategy Sweeps)

Parameter sweep results are automatically saved to CSV with all metrics and parameters.

## Troubleshooting

### yfinance Download Errors

If data download fails:
1. Check internet connection
2. Verify ticker symbols are correct
3. Try clearing cache: `loader.clear_cache()`
4. Some tickers may have limited historical data

### Memory Issues

For large parameter sweeps or long backtests:
- Reduce `max_variations`
- Shorten date range
- Use fewer tickers
- Clear cache between runs

### Import Errors

Ensure you're running from the project root directory:

```bash
cd /path/to/agentic-strategy-backtester
python -m src.cli.interface
```

## Future Enhancements

Potential features (not yet implemented):
- Intraday data support
- Short selling
- Options and derivatives
- Walk-forward optimization
- Monte Carlo simulation
- Live trading integration
- Multi-asset portfolios
- Custom risk management rules

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - feel free to use for personal or commercial projects.

## Disclaimer

This software is for educational purposes only. Past performance does not guarantee future results. Always do your own research before trading with real money. The authors are not responsible for any financial losses incurred using this software.

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing documentation
- Review example scripts

---

**Happy Backtesting!** 🚀📈
