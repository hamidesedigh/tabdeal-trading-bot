"""
Tests for app.engine.
"""

from unittest.mock import patch

from app.engine import run_cycle
from app.models import Candle, Trade


def make_trade(trade_id: int) -> Trade:
    """Create a sample trade."""

    return Trade(
        id=trade_id,
        price=100.0,
        quantity=1.0,
        quote_quantity=100.0,
        timestamp=trade_id * 60000,
        is_buyer_maker=False,
    )


@patch("app.engine.load_trades")
@patch("app.engine.insert_trades")
@patch("app.engine.fetch_trades")
@patch("app.engine.initialize_database")
def test_run_cycle(
    mock_initialize,
    mock_fetch,
    mock_insert,
    mock_load,
):
    """Run one engine cycle."""

    latest = [
        make_trade(1),
        make_trade(2),
    ]

    mock_fetch.return_value = latest
    mock_load.return_value = latest

    candles = run_cycle(
        symbol="BTC_IRT",
        limit=1000,
    )

    mock_initialize.assert_called_once()

    mock_fetch.assert_called_once_with(
        symbol="BTC_IRT",
        limit=1000,
    )

    mock_insert.assert_called_once_with(latest)

    mock_load.assert_called_once()

    assert len(candles) == 2

    assert isinstance(candles[0], Candle)