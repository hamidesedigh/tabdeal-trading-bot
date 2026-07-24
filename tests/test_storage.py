"""
Tests for app.storage.
"""

from pathlib import Path

import app.storage as storage
from app.models import Trade


def make_trade(trade_id: int) -> Trade:
    """Create a sample trade."""

    return Trade(
        id=trade_id,
        price=100.0 + trade_id,
        quantity=1.0,
        quote_quantity=100.0,
        timestamp=trade_id * 1000,
        is_buyer_maker=False,
    )


def test_initialize_database(tmp_path):
    """Database file should be created."""

    storage.DATABASE_PATH = tmp_path / "trades.db"

    storage.initialize_database()

    assert storage.DATABASE_PATH.exists()


def test_insert_and_count_trades(tmp_path):
    """Trades should be inserted."""

    storage.DATABASE_PATH = tmp_path / "trades.db"

    storage.initialize_database()

    trades = [
        make_trade(1),
        make_trade(2),
        make_trade(3),
    ]

    storage.insert_trades(trades)

    assert storage.count_trades() == 3


def test_duplicate_trade_is_ignored(tmp_path):
    """Duplicate trade IDs should be ignored."""

    storage.DATABASE_PATH = tmp_path / "trades.db"

    storage.initialize_database()

    trade = make_trade(1)

    storage.insert_trades([trade])
    storage.insert_trades([trade])

    assert storage.count_trades() == 1


def test_load_trades(tmp_path):
    """Trades should be loaded from database."""

    storage.DATABASE_PATH = tmp_path / "trades.db"

    storage.initialize_database()

    trades = [
        make_trade(1),
        make_trade(2),
    ]

    storage.insert_trades(trades)

    loaded = storage.load_trades()

    assert len(loaded) == 2

    assert loaded[0].id == 1
    assert loaded[1].id == 2


def test_load_trades_limit(tmp_path):
    """Limit should restrict number of loaded trades."""

    storage.DATABASE_PATH = tmp_path / "trades.db"

    storage.initialize_database()

    trades = [
        make_trade(1),
        make_trade(2),
        make_trade(3),
    ]

    storage.insert_trades(trades)

    loaded = storage.load_trades(limit=2)

    assert len(loaded) == 2

    assert loaded[0].id == 1
    assert loaded[1].id == 2