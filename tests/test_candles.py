"""
Tests for app.candles.
"""

from app.candles import build_candles
from app.models import Trade


def make_trade(price, quantity, timestamp):

    return Trade(
        id=timestamp,
        price=price,
        quantity=quantity,
        quote_quantity=price * quantity,
        timestamp=timestamp,
        is_buyer_maker=False,
    )


def test_build_single_candle():

    trades = [
        make_trade(100, 1, 0),
        make_trade(110, 2, 10000),
        make_trade(90, 1, 20000),
        make_trade(105, 1, 50000),
    ]

    candles = build_candles(trades)

    assert len(candles) == 1

    candle = candles[0]

    assert candle.open == 100
    assert candle.high == 110
    assert candle.low == 90
    assert candle.close == 105
    assert candle.volume == 5