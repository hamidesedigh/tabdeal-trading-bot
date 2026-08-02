"""
Relative Strength Index (RSI).

Uses Wilder's smoothing.
"""

from __future__ import annotations

from app.models import Candle
from app.indicators.utils import (
    closing_prices,
    wilder_average,
)


def rsi(
    candles: list[Candle],
    period: int = 14,
) -> list[float | None]:
    """
    Calculate Relative Strength Index (RSI).

    Parameters
    ----------
    candles
        Input candles.

    period
        RSI period.

    Returns
    -------
    list[float | None]
        RSI values aligned with candles.
    """

    closes = closing_prices(candles)

    if len(closes) <= period:
        return [None] * len(closes)

    gains: list[float] = []
    losses: list[float] = []

    #
    # Price changes
    #

    for i in range(1, len(closes)):

        delta = closes[i] - closes[i - 1]

        gains.append(
            max(delta, 0.0)
        )

        losses.append(
            max(-delta, 0.0)
        )

    #
    # First averages
    #

    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period

    values: list[float | None] = [None] * len(closes)

    #
    # First RSI
    #

    if avg_loss == 0:
        values[period] = 100.0
    else:
        rs = avg_gain / avg_loss
        values[period] = 100 - (100 / (1 + rs))

    #
    # Remaining values
    #

    for i in range(period + 1, len(closes)):

        avg_gain = wilder_average(
            avg_gain,
            gains[i - 1],
            period,
        )

        avg_loss = wilder_average(
            avg_loss,
            losses[i - 1],
            period,
        )

        if avg_loss == 0:
            values[i] = 100.0
            continue

        rs = avg_gain / avg_loss

        values[i] = (
            100
            - (100 / (1 + rs))
        )

    return values