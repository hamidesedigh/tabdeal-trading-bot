"""
Common data models.
"""

from dataclasses import dataclass
from typing import Sequence , Any
from collections.abc import Callable


@dataclass(slots=True, frozen=True)
class Trade:
    """
    Standard trade model used across the project.
    """

    id: int
    price: float
    quantity: float
    quote_quantity: float
    timestamp: int
    is_buyer_maker: bool

@dataclass(slots=True, frozen=True)
class Candle:
    """
    OHLCV candle.
    """

    timestamp: int

    open: float
    high: float
    low: float
    close: float

    volume: float

@dataclass(slots=True)
class OverlayIndicator:
    name: str
    values: Sequence[float]

    color: str = "tab:blue"
    linewidth: float = 1.5
    linestyle: str = "-"

    plot_type: str = "line"      # line | scatter
    marker: str = "o"


@dataclass(slots=True)
class PanelIndicator:
    name: str
    values: Sequence[float]

    color: str = "tab:blue"
    linewidth: float = 1.5
    linestyle: str = "-"

    plot_type: str = "line"
    marker: str = "o"

@dataclass(slots=True, frozen=True)
class IndicatorSpec:
    """
    Specification for computing an indicator.
    """

    name: str

    func: Callable[..., list[float | None]]

    kwargs: dict[str, Any]