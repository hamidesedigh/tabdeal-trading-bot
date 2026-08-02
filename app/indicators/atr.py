"""
Average True Range (ATR).

Uses Wilder's smoothing.
"""

from __future__ import annotations

from app.models import Candle
from app.indicators.utils import (
    true_range,
    wilder_smooth,
)


def atr(
    candles: list[Candle],
    period: int = 14,
) -> list[float | None]:
    """
    Calculate Average True Range (ATR).

    Parameters
    ----------
    candles
        OHLC candles.

    period
        ATR period.

    Returns
    -------
    list[float | None]
        ATR values.
    """

    if len(candles) < period:
        return [None] * len(candles)

    tr = true_range(candles)

    return wilder_smooth(
        tr,
        period,
    )