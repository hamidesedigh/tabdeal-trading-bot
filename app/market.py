"""
Trading engine.
"""

from app.candles import build_candles
from app.collector import fetch_trades
from app.models import Candle
from app.storage import (
    initialize_database,
    insert_trades,
    load_trades,
)

def load_market(
    timeframe="1min",
) -> list[Candle]:
    # Market Data Pipeline

    trades = load_trades()

    return build_candles(
        trades,
        timeframe,
    )


def run_cycle(
    symbol: str,
    limit: int,
) -> list[Candle]:
    """
    Execute one trading cycle. Live Engine
    """

    initialize_database()

    latest = fetch_trades(
        symbol=symbol,
        limit=limit,
    )

    insert_trades(latest)

    trades = load_trades()

    candles = build_candles(trades)

    return candles