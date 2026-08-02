"""
Run a backtest of the trading strategy against historical candles.

Usage:
    python -m tools.backtest [timeframe]

    e.g. python -m tools.backtest 5min
"""

import sys

from app.backtest import run_backtest
from app.candles import build_candles
from app.state.pipeline import build_state
from app.storage import load_trades
from app.strategy.pipeline import build_signals

WARMUP_PERIOD = 20  # matches the `period` default used across app/state


def main(timeframe: str = "5min", fee_pct: float = 0.0) -> None:

    trades = load_trades()
    candles = build_candles(trades, timeframe=timeframe)

    print(f"Trades  : {len(trades)}")
    print(f"Candles : {len(candles)} ({timeframe})")

    if len(candles) <= WARMUP_PERIOD:
        print(
            f"\nNot enough candles to backtest: need more than "
            f"{WARMUP_PERIOD} (state indicators need a warm-up window "
            f"before they produce values). Try a smaller timeframe or "
            f"collect more trade history."
        )
        return

    state = build_state(candles)
    signals = build_signals(candles, state)

    buys = sum(1 for s in signals if s.side == "BUY")
    sells = sum(1 for s in signals if s.side == "SELL")
    print(f"Signals : {len(signals)}  ({buys} BUY / {sells} SELL)")

    result = run_backtest(candles, signals, fee_pct=fee_pct)

    print()
    print("=== Backtest Report ===")
    print(f"Trades executed : {len(result.trades)}")
    print(f"Total return    : {result.total_return_pct:+.2f}%")
    print(f"Win rate        : {result.win_rate_pct:.2f}%")
    print(f"Avg trade PnL   : {result.avg_trade_pnl_pct:+.2f}%")
    print(f"Max drawdown    : {result.max_drawdown_pct:.2f}%")

    if not result.trades:
        print(
            "\nNo completed round-trips. This can happen if a position "
            "was opened but never closed by end of data, or thresholds "
            "were never met together. Check `signals` above — 0 signals "
            "means the strategy never triggered on this data/timeframe."
        )
        return

    print()
    print("Trade log:")
    for t in result.trades:
        print(
            f"  entry={t.entry_price:>12,.0f} @ {t.entry_time}   "
            f"exit={t.exit_price:>12,.0f} @ {t.exit_time}   "
            f"pnl={t.pnl_pct * 100:+6.2f}%"
        )


if __name__ == "__main__":
    tf = sys.argv[1] if len(sys.argv) > 1 else "5min"
    main(timeframe=tf)
