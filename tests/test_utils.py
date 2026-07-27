"""
Tests for indicator utilities.
"""

from app.indicators.utils import (
    closing_prices,
    high_prices,
    low_prices,
    opening_prices,
    volumes,
)
from app.models import Candle


def make_candle(
    timestamp: int,
    open_: float,
    high: float,
    low: float,
    close: float,
    volume: float,
) -> Candle:
    return Candle(
        timestamp=timestamp,
        open=open_,
        high=high,
        low=low,
        close=close,
        volume=volume,
    )


def test_closing_prices():

    candles = [
        make_candle(1, 100, 110, 95, 105, 10),
        make_candle(2, 105, 115, 100, 110, 20),
    ]

    assert closing_prices(candles) == [105, 110]


def test_opening_prices():

    candles = [
        make_candle(1, 100, 110, 95, 105, 10),
        make_candle(2, 105, 115, 100, 110, 20),
    ]

    assert opening_prices(candles) == [100, 105]


def test_high_prices():

    candles = [
        make_candle(1, 100, 110, 95, 105, 10),
        make_candle(2, 105, 115, 100, 110, 20),
    ]

    assert high_prices(candles) == [110, 115]


def test_low_prices():

    candles = [
        make_candle(1, 100, 110, 95, 105, 10),
        make_candle(2, 105, 115, 100, 110, 20),
    ]

    assert low_prices(candles) == [95, 100]


def test_volumes():

    candles = [
        make_candle(1, 100, 110, 95, 105, 10),
        make_candle(2, 105, 115, 100, 110, 20),
    ]

    assert volumes(candles) == [10, 20]