"""Portfolio management for backtesting."""

from datetime import datetime
from typing import Dict, List, Optional


class Portfolio:
    """Manages portfolio positions, cash, and trade history."""

    def __init__(self, initial_cash: float, transaction_cost_pct: float = 0.001):
        """
        Initialize portfolio.

        Args:
            initial_cash: Starting cash balance
            transaction_cost_pct: Transaction cost as percentage of trade value (default 0.1%)
        """
        if initial_cash <= 0:
            raise ValueError("Initial cash must be positive")
        if transaction_cost_pct < 0:
            raise ValueError("Transaction cost percentage cannot be negative")

        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.transaction_cost_pct = transaction_cost_pct
        self.positions: Dict[str, float] = {}  # ticker -> shares
        self.trades: List[Dict] = []

    def buy(
        self,
        ticker: str,
        shares: float,
        price: float,
        date: datetime,
    ) -> bool:
        """
        Execute a buy order.

        Args:
            ticker: Stock ticker symbol
            shares: Number of shares to buy
            price: Price per share
            date: Trade date

        Returns:
            True if trade executed successfully, False otherwise
        """
        if shares <= 0:
            return False

        cost = shares * price
        transaction_cost = cost * self.transaction_cost_pct
        total_cost = cost + transaction_cost

        if total_cost > self.cash:
            return False  # Insufficient funds

        # Execute trade
        self.cash -= total_cost
        self.positions[ticker] = self.positions.get(ticker, 0.0) + shares

        # Record trade
        self.trades.append({
            "date": date,
            "ticker": ticker,
            "action": "buy",
            "shares": shares,
            "price": price,
            "cost": cost,
            "transaction_cost": transaction_cost,
            "total_cost": total_cost,
        })

        return True

    def sell(
        self,
        ticker: str,
        shares: float,
        price: float,
        date: datetime,
    ) -> bool:
        """
        Execute a sell order.

        Args:
            ticker: Stock ticker symbol
            shares: Number of shares to sell
            price: Price per share
            date: Trade date

        Returns:
            True if trade executed successfully, False otherwise
        """
        if shares <= 0:
            return False

        current_position = self.positions.get(ticker, 0.0)
        if current_position < shares:
            return False  # Insufficient shares

        proceeds = shares * price
        transaction_cost = proceeds * self.transaction_cost_pct
        net_proceeds = proceeds - transaction_cost

        # Execute trade
        self.cash += net_proceeds
        self.positions[ticker] -= shares

        # Remove position if fully sold
        if self.positions[ticker] == 0:
            del self.positions[ticker]

        # Record trade
        self.trades.append({
            "date": date,
            "ticker": ticker,
            "action": "sell",
            "shares": shares,
            "price": price,
            "proceeds": proceeds,
            "transaction_cost": transaction_cost,
            "net_proceeds": net_proceeds,
        })

        return True

    def get_position(self, ticker: str) -> float:
        """Get current position in shares for a ticker."""
        return self.positions.get(ticker, 0.0)

    def get_portfolio_value(self, current_prices: Dict[str, float]) -> float:
        """
        Calculate total portfolio value.

        Args:
            current_prices: Dictionary of ticker -> current price

        Returns:
            Total portfolio value (cash + positions)
        """
        positions_value = sum(
            shares * current_prices.get(ticker, 0.0)
            for ticker, shares in self.positions.items()
        )
        return self.cash + positions_value

    def get_positions_value(self, current_prices: Dict[str, float]) -> float:
        """Calculate value of all positions (excluding cash)."""
        return sum(
            shares * current_prices.get(ticker, 0.0)
            for ticker, shares in self.positions.items()
        )

    def get_trade_history(self) -> List[Dict]:
        """Get complete trade history."""
        return self.trades.copy()

    def get_position_breakdown(self, current_prices: Dict[str, float]) -> Dict[str, Dict]:
        """
        Get detailed breakdown of all positions.

        Returns:
            Dictionary with position details per ticker
        """
        breakdown = {}
        for ticker, shares in self.positions.items():
            price = current_prices.get(ticker, 0.0)
            value = shares * price
            breakdown[ticker] = {
                "shares": shares,
                "price": price,
                "value": value,
            }
        return breakdown

    def __repr__(self) -> str:
        """String representation of portfolio."""
        return (
            f"Portfolio(cash=${self.cash:.2f}, "
            f"positions={len(self.positions)}, "
            f"trades={len(self.trades)})"
        )
