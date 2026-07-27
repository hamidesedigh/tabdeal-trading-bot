"""
Relative Strength Index (RSI).
"""

from app.models import Candle


def rsi(
    candles: list[Candle],
    period: int = 14,
) -> list[float | None]:
    """
    Compute Wilder RSI.

    Parameters
    ----------
    candles
        Candle list.
    period
        RSI period.

    Returns
    -------
    list[float | None]
        RSI values.
    """

    closes = [c.close for c in candles]

    if len(closes) <= period:
        return [None] * len(closes)

    gains: list[float] = []
    losses: list[float] = []

    for i in range(1, len(closes)):
        delta = closes[i] - closes[i - 1]

        gains.append(max(delta, 0.0))
        losses.append(max(-delta, 0.0))

    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period

    values: list[float | None] = [None] * len(closes)

    if avg_loss == 0:
        values[period] = 100.0
    else:
        rs = avg_gain / avg_loss
        values[period] = 100 - (100 / (1 + rs))

    for i in range(period + 1, len(closes)):

        gain = gains[i - 1]
        loss = losses[i - 1]

        avg_gain = (
            (avg_gain * (period - 1) + gain)
            / period
        )

        avg_loss = (
            (avg_loss * (period - 1) + loss)
            / period
        )

        if avg_loss == 0:
            values[i] = 100.0
        else:
            rs = avg_gain / avg_loss
            values[i] = 100 - (100 / (1 + rs))

    return values