"""
Average Directional Index (ADX).

Wilder's trend strength indicator.
"""

from __future__ import annotations

from app.models import Candle


def _wilder_smooth(
    values: list[float],
    period: int,
) -> list[float | None]:
    """
    Wilder smoothing.
    """

    result: list[float | None] = [None] * len(values)

    #
    # First smoothed value
    #

    smoothed = sum(values[:period])

    result[period - 1] = smoothed

    #
    # Remaining values
    #

    for i in range(period, len(values)):

        smoothed = (
            smoothed
            - smoothed / period
            + values[i]
        )

        result[i] = smoothed

    return result

def _wilder_average(
    values: list[float | None],
    period: int,
) -> list[float | None]:
    """
    Wilder moving average.
    """

    result: list[float | None] = [None] * len(values)

    #
    # find first complete window
    #

    start = None

    for i in range(len(values) - period + 1):

        window = values[i:i + period]

        if all(v is not None for v in window):
            start = i
            break

    if start is None:
        return result

    #
    # first ADX
    #

    average = sum(window) / period

    result[start + period - 1] = average

    #
    # Wilder smoothing
    #

    for i in range(start + period, len(values)):

        if values[i] is None:
            continue

        average = (
            (average * (period - 1))
            + values[i]
        ) / period

        result[i] = average

    return result


def adx(
    candles: list[Candle],
    period: int = 14,
) -> list[float | None]:
    """
    Calculate Average Directional Index.

    Parameters
    ----------
    candles
        OHLC candles.
    period
        Wilder smoothing period.

    Returns
    -------
    list[float | None]
        ADX values.
    """

    if len(candles) < period * 2:
        return [None] * len(candles)

    #
    # Step 1
    # Calculate True Range (TR)
    #

    tr: list[float] = []

    for i, candle in enumerate(candles):

        if i == 0:
            #
            # First candle has no previous close.
            #
            tr.append(
                candle.high - candle.low
            )
            continue

        previous_close = candles[i - 1].close

        tr.append(
            max(
                candle.high - candle.low,
                abs(candle.high - previous_close),
                abs(candle.low - previous_close),
            )
        )

    #
    # Temporary debug
    #

    print("TR last 5:", tr[-5:])

    #
    #
    # Step 2
    # Calculate Directional Movement
    #

    plus_dm: list[float] = [0.0]
    minus_dm: list[float] = [0.0]

    for i in range(1, len(candles)):

        current = candles[i]
        previous = candles[i - 1]

        up_move = (
            current.high
            - previous.high
        )

        down_move = (
            previous.low
            - current.low
        )

        if up_move > down_move and up_move > 0:
            plus_dm.append(up_move)
        else:
            plus_dm.append(0.0)

        if down_move > up_move and down_move > 0:
            minus_dm.append(down_move)
        else:
            minus_dm.append(0.0)

    print("TR      :", tr[-5:])
    print("+DM     :", plus_dm[-5:])
    print("-DM     :", minus_dm[-5:])

    #
    # Step 3
    # Wilder smoothing
    #

    tr_smoothed = _wilder_smooth(
        tr,
        period,
    )

    plus_dm_smoothed = _wilder_smooth(
        plus_dm,
        period,
    )

    minus_dm_smoothed = _wilder_smooth(
        minus_dm,
        period,
    )

    print("ATR smooth :", tr_smoothed[-5:])
    print("+DM smooth :", plus_dm_smoothed[-5:])
    print("-DM smooth :", minus_dm_smoothed[-5:])

    #
    # Step 4
    # Calculate Directional Indicators
    #

    plus_di: list[float | None] = []
    minus_di: list[float | None] = []

    for atr, plus, minus in zip(
        tr_smoothed,
        plus_dm_smoothed,
        minus_dm_smoothed,
    ):

        if atr is None or atr == 0:
            plus_di.append(None)
            minus_di.append(None)
            continue

        plus_di.append(
            100 * plus / atr
        )

        minus_di.append(
            100 * minus / atr
        )

    print("+DI:", plus_di[-5:])
    print("-DI:", minus_di[-5:])

    #
    # Step 5
    # Calculate DX
    #

    dx: list[float | None] = []

    for plus, minus in zip(
        plus_di,
        minus_di,
    ):

        if plus is None or minus is None:
            dx.append(None)
            continue

        total = plus + minus

        if total == 0:
            dx.append(0.0)
            continue

        dx.append(
            100 * abs(plus - minus) / total
        )

    print("DX:", dx[-5:])

    #
    # Step 6
    # Calculate ADX
    #

    adx_values = _wilder_average(
        dx,
        period,
    )

    print("ADX:", adx_values[-10:])

    return adx_values

    return [None] * len(candles)