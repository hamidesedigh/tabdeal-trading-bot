from app.indicators.rsi import rsi
from app.models import Candle


def make_candles():

    candles = []

    for i in range(100):

        candles.append(
            Candle(
                timestamp=i,
                open=100 + i,
                high=101 + i,
                low=99 + i,
                close=100 + i,
                volume=1,
            )
        )

    return candles


def test_rsi_length():

    candles = make_candles()

    values = rsi(candles)

    assert len(values) == len(candles)


def test_rsi_prefix():

    candles = make_candles()

    values = rsi(candles)

    assert values[:14] == [None] * 14


def test_rsi_range():

    candles = make_candles()

    values = rsi(candles)

    for value in values:

        if value is not None:

            assert 0 <= value <= 100