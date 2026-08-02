"""
Moving Average Convergence Divergence (MACD).
"""

from __future__ import annotations

from app.models import Candle

from app.indicators.ema import (
    ema,
    ema_values,
)


def macd(
    candles: list[Candle],
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9,
) -> tuple[
    list[float | None],
    list[float | None],
    list[float | None],
]:
    """
    Return

    - MACD line
    - Signal line
    - Histogram
    """

    fast = ema(
        candles,
        period=fast_period,
    )

    slow = ema(
        candles,
        period=slow_period,
    )

    macd_line: list[float | None] = []

    for fast_value, slow_value in zip(
        fast,
        slow,
    ):

        if (
            fast_value is None
            or slow_value is None
        ):
            macd_line.append(None)
        else:
            macd_line.append(
                fast_value - slow_value
            )

    #
    # Signal EMA
    #

    first_valid = next(
        (
            index
            for index, value in enumerate(macd_line)
            if value is not None
        ),
        len(macd_line),
    )

    valid_macd = [
        value
        for value in macd_line[first_valid:]
        if value is not None
    ]

    valid_signal = ema_values(
        valid_macd,
        signal_period,
    )

    signal: list[float | None] = [None] * len(macd_line)

    for index, value in enumerate(
        valid_signal,
        start=first_valid,
    ):
        signal[index] = value

    #
    # Histogram
    #

    histogram: list[float | None] = []

    for macd_value, signal_value in zip(
        macd_line,
        signal,
    ):

        if (
            macd_value is None
            or signal_value is None
        ):
            histogram.append(None)
        else:
            histogram.append(
                macd_value - signal_value
            )

    return (
        macd_line,
        signal,
        histogram,
    )