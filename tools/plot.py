"""
Plot candles stored in SQLite.
"""

from app.candles import build_candles
from app.indicators.pipeline import build_indicators
from app.indicators.sma import sma
from app.indicators.ema import ema
from app.indicators.rsi import rsi
from app.indicators.macd_panel import create_macd_panel
from app.models import IndicatorSpec
from app.plotting import plot_candles
from app.storage import load_trades

DISPLAY_CANDLE_COUNT = 60


def main():

    # Calculate indicators from all available history so the displayed range
    # has enough warm-up data for RSI, MACD, and moving averages.
    trades = load_trades()

    candles = build_candles(
        trades,
        timeframe="15min",
    )

    print(f"Trades  : {len(trades)}")
    displayed_candle_count = min(
        len(candles),
        DISPLAY_CANDLE_COUNT,
    )
    print(
        f"Candles : {len(candles)} "
        f"(displaying {displayed_candle_count})"
    )

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
        panels=[
            IndicatorSpec(
                name="RSI14",
                func=rsi,
                kwargs={"period": 14},
                color="tab:green",
            ),
        ],
    )

    panels.append(
        create_macd_panel(candles)
    )

    plot_candles(
        candles,
        overlays=overlays,
        panels=panels,
        title="BTC_IRT",
        max_candles=DISPLAY_CANDLE_COUNT,
    )


if __name__ == "__main__":
    main()
