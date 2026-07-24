"""
Store and merge trades.
"""

from app.models import Trade


def merge_trades(
    existing: list[Trade],
    new: list[Trade],
) -> list[Trade]:
    """
    Merge existing and new trades.

    Duplicate trades are removed based on trade ID.
    The result is sorted by trade ID.
    """

    trades = {trade.id: trade for trade in existing}

    for trade in new:
        trades[trade.id] = trade

    return sorted(trades.values(), key=lambda trade: trade.id)