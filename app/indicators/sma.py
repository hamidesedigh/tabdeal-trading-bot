"""
Simple Moving Average (SMA).
"""

from app.indicators.utils import closing_prices
from app.models import Candle


def sma(
    candles: list[Candle],
    period: int = 20,
) -> list[float | None]:
    """
    Calculate Simple Moving Average.
    """

    if period <= 0:
        raise ValueError("period must be greater than zero")

    closes = closing_prices(candles)

    values: list[float | None] = []

    for index in range(len(closes)):

        if index + 1 < period:
            values.append(None)
            continue

        window = closes[index + 1 - period : index + 1]

        values.append(sum(window) / period)

    return values