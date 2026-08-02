"""
Utility functions for technical indicators.
"""

from __future__ import annotations

from app.models import Candle


def closing_prices(
    candles: list[Candle],
) -> list[float]:
    """
    Return candle closing prices.
    """

    return [c.close for c in candles]


def opening_prices(
    candles: list[Candle],
) -> list[float]:
    """
    Return candle opening prices.
    """

    return [c.open for c in candles]


def high_prices(
    candles: list[Candle],
) -> list[float]:
    """
    Return candle high prices.
    """

    return [c.high for c in candles]


def low_prices(
    candles: list[Candle],
) -> list[float]:
    """
    Return candle low prices.
    """

    return [c.low for c in candles]


def volumes(
    candles: list[Candle],
) -> list[float]:
    """
    Return candle volumes.
    """

    return [c.volume for c in candles]


def true_range(
    candles: list[Candle],
) -> list[float]:

    if not candles:
        return []

    values = [
        candles[0].high - candles[0].low
    ]

    previous_close = candles[0].close

    for candle in candles[1:]:

        values.append(
            max(
                candle.high - candle.low,
                abs(candle.high - previous_close),
                abs(candle.low - previous_close),
            )
        )

        previous_close = candle.close

    return values

def wilder_average(
    previous: float,
    current: float,
    period: int,
) -> float:
    """
    One-step Wilder moving average.
    """

    return (
        previous * (period - 1)
        + current
    ) / period


def wilder_smooth(
    values: list[float],
    period: int,
) -> list[float | None]:
    """
    Wilder smoothing over a complete series.

    Used by ATR and ADX.
    """

    if len(values) < period:
        return [None] * len(values)

    result: list[float | None] = [None] * len(values)

    average = sum(values[:period]) / period
    result[period - 1] = average

    for i in range(period, len(values)):

        average = wilder_average(
            average,
            values[i],
            period,
        )

        result[i] = average

    return result