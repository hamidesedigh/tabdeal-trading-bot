"""
Tests for app.storage.
"""

from app.models import Trade
from app.storage import merge_trades


def make_trade(trade_id: int) -> Trade:
    """Create a sample trade."""

    return Trade(
        id=trade_id,
        price=100.0 + trade_id,
        quantity=1.0,
        quote_quantity=100.0,
        timestamp=trade_id,
        is_buyer_maker=False,
    )


def test_merge_trades():
    """Merge two different trade lists."""

    existing = [
        make_trade(1),
        make_trade(2),
    ]

    new = [
        make_trade(3),
        make_trade(4),
    ]

    merged = merge_trades(existing, new)

    assert len(merged) == 4
    assert [trade.id for trade in merged] == [1, 2, 3, 4]


def test_remove_duplicate_trade():
    """Duplicate trades should be removed."""

    existing = [
        make_trade(1),
        make_trade(2),
    ]

    new = [
        make_trade(2),
        make_trade(3),
    ]

    merged = merge_trades(existing, new)

    assert len(merged) == 3
    assert [trade.id for trade in merged] == [1, 2, 3]


def test_sort_trades():
    """Trades should be sorted by ID."""

    existing = [
        make_trade(10),
    ]

    new = [
        make_trade(2),
        make_trade(5),
        make_trade(1),
    ]

    merged = merge_trades(existing, new)

    assert [trade.id for trade in merged] == [1, 2, 5, 10]