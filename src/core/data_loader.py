"""Historical market data loader using yfinance."""

import os
import pandas as pd
import yfinance as yf
from typing import List, Optional
from datetime import datetime
import pickle


class HistoricalDataLoader:
    """Downloads and caches historical market data."""

    def __init__(self, cache_dir: str = ".cache/market_data"):
        """
        Initialize data loader.

        Args:
            cache_dir: Directory for caching downloaded data
        """
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)

    def _get_cache_path(self, ticker: str, start_date: str, end_date: str) -> str:
        """Generate cache file path for a ticker and date range."""
        filename = f"{ticker}_{start_date}_{end_date}.pkl"
        return os.path.join(self.cache_dir, filename)

    def _load_from_cache(self, ticker: str, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        """Load data from cache if available."""
        cache_path = self._get_cache_path(ticker, start_date, end_date)
        if os.path.exists(cache_path):
            try:
                with open(cache_path, "rb") as f:
                    return pickle.load(f)
            except Exception as e:
                print(f"Warning: Failed to load cache for {ticker}: {e}")
                return None
        return None

    def _save_to_cache(self, data: pd.DataFrame, ticker: str, start_date: str, end_date: str):
        """Save data to cache."""
        cache_path = self._get_cache_path(ticker, start_date, end_date)
        try:
            with open(cache_path, "wb") as f:
                pickle.dump(data, f)
        except Exception as e:
            print(f"Warning: Failed to save cache for {ticker}: {e}")

    def load_data(
        self,
        tickers: List[str],
        start_date: str,
        end_date: str,
        use_cache: bool = True,
    ) -> pd.DataFrame:
        """
        Load historical OHLCV data for multiple tickers.

        Args:
            tickers: List of ticker symbols
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            use_cache: Whether to use cached data if available

        Returns:
            DataFrame with MultiIndex columns (ticker, field)
        """
        all_data = {}

        for ticker in tickers:
            # Try to load from cache first
            if use_cache:
                cached_data = self._load_from_cache(ticker, start_date, end_date)
                if cached_data is not None:
                    all_data[ticker] = cached_data
                    print(f"Loaded {ticker} from cache")
                    continue

            # Download from yfinance
            print(f"Downloading {ticker} from {start_date} to {end_date}...")
            try:
                ticker_obj = yf.Ticker(ticker)
                data = ticker_obj.history(start=start_date, end=end_date)

                if data.empty:
                    print(f"Warning: No data returned for {ticker}")
                    continue

                # Save to cache
                if use_cache:
                    self._save_to_cache(data, ticker, start_date, end_date)

                all_data[ticker] = data

            except Exception as e:
                print(f"Error downloading {ticker}: {e}")
                continue

        if not all_data:
            raise ValueError("No data loaded for any ticker")

        # Combine all ticker data into a single DataFrame with MultiIndex columns
        combined_data = pd.concat(all_data, axis=1, keys=all_data.keys())

        # Ensure datetime index
        combined_data.index = pd.to_datetime(combined_data.index)

        # Fill forward missing data (holidays, etc.)
        combined_data = combined_data.ffill()

        return combined_data

    def get_price_series(
        self,
        data: pd.DataFrame,
        ticker: str,
        price_type: str = "Close",
    ) -> pd.Series:
        """
        Extract a specific price series for a ticker.

        Args:
            data: Combined DataFrame from load_data()
            ticker: Ticker symbol
            price_type: Type of price (Open, High, Low, Close, Adj Close)

        Returns:
            Series of prices
        """
        try:
            return data[ticker][price_type]
        except KeyError:
            raise ValueError(f"No {price_type} data found for {ticker}")

    def get_ohlcv(self, data: pd.DataFrame, ticker: str) -> pd.DataFrame:
        """
        Get OHLCV data for a specific ticker.

        Args:
            data: Combined DataFrame from load_data()
            ticker: Ticker symbol

        Returns:
            DataFrame with OHLCV columns
        """
        try:
            return data[ticker][["Open", "High", "Low", "Close", "Volume"]]
        except KeyError:
            raise ValueError(f"No OHLCV data found for {ticker}")

    def clear_cache(self, ticker: Optional[str] = None):
        """
        Clear cached data.

        Args:
            ticker: If specified, clear only this ticker's cache. Otherwise clear all.
        """
        if ticker:
            # Clear specific ticker
            for filename in os.listdir(self.cache_dir):
                if filename.startswith(f"{ticker}_"):
                    filepath = os.path.join(self.cache_dir, filename)
                    os.remove(filepath)
                    print(f"Cleared cache for {ticker}")
        else:
            # Clear all cache
            for filename in os.listdir(self.cache_dir):
                filepath = os.path.join(self.cache_dir, filename)
                if os.path.isfile(filepath):
                    os.remove(filepath)
            print("Cleared all cache")
