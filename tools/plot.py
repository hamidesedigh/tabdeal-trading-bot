"""
Plot candles stored in SQLite.
"""

from app.indicators.registry import create_overlay
from app.candles import build_candles
from app.indicators.sma import sma
from app.models import OverlayIndicator
from app.plotting import plot_candles
from app.storage import load_trades
from app.indicators.pipeline import build_indicators
from app.models import IndicatorSpec


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

    overlays, panels = build_indicators(
        candles,
        overlays=[
            IndicatorSpec(
                name="SMA20",
                func=sma,
                kwargs={
                    "period": 20,
                },
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