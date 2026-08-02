from app.indicators.atr import atr


def test_atr(candles):

    values = atr(
        candles,
        period=14,
    )

    assert len(values) == len(candles)

    valid = [v for v in values if v is not None]

    assert len(valid) > 0

    assert all(v >= 0 for v in valid)