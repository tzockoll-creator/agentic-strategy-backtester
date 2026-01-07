# MCP Server Integration Guide

## What is MCP?

Model Context Protocol (MCP) allows you to create tools that Claude can use directly in conversations.

## Creating a Backtesting MCP Server

You could create an MCP server that exposes backtesting as a tool:

### 1. Install MCP SDK

```bash
npm install -g @anthropic/mcp
```

### 2. Create MCP Server (mcp_server.py)

```python
from mcp.server import Server
from src.core.backtest_engine import BacktestEngine
from src.strategies.ma_crossover import MovingAverageCrossover

server = Server("backtesting")

@server.tool()
def run_backtest(strategy: str, ticker: str, start_date: str, end_date: str):
    """Run a backtest on specified parameters"""
    engine = BacktestEngine()

    if strategy == "ma_crossover":
        strat = MovingAverageCrossover(20, 50)

    result = engine.run_backtest(strat, [ticker], start_date, end_date)

    return {
        "total_return": result.metrics["total_return"],
        "sharpe_ratio": result.metrics["sharpe_ratio"],
        "max_drawdown": result.metrics["max_drawdown"]
    }

server.run()
```

### 3. Configure Claude to Use It

Add to your Claude Code configuration:

```json
{
  "mcpServers": {
    "backtesting": {
      "command": "python",
      "args": ["mcp_server.py"]
    }
  }
}
```

### 4. Use in Conversations

Then in Claude conversations, you could say:
- "Run a backtest on SPY from 2020 to 2024"
- "Compare MA crossover vs RSI strategies"

Claude would automatically call your backtesting tools!

## Resources

- [MCP Documentation](https://github.com/anthropics/claude-code)
- [Creating MCP Servers](https://modelcontextprotocol.io/)

## Simpler Alternative

For now, just use:
1. **Claude Code** (this terminal interface) for development
2. **Regular Claude.ai** for discussing results

No integration needed - they work great together!
