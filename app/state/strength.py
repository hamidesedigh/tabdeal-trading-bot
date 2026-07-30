"""
Strength state.
"""

from app.models import Candle


def strength(
    candles: list[Candle],
) -> list[float]:

    return [0.0] * len(candles)