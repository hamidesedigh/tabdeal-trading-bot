"""
Tests for app.candles.
"""

import pytest

from app.candles import build_candles
from app.models import Trade


def make_trade(
    trade_id: int,
    timestamp: int,
    price: float,
    quantity: float = 1.0,
) -> Trade:
    """Create a sample trade."""

    return Trade(
        id=trade_id,
        price=price,
        quantity=quantity,
        quote_quantity=price * quantity,
        timestamp=timestamp,
        is_buyer_maker=False,
    )


def test_empty_trade_list():
    """Empty input should return an empty candle list."""

    candles = build_candles([])

    assert candles == []


def test_single_candle():
    """Trades within one minute should produce one candle."""

    trades = [
        make_trade(1, 0, 100),
        make_trade(2, 10_000, 110),
        make_trade(3, 20_000, 90),
        make_trade(4, 50_000, 105),
    ]

    candles = build_candles(trades)

    assert len(candles) == 1

    candle = candles[0]

    assert candle.open == 100
    assert candle.high == 110
    assert candle.low == 90
    assert candle.close == 105
    assert candle.volume == 4.0


def test_multiple_candles():
    """Trades in different minutes should produce multiple candles."""

    trades = [
        make_trade(1, 0, 100),
        make_trade(2, 20_000, 105),
        make_trade(3, 61_000, 110),
        make_trade(4, 70_000, 120),
    ]

    candles = build_candles(trades)

    assert len(candles) == 2

    assert candles[0].open == 100
    assert candles[0].close == 105

    assert candles[1].open == 110
    assert candles[1].close == 120


def test_unsorted_trades():
    """Trades should be sorted automatically."""

    trades = [
        make_trade(3, 20_000, 90),
        make_trade(1, 0, 100),
        make_trade(4, 50_000, 105),
        make_trade(2, 10_000, 110),
    ]

    candles = build_candles(trades)

    candle = candles[0]

    assert candle.open == 100
    assert candle.high == 110
    assert candle.low == 90
    assert candle.close == 105


def test_volume_sum():
    """Volume should equal the sum of trade quantities."""

    trades = [
        make_trade(1, 0, 100, quantity=1.5),
        make_trade(2, 5_000, 101, quantity=2.0),
        make_trade(3, 10_000, 102, quantity=0.5),
    ]

    candles = build_candles(trades)

    assert candles[0].volume == 4.0


def test_five_minute_timeframe():
    """Five-minute timeframe should merge all trades."""

    trades = [
        make_trade(1, 0, 100),
        make_trade(2, 60_000, 105),
        make_trade(3, 120_000, 110),
        make_trade(4, 240_000, 120),
    ]

    candles = build_candles(
        trades,
        timeframe="5min",
    )

    assert len(candles) == 1

    candle = candles[0]

    assert candle.open == 100
    assert candle.close == 120
    assert candle.high == 120
    assert candle.low == 100


def test_invalid_timeframe():
    """Unsupported timeframe should raise ValueError."""

    trades = [
        make_trade(1, 0, 100),
    ]

    with pytest.raises(ValueError):
        build_candles(
            trades,
            timeframe="10seconds",
        )