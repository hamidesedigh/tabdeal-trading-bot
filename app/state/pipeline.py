"""
Market state pipeline.
"""

from app.models import Candle

from app.state.direction import direction
from app.state.strength import strength
from app.state.quality import quality
from app.state.efficiency import efficiency

from app.state.models import MarketState


def build_state(
    candles: list[Candle],
) -> MarketState:
    """
    Build complete market state.
    """

    return MarketState(
        direction=direction(candles),
        strength=strength(candles),
        quality=quality(candles),
        efficiency=efficiency(candles),
    )