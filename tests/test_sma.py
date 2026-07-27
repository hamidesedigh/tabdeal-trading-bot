"""
Tests for SMA indicator.
"""

import pytest

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


def test_sma_period_3():

    candles = [
        make_candle(1, 1),
        make_candle(2, 2),
        make_candle(3, 3),
        make_candle(4, 4),
        make_candle(5, 5),
    ]

    result = sma(
        candles,
        period=3,
    )

    assert result == [
        None,
        None,
        2.0,
        3.0,
        4.0,
    ]


def test_sma_period_1():

    candles = [
        make_candle(1, 10),
        make_candle(2, 20),
    ]

    result = sma(
        candles,
        period=1,
    )

    assert result == [
        10.0,
        20.0,
    ]


def test_empty_input():

    assert sma([], period=5) == []


def test_invalid_period():

    with pytest.raises(ValueError):
        sma([], period=0)