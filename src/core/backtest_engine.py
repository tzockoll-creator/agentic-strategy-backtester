"""Backtesting engine for running strategy simulations."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, TYPE_CHECKING
import pandas as pd

from src.core.portfolio import Portfolio
from src.core.data_loader import HistoricalDataLoader
from src.core.metrics import calculate_all_metrics

if TYPE_CHECKING:
    from src.strategies.base import Strategy


@dataclass
class BacktestResult:
    """Results from a backtest run."""

    strategy_name: str
    parameters: Dict
    equity_curve: pd.Series
    trades: List[Dict]
    metrics: Dict[str, float]
    start_date: str
    end_date: str
    tickers: List[str]
    initial_cash: float

    def to_dict(self) -> Dict:
        """Convert result to dictionary for JSON export."""
        return {
            "strategy_name": self.strategy_name,
            "parameters": self.parameters,
            "equity_curve": self.equity_curve.to_dict(),
            "trades": self.trades,
            "metrics": self.metrics,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "tickers": self.tickers,
            "initial_cash": self.initial_cash,
        }


class BacktestEngine:
    """Engine for running backtests."""

    def __init__(
        self,
        initial_cash: float = 100000.0,
        transaction_cost_pct: float = 0.001,
        rebalance_frequency: str = "daily",
    ):
        """
        Initialize backtest engine.

        Args:
            initial_cash: Starting portfolio cash
            transaction_cost_pct: Transaction cost as percentage (0.001 = 0.1%)
            rebalance_frequency: Frequency of rebalancing ('daily' only for now)
        """
        self.initial_cash = initial_cash
        self.transaction_cost_pct = transaction_cost_pct
        self.rebalance_frequency = rebalance_frequency

        if rebalance_frequency != "daily":
            raise NotImplementedError("Only daily rebalancing is currently supported")

        self.data_loader = HistoricalDataLoader()

    def run_backtest(
        self,
        strategy: "Strategy",
        tickers: List[str],
        start_date: str,
        end_date: str,
        position_size_pct: float = 1.0,
    ) -> BacktestResult:
        """
        Run a backtest for a strategy.

        Args:
            strategy: Trading strategy to test
            tickers: List of ticker symbols to trade
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            position_size_pct: Percentage of portfolio to allocate per position (1.0 = 100%)

        Returns:
            BacktestResult object with all results
        """
        # Load historical data
        print(f"Loading data for {tickers} from {start_date} to {end_date}...")
        data = self.data_loader.load_data(tickers, start_date, end_date)

        # Initialize portfolio
        portfolio = Portfolio(self.initial_cash, self.transaction_cost_pct)

        # Track equity curve
        equity_curve = {}

        # Get list of trading dates
        trading_dates = data.index.tolist()

        print(f"Running backtest for {strategy.name}...")
        print(f"Total trading days: {len(trading_dates)}")

        # Iterate through each trading day
        for i, date in enumerate(trading_dates):
            # Get current prices for all tickers
            current_prices = {}
            for ticker in tickers:
                try:
                    price = data[ticker]["Close"].loc[date]
                    if pd.notna(price):
                        current_prices[ticker] = float(price)
                except (KeyError, TypeError):
                    pass

            # Skip if no valid prices
            if not current_prices:
                continue

            # Generate signals from strategy
            # Pass data up to current date to avoid lookahead bias
            historical_data = data.loc[:date]
            signals = strategy.generate_signals(historical_data, date)

            # Execute trades based on signals
            for ticker, signal in signals.items():
                if ticker not in current_prices:
                    continue

                price = current_prices[ticker]
                current_position = portfolio.get_position(ticker)

                if signal == "buy" and current_position == 0:
                    # Calculate position size
                    portfolio_value = portfolio.get_portfolio_value(current_prices)
                    cash_to_use = portfolio.cash * position_size_pct / len([s for s in signals.values() if s == "buy"])
                    shares = int(cash_to_use / price)

                    if shares > 0:
                        portfolio.buy(ticker, shares, price, date)

                elif signal == "sell" and current_position > 0:
                    # Sell entire position
                    portfolio.sell(ticker, current_position, price, date)

            # Record portfolio value
            portfolio_value = portfolio.get_portfolio_value(current_prices)
            equity_curve[date] = portfolio_value

            # Progress update
            if (i + 1) % 50 == 0 or i == len(trading_dates) - 1:
                print(f"Progress: {i + 1}/{len(trading_dates)} days, "
                      f"Portfolio value: ${portfolio_value:,.2f}")

        # Create equity curve series
        equity_series = pd.Series(equity_curve)
        equity_series.index = pd.to_datetime(equity_series.index)

        # Calculate performance metrics
        metrics = calculate_all_metrics(equity_series, portfolio.get_trade_history())

        # Create and return result
        result = BacktestResult(
            strategy_name=strategy.name,
            parameters=strategy.parameters,
            equity_curve=equity_series,
            trades=portfolio.get_trade_history(),
            metrics=metrics,
            start_date=start_date,
            end_date=end_date,
            tickers=tickers,
            initial_cash=self.initial_cash,
        )

        print(f"\nBacktest complete!")
        print(f"Total Return: {metrics['total_return']:.2%}")
        print(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
        print(f"Max Drawdown: {metrics['max_drawdown']:.2%}")
        print(f"Total Trades: {metrics['total_trades']}")

        return result

    def run_multiple_backtests(
        self,
        strategies: List["Strategy"],
        tickers: List[str],
        start_date: str,
        end_date: str,
    ) -> List[BacktestResult]:
        """
        Run backtests for multiple strategies.

        Args:
            strategies: List of strategies to test
            tickers: List of ticker symbols
            start_date: Start date
            end_date: End date

        Returns:
            List of BacktestResult objects
        """
        results = []
        for i, strategy in enumerate(strategies):
            print(f"\n{'=' * 60}")
            print(f"Running strategy {i + 1}/{len(strategies)}: {strategy.name}")
            print(f"{'=' * 60}")

            result = self.run_backtest(strategy, tickers, start_date, end_date)
            results.append(result)

        return results
