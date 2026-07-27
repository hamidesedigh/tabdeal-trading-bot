"""
Plot candles stored in SQLite.
"""

from app.candles import build_candles
from app.indicators.ema import ema
from app.indicators.pipeline import build_indicators
from app.indicators.sma import sma
from app.models import IndicatorSpec
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

    overlays, panels = build_indicators(
        candles,
        overlays=[
            IndicatorSpec(
                name="SMA20",
                func=sma,
                kwargs={"period": 20},
                color="orange",
            ),
            IndicatorSpec(
                name="EMA20",
                func=ema,
                kwargs={"period": 20},
                color="purple",
            ),
        ],
    )

    plot_candles(
        candles,
        overlays=overlays,
        panels=panels,
        title="BTC_IRT",
    )


if __name__ == "__main__":
    main()