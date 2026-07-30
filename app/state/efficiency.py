"""
Efficiency state.
"""

from app.models import Candle


def efficiency(
    candles: list[Candle],
) -> list[float]:

    return [0.0] * len(candles)