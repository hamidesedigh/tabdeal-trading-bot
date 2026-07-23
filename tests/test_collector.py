"""
Tests for app.collector.
"""

from unittest.mock import Mock, patch

import pytest
import requests

from app.collector import fetch_trades, normalize_trade
from app.models import Trade


@patch("app.collector.requests.get")
def test_fetch_trades(mock_get):
    """Fetch trades successfully."""

    url = "https://api.tabdeal.org/r/plots/trades"

    expected_data = [
        {
            "id": 189893564,
            "price": "12167471211.0000000000000000",
            "qty": "0.00021029",
            "quoteQty": "2549742.07963783",
            "time": 1784183686071,
            "isBuyerMaker": True,
        }
    ]

    response = Mock()
    response.json.return_value = expected_data
    mock_get.return_value = response

    trades = fetch_trades(url)

    assert len(trades) == 1
    assert isinstance(trades[0], Trade)

    assert trades[0].id == 189893564
    assert trades[0].price == 12167471211.0
    assert trades[0].quantity == 0.00021029
    assert trades[0].quote_quantity == 2549742.07963783
    assert trades[0].timestamp == 1784183686071
    assert trades[0].is_buyer_maker is True

    mock_get.assert_called_once_with(url, timeout=10)
    response.raise_for_status.assert_called_once()


@patch("app.collector.requests.get")
def test_fetch_trades_http_error(mock_get):
    """Raise HTTPError when API request fails."""

    response = Mock()
    response.raise_for_status.side_effect = requests.HTTPError()

    mock_get.return_value = response

    with pytest.raises(requests.HTTPError):
        fetch_trades("https://example.com")


def test_normalize_trade():
    """Normalize a raw trade from Tabdeal."""

    raw = {
        "id": 189893564,
        "price": "12167471211.0000000000000000",
        "qty": "0.00021029",
        "quoteQty": "2549742.07963783",
        "time": 1784183686071,
        "isBuyerMaker": True,
    }

    trade = normalize_trade(raw)

    assert isinstance(trade, Trade)

    assert trade.id == 189893564
    assert trade.price == 12167471211.0
    assert trade.quantity == 0.00021029
    assert trade.quote_quantity == 2549742.07963783
    assert trade.timestamp == 1784183686071
    assert trade.is_buyer_maker is True