from setuptools import setup, find_packages

setup(
    name="agentic-strategy-backtester",
    version="0.1.0",
    description="An agentic backtesting system for algorithmic trading strategies",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "yfinance>=0.2.0",
        "matplotlib>=3.7.0",
        "questionary>=2.0.0",
        "pytest>=7.4.0",
        "python-dateutil>=2.8.0",
        "tabulate>=0.9.0",
    ],
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Financial and Insurance Industry",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
