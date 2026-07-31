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