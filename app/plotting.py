"""
Plot OHLCV candles using mplfinance.
"""

from __future__ import annotations
from app.models import (
    Candle,
    OverlayIndicator,
    PanelIndicator,
)

from datetime import datetime
from matplotlib.lines import Line2D

import matplotlib.pyplot as plt
import mplfinance as mpf
import pandas as pd
import numpy as np


def _indicator_series(
    values: list[float | None],
    index: pd.Index,
) -> pd.Series:
    """
    Convert indicator values to a pandas Series compatible with mplfinance.

    None values are converted to NaN so matplotlib skips them.
    """

    return pd.Series(
        [
            np.nan if value is None else value
            for value in values
        ],
        index=index,
    )


def plot_candles(
    candles: list[Candle],
    overlays: list[OverlayIndicator] | None = None,
    panels: list[PanelIndicator] | None = None,
    title: str = "Candlestick Chart",
    figsize: tuple[int, int] = (14, 8),
    price_panel_ratio: int = 4,
    volume_panel_ratio: int = 1,
    max_candles: int | None = None,
    show: bool = True,
):
    """
    Plot OHLCV candles.

    Parameters
    ----------
    candles
        Candle list.
    overlays
        Indicators drawn on price panel.
    panels
        Indicators drawn on their own panels.
    title
        Chart title.
    figsize
        Matplotlib figure size.
    price_panel_ratio
        Height ratio of price panel.
    volume_panel_ratio
        Height ratio of volume panel.
    max_candles
        Number of most recent candles to display. Indicators are expected to
        be calculated from the full candle list before this display slice.
    show
        If True call plt.show().
        Otherwise only return figure and axes.
    """

    overlays = overlays or []
    panels = panels or []

    if not candles:
        raise ValueError("No candles to plot.")

    if max_candles is not None and max_candles <= 0:
        raise ValueError("max_candles must be positive.")

    source_candle_count = len(candles)

    if max_candles is not None:
        candles = candles[-max_candles:]

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

    candle_count = len(df)

    addplots = []

    #
    # Overlay indicators
    #

    for indicator in overlays:

        if len(indicator.values) != source_candle_count:
            raise ValueError(
                f"{indicator.name}: indicator length "
                f"({len(indicator.values)}) "
                f"does not match candles ({source_candle_count})."
            )

        kwargs = {
        "panel": 0,
        "ylabel": "Price",
        "color": indicator.color,
        "linestyle": indicator.linestyle,
        "width": indicator.linewidth,
    }

        if indicator.plot_type == "scatter":
            kwargs["type"] = "scatter"
            kwargs["marker"] = indicator.marker

        series = _indicator_series(
            indicator.values[-candle_count:],
            df.index,
        )

        addplots.append(
            mpf.make_addplot(
                series,
                **kwargs,
            )
        )
    #
    # Panel indicators
    #

    panel_index = 2

    for indicator in panels:

        #
        # One panel may contain multiple plotted series.
        #

        for line in indicator.series:

            if len(line.values) != source_candle_count:
                raise ValueError(
                    f"{line.name}: indicator length "
                    f"({len(line.values)}) "
                    f"does not match candles ({source_candle_count})."
                )

            kwargs = dict(
                panel=panel_index,
                ylabel=indicator.name,
                color=line.color,
                linestyle=line.linestyle,
                width=line.linewidth,
                secondary_y=False,
            )

            if line.plot_type == "scatter":
                kwargs["type"] = "scatter"
                kwargs["marker"] = line.marker

            elif line.plot_type == "bar":
                kwargs["type"] = "bar"

            series = _indicator_series(
                line.values[-candle_count:],
                df.index,
            )

            addplots.append(
                mpf.make_addplot(
                    series,
                    **kwargs,
                )
            )

        #
        # next indicator gets its own panel
        #

        panel_index += 1

    panel_ratios = [
        price_panel_ratio,
        volume_panel_ratio,
    ]

    panel_ratios.extend([1] * len(panels))

    fig, axes = mpf.plot(
        df,
        type="candle",
        style="yahoo",
        volume=True,
        addplot=addplots,
        panel_ratios=tuple(panel_ratios),
        title=title,
        ylabel="Price",
        ylabel_lower="Volume",
        figsize=figsize,
        tight_layout=True,
        returnfig=True,
    )

    # mplfinance places panel labels on the right by default, where they can
    # be clipped by the figure boundary. Keep them visible on the left.
    for panel_number, indicator in enumerate(panels, start=2):
        panel_axis = axes[panel_number * 2]
        panel_axis.set_ylabel(indicator.name)
        panel_axis.yaxis.set_label_position("left")
        panel_axis.yaxis.tick_left()

    #
    # Legend
    #

    legend_handles = []

    for indicator in overlays:

        legend_handles.append(
            Line2D(
                [],
                [],
                color=indicator.color,
                linewidth=indicator.linewidth,
                linestyle=indicator.linestyle,
                label=indicator.name,
            )
        )

    if legend_handles:
        axes[0].legend(
            handles=legend_handles,
            loc="upper left",
            frameon=True,
        )

    if show:
        plt.show()

    return fig, axes
