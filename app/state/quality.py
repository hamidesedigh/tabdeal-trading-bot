"""
Quality state.

Quality is represented by rolling R² of the regression.
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
    Rolling regression quality (R²).
    """

    closes = [c.close for c in candles]

    values: list[float | None] = []

    for i in range(len(closes)):

        if i < period - 1:
            values.append(None)
            continue

        window = closes[i - period + 1:i + 1]

        values.append(
            _r_squared(window)
        )

    return StateSeries(
        name="Quality",
        values=values,
    )


def _r_squared(
    values: list[float],
) -> float:

    slope, intercept = linear_regression(values)

    mean = sum(values) / len(values)

    ss_tot = 0.0
    ss_res = 0.0

    for i, y in enumerate(values):

        prediction = slope * i + intercept

        ss_tot += (y - mean) ** 2
        ss_res += (y - prediction) ** 2

    if ss_tot == 0:
        return 0.0

    return 1 - ss_res / ss_tot