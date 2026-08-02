"""
State models.
"""

from dataclasses import dataclass
from collections.abc import Sequence


@dataclass(slots=True)
class StateSeries:
    """
    One calculated market state.
    """

    name: str

    values: Sequence[float | None]

@dataclass(slots=True)
class MarketState:
    """
    Complete market state.
    """

    direction: StateSeries
    strength: StateSeries
    quality: StateSeries
    efficiency: StateSeries