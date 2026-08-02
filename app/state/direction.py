"""
Direction state.

Direction is represented by the slope of a rolling linear regression.
"""

from __future__ import annotations

from app.models import Candle
from app.state.models import StateSeries
from app.state.utils import linear_regression


def direction(
    candles: list[Candle],
    period: int = 20,
) -> StateSeries:
    """
    Calculate rolling regression slope.

    Returns
    -------
    StateSeries
    """

    closes = [c.close for c in candles]

    values: list[float | None] = []

    for i in range(len(closes)):

        if i < period - 1:
            values.append(None)
            continue

        window = closes[i - period + 1 : i + 1]

        slope, _, _  = linear_regression(window)

        values.append(slope)

    return StateSeries(
        name="Direction",
        values=values,
    )