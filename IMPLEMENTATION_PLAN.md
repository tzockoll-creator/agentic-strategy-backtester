# Agentic Backtesting System - Implementation Plan

## Overview
Building a comprehensive backtesting system for algorithmic trading strategies with automatic parameter optimization and performance ranking.

## Architecture Design

### 1. Project Structure
```
agentic-strategy-backtester/
├── src/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── portfolio.py          # Portfolio class
│   │   ├── backtest_engine.py    # Main backtesting engine
│   │   ├── data_loader.py        # Historical data fetching
│   │   └── metrics.py            # Performance calculations
│   ├── strategies/
│   │   ├── __init__.py
│   │   ├── base.py               # Abstract Strategy class
│   │   ├── ma_crossover.py       # MA Crossover strategy
│   │   ├── rsi_reversion.py      # RSI Mean Reversion
│   │   └── bollinger_breakout.py # Bollinger Band Breakout
│   ├── factory/
│   │   ├── __init__.py
│   │   └── strategy_factory.py   # Parameter variation generator
│   └── cli/
│       ├── __init__.py
│       ├── interface.py          # Interactive CLI
│       └── visualizer.py         # Plotting utilities
├── tests/
│   ├── __init__.py
│   ├── test_portfolio.py
│   ├── test_metrics.py
│   └── test_strategies.py
├── examples/
│   └── spy_backtest.py           # Example SPY backtest
├── requirements.txt
├── setup.py
└── README.md
```

### 2. Core Components Design

#### 2.1 Portfolio Class (`src/core/portfolio.py`)
**Responsibilities:**
- Track cash balance and positions (shares held per ticker)
- Record all trades with timestamps and prices
- Calculate portfolio value over time
- Handle transaction costs

**Key Methods:**
```python
class Portfolio:
    def __init__(self, initial_cash: float, transaction_cost_pct: float = 0.001)
    def buy(self, ticker: str, shares: float, price: float, date: datetime)
    def sell(self, ticker: str, shares: float, price: float, date: datetime)
    def get_position(self, ticker: str) -> float
    def get_portfolio_value(self, current_prices: dict) -> float
    def get_trade_history() -> list[dict]
```

#### 2.2 Performance Metrics (`src/core/metrics.py`)
**Calculations:**
- **Sharpe Ratio**: `(mean_return - risk_free_rate) / std_return * sqrt(252)`
- **Maximum Drawdown**: Peak-to-trough decline
- **CAGR**: Compound Annual Growth Rate
- **Win Rate**: Percentage of profitable trades
- **Total Return**: Final value / initial value - 1
- **Volatility**: Annualized standard deviation

**Key Functions:**
```python
def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.02) -> float
def calculate_max_drawdown(equity_curve: pd.Series) -> float
def calculate_cagr(equity_curve: pd.Series) -> float
def calculate_win_rate(trades: list[dict]) -> float
```

#### 2.3 Historical Data Loader (`src/core/data_loader.py`)
**Features:**
- Use yfinance to download historical OHLCV data
- Cache data locally to avoid repeated API calls
- Support multiple tickers
- Handle missing data and adjustments

**Key Class:**
```python
class HistoricalDataLoader:
    def __init__(self, cache_dir: str = ".cache/market_data")
    def load_data(self, tickers: list[str], start_date: str, end_date: str) -> pd.DataFrame
    def get_price_series(self, ticker: str, price_type: str = "Close") -> pd.Series
```

#### 2.4 Backtest Engine (`src/core/backtest_engine.py`)
**Workflow:**
1. Load historical data for specified tickers and date range
2. Initialize portfolio with starting cash
3. Iterate through each trading day:
   - Get strategy signals (buy/sell/hold) for each ticker
   - Execute trades based on signals
   - Apply transaction costs
   - Record portfolio value
4. Calculate performance metrics
5. Return backtest results

**Key Class:**
```python
class BacktestEngine:
    def __init__(self,
                 initial_cash: float,
                 transaction_cost_pct: float = 0.001,
                 rebalance_frequency: str = "daily")

    def run_backtest(self,
                    strategy: Strategy,
                    tickers: list[str],
                    start_date: str,
                    end_date: str) -> BacktestResult
```

