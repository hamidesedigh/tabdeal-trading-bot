"""
Convert trades to OHLC candles.
"""

from collections import defaultdict

from app.models import Candle, Trade


TIMEFRAME_SECONDS = {
    "1min": 60,
    "5min": 300,
    "15min": 900,
    "30min": 1800,
    "1h": 3600,
    "4h": 14400,
    "1d": 86400,
}


def _bucket_timestamp(timestamp_ms: int, timeframe: str) -> int:
    """
    Round timestamp down to the beginning of its timeframe bucket.
    """

    seconds = timestamp_ms // 1000
    bucket = seconds // TIMEFRAME_SECONDS[timeframe]

    return bucket * TIMEFRAME_SECONDS[timeframe] * 1000


def build_candles(
    trades: list[Trade],
    timeframe: str = "1min",
) -> list[Candle]:
    """
    Build OHLC candles from trades.
    """

    if not trades:
        return []

    if timeframe not in TIMEFRAME_SECONDS:
        raise ValueError(f"Unsupported timeframe: {timeframe}")

    # Ensure trades are ordered by time.
    trades = sorted(trades, key=lambda trade: trade.timestamp)

    grouped = defaultdict(list)

    for trade in trades:
        bucket = _bucket_timestamp(
            trade.timestamp,
            timeframe,
        )
        grouped[bucket].append(trade)

    candles = []

    for timestamp in sorted(grouped.keys()):

        bucket_trades = grouped[timestamp]

        prices = [trade.price for trade in bucket_trades]

        candle = Candle(
            timestamp=timestamp,
            open=prices[0],
            high=max(prices),
            low=min(prices),
            close=prices[-1],
            volume=sum(
                trade.quantity
                for trade in bucket_trades
            ),
        )

        candles.append(candle)

    return candles