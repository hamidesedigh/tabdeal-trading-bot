"""
Quality state.
"""

from app.models import Candle


def quality(
    candles: list[Candle],
) -> list[float]:

    return [0.0] * len(candles)