**BacktestResult dataclass:**
```python
@dataclass
class BacktestResult:
    equity_curve: pd.Series
    trades: list[dict]
    metrics: dict[str, float]
    strategy_name: str
    parameters: dict
```

### 3. Strategy Framework

#### 3.1 Abstract Base Class (`src/strategies/base.py`)
```python
from abc import ABC, abstractmethod

class Strategy(ABC):
    def __init__(self, parameters: dict):
        self.parameters = parameters

    @abstractmethod
    def generate_signals(self,
                        data: pd.DataFrame,
                        current_date: datetime) -> dict[str, str]:
        """
        Returns: {'TICKER': 'buy'/'sell'/'hold'}
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass
```

#### 3.2 Moving Average Crossover (`src/strategies/ma_crossover.py`)
**Logic:**
- Buy when fast MA crosses above slow MA
- Sell when fast MA crosses below slow MA
- Hold otherwise

**Parameters:**
- `fast_period`: Short MA period (e.g., 10, 20, 50)
- `slow_period`: Long MA period (e.g., 20, 50, 200)

#### 3.3 RSI Mean Reversion (`src/strategies/rsi_reversion.py`)
**Logic:**
- Buy when RSI < oversold threshold (e.g., 30)
- Sell when RSI > overbought threshold (e.g., 70)
- Hold in neutral zone

**Parameters:**
- `rsi_period`: RSI calculation period (e.g., 14, 21, 28)
- `oversold`: Oversold threshold (e.g., 20, 30, 40)
- `overbought`: Overbought threshold (e.g., 60, 70, 80)

#### 3.4 Bollinger Band Breakout (`src/strategies/bollinger_breakout.py`)
**Logic:**
- Buy when price breaks above upper band
- Sell when price breaks below lower band
- Hold within bands

**Parameters:**
- `period`: Moving average period (e.g., 20, 30, 50)
- `num_std`: Number of standard deviations (e.g., 1.5, 2.0, 2.5)

### 4. Strategy Factory

#### 4.1 Parameter Variation Generator (`src/factory/strategy_factory.py`)
**Functionality:**
- Define parameter grids for each strategy
- Generate all combinations or sample N variations
- Run backtests for all variations
- Rank by specified metric (default: Sharpe ratio)
- Return comparison table

**Parameter Grids:**
```python
MA_CROSSOVER_PARAMS = {
    'fast_period': [10, 20, 50],
    'slow_period': [20, 50, 200]
}

RSI_REVERSION_PARAMS = {
    'rsi_period': [14, 21, 28],
    'oversold': [20, 30],
    'overbought': [70, 80]
}

BOLLINGER_BREAKOUT_PARAMS = {
    'period': [20, 30, 50],
    'num_std': [1.5, 2.0, 2.5]
}
```

**Key Class:**
```python
class StrategyFactory:
    def generate_strategy_variations(self,
                                    strategy_class: type[Strategy],
                                    param_grid: dict,
                                    max_variations: int = 10) -> list[Strategy]

    def run_strategy_sweep(self,
                          strategy_class: type[Strategy],
                          param_grid: dict,
                          tickers: list[str],
                          start_date: str,
                          end_date: str,
                          rank_by: str = "sharpe_ratio") -> pd.DataFrame
```

### 5. Interactive CLI

#### 5.1 Interface (`src/cli/interface.py`)
**Features:**
- Menu-driven interface using `questionary` or `prompt_toolkit`
- Strategy selection
- Date range picker
- Ticker input (single or multiple)
- Parameter customization option
- Display results in formatted tables

**Menu Flow:**
```
1. Select Strategy
   - MA Crossover
   - RSI Mean Reversion
   - Bollinger Band Breakout
   - Run Strategy Sweep (all variations)

2. Configure Backtest
   - Enter tickers (comma-separated)
   - Start date (YYYY-MM-DD)
   - End date (YYYY-MM-DD)
   - Initial cash
   - Transaction cost %

3. View Results
   - Performance metrics table
   - Equity curve plot
   - Drawdown chart
   - Trade log (optional)

4. Export Results
   - JSON file with all results
   - Plot images (PNG)
```

