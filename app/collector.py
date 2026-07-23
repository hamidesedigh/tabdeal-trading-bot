"""
Fetch trades from Tabdeal REST API.
"""

from typing import List

import requests

from app.models import Trade


def fetch_trades(url: str) -> List[Trade]:
    """
    Fetch latest trades from Tabdeal.

    Parameters
    ----------
    url : str
        REST endpoint.

    Returns
    -------
    list[Trade]
    """

    response = requests.get(url, timeout=10)
    response.raise_for_status()

    raw_trades = response.json()

    return [normalize_trade(raw) for raw in raw_trades]


def normalize_trade(raw: dict) -> Trade:
    """
    Convert Tabdeal trade into the project model.
    """

    return Trade(
        id=int(raw["id"]),
        price=float(raw["price"]),
        quantity=float(raw["qty"]),
        quote_quantity=float(raw["quoteQty"]),
        timestamp=int(raw["time"]),
        is_buyer_maker=bool(raw["isBuyerMaker"]),
    )