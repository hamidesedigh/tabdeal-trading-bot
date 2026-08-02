"""
Quality state.

Quality is represented by the rolling coefficient of determination (R²)
of a linear regression.
"""

from __future__ import annotations

from app.models import Candle
from app.state.models import StateSeries
from app.state.utils import linear_regression


def quality(
    candles: list[Candle],
    period: int = 20,
) -> StateSeries:
    """
    Calculate rolling regression quality (R²).

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

        _, _, r_squared = linear_regression(window)

        values.append(r_squared)

    return StateSeries(
        name="Quality",
        values=values,
    )