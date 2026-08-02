"""
Base strategy interface.
"""

from abc import ABC
from abc import abstractmethod

from app.models import Candle
from app.models import Signal

from app.state.models import MarketState


class Strategy(ABC):
    """
    Base class for trading strategies.
    """

    @abstractmethod
    def evaluate(
        self,
        candles: list[Candle],
        state: MarketState,
    ) -> list[Signal]:
        """
        Produce trading signals.
        """