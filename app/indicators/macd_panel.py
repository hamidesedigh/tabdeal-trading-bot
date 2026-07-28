"""
Build MACD panel.
"""

from app.indicators.macd import macd
from app.models import Candle
from app.models import PanelIndicator
from app.models import PlotSeries


def create_macd_panel(
    candles: list[Candle],
) -> PanelIndicator:

    macd_line, signal_line, histogram = macd(candles)

    return PanelIndicator(
        name="MACD",
        series=[
            PlotSeries(
                name="MACD",
                values=macd_line,
                color="tab:blue",
            ),
            PlotSeries(
                name="Signal",
                values=signal_line,
                color="orange",
            ),
            PlotSeries(
                name="Histogram",
                values=histogram,
                color="tab:gray",
                plot_type="bar",
            ),
        ],
    )
