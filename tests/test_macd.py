from app.indicators.macd import macd


def test_macd(candles):

    macd_line, signal, histogram = macd(candles)

    assert len(macd_line) == len(candles)

    assert len(signal) == len(candles)

    assert len(histogram) == len(candles)

    valid_macd = [
        v
        for v in macd_line
        if v is not None
    ]

    valid_signal = [
        v
        for v in signal
        if v is not None
    ]

    valid_histogram = [
        v
        for v in histogram
        if v is not None
    ]

    assert len(valid_macd) > 0

    assert len(valid_signal) > 0

    assert len(valid_histogram) > 0