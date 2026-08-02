from app.indicators.sma import sma


def test_sma(candles):

    values = sma(
        candles,
        period=20,
    )

    assert len(values) == len(candles)

    assert values[-1] is not None

    assert all(
        v is None
        for v in values[:19]
    )