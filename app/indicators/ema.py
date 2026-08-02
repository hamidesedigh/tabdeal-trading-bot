"""
Exponential Moving Average (EMA).
"""

from __future__ import annotations

from app.models import Candle
from app.indicators.utils import closing_prices


def ema_values(
    values: list[float],
    period: int,
) -> list[float | None]:
    """
    Compute EMA over a numeric series.

    Parameters
    ----------
    values
        Input numeric values.

    period
        EMA period.

    Returns
    -------
    list[float | None]
    """

    if period <= 0:
        raise ValueError("period must be positive.")

    if len(values) < period:
        return [None] * len(values)

    multiplier = 2 / (period + 1)

    result: list[float | None] = [None] * len(values)

    first = sum(values[:period]) / period

    result[period - 1] = first

    previous = first

    for i in range(period, len(values)):

        previous = (
            (values[i] - previous)
            * multiplier
            + previous
        )

        result[i] = previous

    return result


def ema(
    candles: list[Candle],
    period: int,
) -> list[float | None]:
    """
    Compute EMA from candle closing prices.
    """

    return ema_values(
        closing_prices(candles),
        period,
    )