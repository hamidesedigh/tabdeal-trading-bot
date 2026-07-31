"""
Trend strength state.
"""

from __future__ import annotations

from app.indicators.adx import adx
from app.models import Candle
from app.state.models import StateSeries


def strength(
    candles: list[Candle],
    period: int = 14,
) -> StateSeries:
    """
    Trend strength based on ADX.
    """

    values = adx(
        candles,
        period=period,
    )

    return StateSeries(
        name="Strength",
        values=values,
    )