"""
Average Directional Index (ADX).

Wilder's trend strength indicator.
"""

from __future__ import annotations

from app.models import Candle

from app.indicators.atr import atr
from app.indicators.utils import (
    wilder_average,
    wilder_smooth,
)


def adx(
    candles: list[Candle],
    period: int = 14,
) -> list[float | None]:
    """
    Calculate Average Directional Index.

    Parameters
    ----------
    candles
        OHLC candles.

    period
        ADX period.

    Returns
    -------
    list[float | None]
        ADX values.
    """

    if len(candles) < period * 2:
        return [None] * len(candles)

    #
    # ATR
    #

    atr_values = atr(
        candles,
        period,
    )

    #
    # Directional Movement
    #

    plus_dm = [0.0]
    minus_dm = [0.0]

    for i in range(1, len(candles)):

        current = candles[i]
        previous = candles[i - 1]

        up_move = current.high - previous.high
        down_move = previous.low - current.low

        plus_dm.append(
            up_move
            if up_move > down_move and up_move > 0
            else 0.0
        )

        minus_dm.append(
            down_move
            if down_move > up_move and down_move > 0
            else 0.0
        )

    #
    # Wilder smoothing
    #

    plus_dm_smoothed = wilder_smooth(
        plus_dm,
        period,
    )

    minus_dm_smoothed = wilder_smooth(
        minus_dm,
        period,
    )

    #
    # Directional Indicators
    #

    plus_di: list[float | None] = []
    minus_di: list[float | None] = []

    for atr_value, plus_value, minus_value in zip(
        atr_values,
        plus_dm_smoothed,
        minus_dm_smoothed,
    ):

        if (
            atr_value is None
            or plus_value is None
            or minus_value is None
            or atr_value == 0
        ):
            plus_di.append(None)
            minus_di.append(None)
            continue

        plus_di.append(
            100 * plus_value / atr_value
        )

        minus_di.append(
            100 * minus_value / atr_value
        )

    #
    # DX
    #

    dx: list[float | None] = []

    for plus_value, minus_value in zip(
        plus_di,
        minus_di,
    ):

        if (
            plus_value is None
            or minus_value is None
        ):
            dx.append(None)
            continue

        total = plus_value + minus_value

        if total == 0:
            dx.append(0.0)
            continue

        dx.append(
            100
            * abs(plus_value - minus_value)
            / total
        )

    #
    # ADX
    #

    result: list[float | None] = [None] * len(dx)

    start = None

    for i in range(len(dx) - period + 1):

        window = dx[i : i + period]

        if all(v is not None for v in window):
            start = i
            break

    if start is None:
        return result

    average = (
        sum(window)
        / period
    )

    index = start + period - 1

    result[index] = average

    for i in range(index + 1, len(dx)):

        if dx[i] is None:
            continue

        average = wilder_average(
            average,
            dx[i],
            period,
        )

        result[i] = average

    return result