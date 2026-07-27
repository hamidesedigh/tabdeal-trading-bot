"""
Tests for EMA indicator.
"""

import pytest

from app.indicators.ema import ema
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


def test_empty():

    assert ema([], 5) == []


def test_invalid_period():

    with pytest.raises(ValueError):
        ema([], 0)


def test_short_series():

    candles = [
        make_candle(1, 1),
        make_candle(2, 2),
    ]

    assert ema(candles, 5) == [
        None,
        None,
    ]


def test_length():

    candles = [
        make_candle(i, float(i))
        for i in range(1, 21)
    ]

    result = ema(candles, 5)

    assert len(result) == len(candles)


def test_first_ema_equals_sma():

    candles = [
        make_candle(1, 10),
        make_candle(2, 20),
        make_candle(3, 30),
        make_candle(4, 40),
        make_candle(5, 50),
    ]

    result = ema(candles, 5)

    assert result == [
        None,
        None,
        None,
        None,
        30.0,
    ]


def test_monotonic_increase():

    candles = [
        make_candle(i, float(i))
        for i in range(1, 11)
    ]

    result = ema(candles, 3)

    previous = None

    for value in result:

        if value is None:
            continue

        if previous is not None:
            assert value > previous

        previous = value