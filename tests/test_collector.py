"""
Tests for app.collector.
"""

from unittest.mock import Mock, patch

import pytest
import requests

from app.collector import (
    BASE_URL,
    build_symbol_params,
    fetch_trades,
    normalize_trade,
)
from app.models import Trade


def test_build_symbol_params_with_tabdeal_symbol():
    """Use tabdealSymbol when symbol contains '_'."""

    params = build_symbol_params("BTC_IRT")

    assert params == {
        "tabdealSymbol": "BTC_IRT",
    }


def test_build_symbol_params_with_symbol():
    """Use symbol when symbol has no '_'."""

    params = build_symbol_params("BTCIRT")

    assert params == {
        "symbol": "BTCIRT",
    }


def test_normalize_trade():
    """Normalize a raw trade."""

    raw = {
        "id": 1,
        "price": "100.5",
        "qty": "0.25",
        "quoteQty": "25.125",
        "time": 1000,
        "isBuyerMaker": True,
    }

    trade = normalize_trade(raw)

    assert isinstance(trade, Trade)

    assert trade.id == 1
    assert trade.price == 100.5
    assert trade.quantity == 0.25
    assert trade.quote_quantity == 25.125
    assert trade.timestamp == 1000
    assert trade.is_buyer_maker is True


@patch("app.collector.requests.get")
def test_fetch_trades(mock_get):
    """Fetch trades successfully."""

    response = Mock()

    response.json.return_value = [
        {
            "id": 1,
            "price": "100",
            "qty": "0.2",
            "quoteQty": "20",
            "time": 1,
            "isBuyerMaker": False,
        }
    ]

    mock_get.return_value = response

    trades = fetch_trades(
        symbol="BTC_IRT",
        limit=1000,
    )

    assert len(trades) == 1

    assert isinstance(trades[0], Trade)

    mock_get.assert_called_once_with(
        BASE_URL,
        params={
            "tabdealSymbol": "BTC_IRT",
            "limit": 1000,
        },
        timeout=10,
    )

    response.raise_for_status.assert_called_once()


@patch("app.collector.requests.get")
def test_fetch_trades_http_error(mock_get):
    """Raise HTTPError when request fails."""

    response = Mock()
    response.raise_for_status.side_effect = requests.HTTPError()

    mock_get.return_value = response

    with pytest.raises(requests.HTTPError):
        fetch_trades("BTC_IRT")