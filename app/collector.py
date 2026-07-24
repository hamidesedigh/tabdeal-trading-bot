"""
Fetch trades from Tabdeal REST API.
"""

import requests

from app.models import Trade

BASE_URL = "https://api1.tabdeal.org/r/api/v1/trades"


def build_symbol_params(symbol: str) -> dict:
    """
    Build query parameters for Tabdeal symbol.
    """

    if "_" in symbol:
        return {"tabdealSymbol": symbol}

    return {"symbol": symbol}


def normalize_trade(raw: dict) -> Trade:
    """
    Convert a raw Tabdeal trade to the project model.
    """

    return Trade(
        id=int(raw["id"]),
        price=float(raw["price"]),
        quantity=float(raw["qty"]),
        quote_quantity=float(raw["quoteQty"]),
        timestamp=int(raw["time"]),
        is_buyer_maker=bool(raw["isBuyerMaker"]),
    )


def fetch_trades(
    symbol: str,
    limit: int = 1000,
) -> list[Trade]:
    """
    Fetch latest trades from Tabdeal.
    """

    params = build_symbol_params(symbol)
    params["limit"] = limit

    response = requests.get(
        BASE_URL,
        params=params,
        timeout=10,
    )

    response.raise_for_status()

    raw_trades = response.json()

    return [normalize_trade(raw) for raw in raw_trades]