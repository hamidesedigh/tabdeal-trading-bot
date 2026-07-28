"""
Moving Average Convergence Divergence (MACD).
"""

from app.models import Candle
from app.indicators.ema import ema


def macd(
    candles: list[Candle],
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9,
) -> tuple[
    list[float | None],
    list[float | None],
    list[float | None],
]:
    """
    Return:
        macd line,
        signal line,
        histogram
    """

    fast = ema(
        candles,
        period=fast_period,
    )

    slow = ema(
        candles,
        period=slow_period,
    )

    macd_line: list[float | None] = []

    #
    # MACD = EMA(fast) - EMA(slow)
    #

    for f, s in zip(fast, slow):

        if f is None or s is None:
            macd_line.append(None)
        else:
            macd_line.append(f - s)

    # The signal EMA starts only after the MACD line becomes valid. Feeding
    # placeholder zeroes into EMA would create a false signal line before
    # there is enough price history.
    first_valid_index = next(
        (
            index
            for index, value in enumerate(macd_line)
            if value is not None
        ),
        len(candles),
    )

    valid_macd_candles = [
        Candle(
            timestamp=candle.timestamp,
            open=value,
            high=value,
            low=value,
            close=value,
            volume=0,
        )
        for candle, value in zip(
            candles[first_valid_index:],
            macd_line[first_valid_index:],
        )
        if value is not None
    ]

    valid_signal = ema(
        valid_macd_candles,
        period=signal_period,
    )

    signal: list[float | None] = [None] * len(candles)

    for index, value in enumerate(valid_signal, start=first_valid_index):
        signal[index] = value

    histogram: list[float | None] = []

    for m, s in zip(macd_line, signal):

        if m is None or s is None:
            histogram.append(None)
        else:
            histogram.append(m - s)

    return (
        macd_line,
        signal,
        histogram,
    )
