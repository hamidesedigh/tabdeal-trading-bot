"""
Market state pipeline.
"""

from app.models import Candle
from app.state.models import StatePoint


def build_state(
    candles: list[Candle],
) -> list[StatePoint]:
    """
    Build market state.
    """

    return []