"""
Strategy pipeline.
"""

from app.models import Candle
from app.models import Signal

from app.state.models import MarketState

from app.strategy.trend_following import TrendFollowingStrategy


def build_signals(
    candles: list[Candle],
    state: MarketState,
) -> list[Signal]:
    """
    Execute trading strategy.
    """

    strategy = TrendFollowingStrategy()

    return strategy.evaluate(
        candles,
        state,
    )