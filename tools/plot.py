"""
Plot candles stored in SQLite.
"""

from app.candles import build_candles
from app.plotting import plot_candles
from app.storage import load_trades


def main():

    trades = load_trades(limit=5000)

    candles = build_candles(
        trades,
        timeframe="1h",
    )

    print(f"Trades  : {len(trades)}")
    print(f"Candles : {len(candles)}")
    print(type(candles[0]))
    print(candles[0])
    print(candles[0].__dict__ if hasattr(candles[0], "__dict__") else "No __dict__")
    print(dir(candles[0]))

    plot_candles(
        candles,
        title="BTC_IRT - 1 Minute",
    )


if __name__ == "__main__":
    main()