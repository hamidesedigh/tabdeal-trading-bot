"""
Exponential Moving Average (EMA).
"""

from app.models import Candle


def ema(
    candles: list[Candle],
    period: int,
) -> list[float | None]:
    """
    Compute the Exponential Moving Average.

    Parameters
    ----------
    candles
        Input candles.
    period
        EMA period.

    Returns
    -------
    list[float | None]
        EMA values aligned with candles.
    """

    if period <= 0:
        raise ValueError("period must be positive.")

    if len(candles) < period:
        return [None] * len(candles)

    closes = [c.close for c in candles]

    multiplier = 2 / (period + 1)

    values: list[float | None] = [None] * len(closes)

    #
    # First EMA starts from SMA(period)
    #
    first = sum(closes[:period]) / period
    values[period - 1] = first

    previous = first

    for i in range(period, len(closes)):

        current = (
            (closes[i] - previous) * multiplier
            + previous
        )

        values[i] = current
        previous = current

    return values