"""
Plot OHLCV candles.
"""

from datetime import datetime

import matplotlib.pyplot as plt
import mplfinance as mpf
import pandas as pd

from app.models import Candle


def plot_candles(
    candles: list[Candle],
    title: str = "Candlestick Chart",
) -> None:
    """
    Plot OHLCV candles using mplfinance.
    """

    if not candles:
        raise ValueError("No candles to plot.")

    data = []

    for candle in candles:
        data.append(
            {
                "Date": datetime.fromtimestamp(
                    candle.timestamp / 1000
                ),
                "Open": candle.open,
                "High": candle.high,
                "Low": candle.low,
                "Close": candle.close,
                "Volume": candle.volume,
            }
        )

    df = pd.DataFrame(data)

    df.set_index("Date", inplace=True)

    mpf.plot(
        df,
        type="candle",
        style="yahoo",
        volume=True,
        title=title,
        ylabel="Price",
        ylabel_lower="Volume",
        figsize=(14, 8),
        tight_layout=True,
    )

    plt.show()