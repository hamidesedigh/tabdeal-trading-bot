"""
Efficiency state.

Efficiency measures directional movement relative to volatility.

Efficiency = Regression Slope / ATR
"""

from __future__ import annotations

from app.models import Candle
from app.state.models import StateSeries
from app.state.utils import linear_regression

from app.indicators.atr import atr


def efficiency(
    candles: list[Candle],
    period: int = 20,
) -> StateSeries:
    """
    Calculate market efficiency.

    Efficiency = slope / ATR

    Returns
    -------
    StateSeries
    """

    closes = [c.close for c in candles]

    atr_values = atr(
        candles,
        period,
    )

    values: list[float | None] = []

    for i in range(len(candles)):

        if i < period - 1:
            values.append(None)
            continue

        atr_value = atr_values[i]

        if atr_value is None or atr_value == 0:
            values.append(None)
            continue

        window = closes[
            i - period + 1 : i + 1
        ]

        slope, _, _ = linear_regression(
            window,
        )

        values.append(
            slope / atr_value
        )

    return StateSeries(
        name="Efficiency",
        values=values,
    )