"""
Plot candles stored in SQLite.
"""

from app.candles import build_candles
from app.indicators.sma import sma
from app.models import OverlayIndicator
from app.plotting import plot_candles
from app.storage import load_trades


def main():

    trades = load_trades(limit=5000)

    candles = build_candles(
        trades,
        timeframe="1h",
    )

    sma20 = sma(
        candles,
        period=20,
    )

    print(f"Trades  : {len(trades)}")
    print(f"Candles : {len(candles)}")
    print(type(candles[0]))
    print(candles[0])
    print(candles[0].__dict__ if hasattr(candles[0], "__dict__") else "No __dict__")
    print(dir(candles[0]))

    plot_candles(
        candles,
        overlays=[
            OverlayIndicator(
                name="SMA20",
                values=sma20,
            ),
        ],
        title="BTC_IRT - 1 Hour",
    )


if __name__ == "__main__":
    main()