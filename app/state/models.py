"""
Market state models.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class StatePoint:
    """
    Market state for one candle.
    """

    timestamp: int

    direction: float
    strength: float
    quality: float
    efficiency: float