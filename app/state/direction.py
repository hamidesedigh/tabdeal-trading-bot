"""
Direction state.
"""

from app.models import Candle


def direction(
    candles: list[Candle],
) -> list[float]:

    return [0.0] * len(candles)