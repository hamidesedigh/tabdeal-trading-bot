"""
Indicator registry helpers.

These helpers wrap raw indicator functions into plotting models.
"""

from collections.abc import Callable
from typing import Any

from app.models import (
    Candle,
    OverlayIndicator,
    PanelIndicator,
)


def create_overlay(
    *,
    name: str,
    func: Callable[..., list[float | None]],
    candles: list[Candle],
    color: str | None = None,
    linewidth: float = 1.2,
    linestyle: str = "-",
    plot_type: str = "line",
    marker: str = "o",
    **kwargs: Any,
) -> OverlayIndicator:
    """
    Build an OverlayIndicator from an indicator function.
    """

    values = func(
        candles,
        **kwargs,
    )

    return OverlayIndicator(
        name=name,
        values=values,
        color=color,
        linewidth=linewidth,
        linestyle=linestyle,
        plot_type=plot_type,
        marker=marker,
    )


def create_panel(
    *,
    name: str,
    func: Callable[..., list[float | None]],
    candles: list[Candle],
    color: str | None = None,
    linewidth: float = 1.2,
    linestyle: str = "-",
    plot_type: str = "line",
    marker: str = "o",
    **kwargs: Any,
) -> PanelIndicator:
    """
    Build a PanelIndicator from an indicator function.
    """

    values = func(
        candles,
        **kwargs,
    )

    return PanelIndicator(
        name=name,
        values=values,
        color=color,
        linewidth=linewidth,
        linestyle=linestyle,
        plot_type=plot_type,
        marker=marker,
    )