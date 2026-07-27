"""
Tests for indicator registry.
"""

from app.indicators.registry import (
    create_overlay,
    create_panel,
)
from app.indicators.sma import sma
from app.models import Candle


def make_candle(
    timestamp: int,
    close: float,
) -> Candle:

    return Candle(
        timestamp=timestamp,
        open=close,
        high=close,
        low=close,
        close=close,
        volume=1,
    )


def test_create_overlay():

    candles = [
        make_candle(1, 1),
        make_candle(2, 2),
        make_candle(3, 3),
    ]

    overlay = create_overlay(
        name="SMA3",
        func=sma,
        candles=candles,
        period=3,
    )

    assert overlay.name == "SMA3"
    assert overlay.values == [
        None,
        None,
        2.0,
    ]


def test_create_panel():

    candles = [
        make_candle(1, 1),
        make_candle(2, 2),
        make_candle(3, 3),
    ]

    panel = create_panel(
        name="SMA3",
        func=sma,
        candles=candles,
        period=3,
    )

    assert panel.name == "SMA3"
    assert panel.values == [
        None,
        None,
        2.0,
    ]