#### 5.2 Visualizer (`src/cli/visualizer.py`)
**Plots:**
1. **Equity Curve**: Portfolio value over time with buy/hold comparison
2. **Drawdown Chart**: Underwater plot showing drawdowns
3. **Returns Distribution**: Histogram of daily returns

**Key Functions:**
```python
def plot_equity_curve(backtest_result: BacktestResult, benchmark: pd.Series = None)
def plot_drawdown(backtest_result: BacktestResult)
def plot_returns_distribution(backtest_result: BacktestResult)
def save_plots(backtest_result: BacktestResult, output_dir: str)
```

### 6. Implementation Order

**Phase 1: Core Engine (Days 1-2)**
1. Set up project structure and dependencies
2. Implement Portfolio class
3. Implement PerformanceMetrics module
4. Implement HistoricalDataLoader
5. Implement BacktestEngine
6. Test with simple buy-and-hold strategy on SPY

**Phase 2: Strategy Framework (Days 3-4)**
7. Create abstract Strategy base class
8. Implement MA Crossover strategy
9. Implement RSI Mean Reversion strategy
10. Implement Bollinger Band Breakout strategy
11. Test each strategy individually on SPY 2020-2024

**Phase 3: Strategy Factory (Day 5)**
12. Implement StrategyFactory
13. Generate parameter variations
14. Run strategy sweeps
15. Create comparison tables

**Phase 4: CLI and Visualization (Days 6-7)**
16. Build interactive CLI interface
17. Implement visualization functions
18. Add JSON export functionality
19. Integration testing

**Phase 5: Testing and Documentation (Day 8)**
20. Write unit tests for core calculations
21. Write integration tests
22. Create comprehensive README
23. Add usage examples

### 7. Dependencies

**requirements.txt:**
```
pandas>=2.0.0
numpy>=1.24.0
yfinance>=0.2.0
matplotlib>=3.7.0
questionary>=2.0.0
pytest>=7.4.0
python-dateutil>=2.8.0
```

### 8. Testing Strategy

**Unit Tests:**
- `test_portfolio.py`: Test buy/sell, position tracking, portfolio value
- `test_metrics.py`: Validate Sharpe, drawdown, CAGR calculations with known values
- `test_strategies.py`: Test signal generation for each strategy

**Integration Tests:**
- End-to-end backtest with known data
- Compare results against manual calculations
- Verify transaction costs are applied correctly

**Test Data:**
- Use synthetic data with known patterns for unit tests
- Use SPY 2020-2024 real data for integration tests

### 9. Key Design Decisions

1. **Daily Rebalancing**: Simplifies implementation; assumes signals are generated at market close and executed at next open
2. **Transaction Costs**: Applied as percentage of trade value
3. **Position Sizing**: Equal dollar amounts per position (can extend to sophisticated sizing later)
4. **Data Source**: yfinance for free, reliable historical data
5. **Caching**: Local caching of market data to speed up repeated backtests
6. **Type Hints**: Throughout for better IDE support and error catching
7. **Dataclasses**: For clean data structures (BacktestResult, Trade, etc.)

### 10. Future Enhancements (Out of Scope)

- Multiple timeframe support (intraday)
- Short selling
- Options and derivatives
- Walk-forward optimization
- Monte Carlo simulation
- Risk management rules (stop-loss, position limits)
- Live trading integration
- Web dashboard interface
- Machine learning strategy integration

## Success Criteria

1. ✅ Successfully backtest SPY from 2020-2024 with all three strategies
2. ✅ Generate accurate performance metrics (verified against known calculations)
3. ✅ Strategy factory produces 10 variations per strategy
4. ✅ CLI is intuitive and produces clear visualizations
5. ✅ All unit tests pass
6. ✅ README enables a new user to run their first backtest in under 5 minutes

## Getting Started

Once implemented, users can run:
```bash
# Install dependencies
pip install -r requirements.txt

# Run example backtest
python examples/spy_backtest.py

# Start interactive CLI
python -m src.cli.interface
```

---

**Ready to proceed with implementation?** I'll start with Phase 1: Core Engine, building the Portfolio class and backtesting infrastructure.
