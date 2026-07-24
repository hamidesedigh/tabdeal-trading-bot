"""
Build OHLC candles from trades.
"""

from app.models import Candle, Trade


def build_candles(trades: list[Trade]) -> list[Candle]:
    """
    Build 1-minute candles from trades.
    """

    if not trades:
        return []

    buckets: dict[int, list[Trade]] = {}

    for trade in trades:

        # 60000 ms = 1 minute
        minute = trade.timestamp // 60000

        buckets.setdefault(minute, []).append(trade)

    candles = []

    for minute in sorted(buckets):

        bucket = buckets[minute]

        candles.append(
            Candle(
                open_time=minute * 60000,
                open=bucket[0].price,
                high=max(t.price for t in bucket),
                low=min(t.price for t in bucket),
                close=bucket[-1].price,
                volume=sum(t.quantity for t in bucket),
            )
        )

    return candles