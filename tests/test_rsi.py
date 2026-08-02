from app.indicators.rsi import rsi


def test_rsi(candles):

    values = rsi(
        candles,
        period=14,
    )

    assert len(values) == len(candles)

    valid = [v for v in values if v is not None]

    assert len(valid) > 0

    assert all(
        0 <= v <= 100
        for v in valid
    )