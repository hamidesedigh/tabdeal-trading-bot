from app.indicators.ema import ema


def test_ema(candles):

    values = ema(
        candles,
        period=20,
    )

    assert len(values) == len(candles)

    assert values[-1] is not None

    assert values[19] is not None