"""
Execution layer — wraps the official `tabdeal-python` SDK
(https://github.com/Tabdeal-Exchange/tabdeal-python).

Credentials are read from environment variables, never hardcoded or
committed to source. `dry_run` defaults to True: orders are validated
and logged but never actually sent to Tabdeal until you explicitly flip
it, and only after you trust the strategy.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field

from tabdeal.enums import OrderSides, OrderTypes
from tabdeal.exceptions import ClientException, ServerException
from tabdeal.spot import Spot

from app.models import OrderRequest, OrderResult, SymbolFilters


class ExchangeError(Exception):
    """
    Raised when the exchange rejects a request or cannot be reached.
    """


_SIDE_MAP = {
    "BUY": OrderSides.BUY,
    "SELL": OrderSides.SELL,
}

_TYPE_MAP = {
    "MARKET": OrderTypes.MARKET,
    "LIMIT": OrderTypes.LIMIT,
}


@dataclass(slots=True)
class TabdealExchange:
    """
    Thin wrapper around tabdeal.spot.Spot with dry-run support and
    parsing of exchangeInfo into the project's SymbolFilters model.
    """

    api_key: str | None = None
    api_secret: str | None = None
    dry_run: bool = True

    _client: Spot = field(init=False, repr=False)

    def __post_init__(self) -> None:

        self.api_key = self.api_key or os.environ.get("TABDEAL_API_KEY")
        self.api_secret = self.api_secret or os.environ.get(
            "TABDEAL_API_SECRET"
        )

        if not self.api_key or not self.api_secret:
            raise ExchangeError(
                "Missing Tabdeal API credentials. Set TABDEAL_API_KEY and "
                "TABDEAL_API_SECRET environment variables — never hardcode "
                "them in source or commit them to git."
            )

        self._client = Spot(self.api_key, self.api_secret)

    def get_symbol_filters(self, symbol: str) -> SymbolFilters:
        """
        Fetch and parse trading rules (tick/step size, min notional, etc)
        for a symbol from Tabdeal's exchangeInfo endpoint.
        """

        try:
            info = self._client.exchange_info(symbol=symbol)
        except (ClientException, ServerException) as exc:
            raise ExchangeError(
                f"Failed to fetch exchangeInfo for {symbol}: {exc}"
            ) from exc

        market = info[0] if isinstance(info, list) else info
        filters_by_type = {
            f["filterType"]: f for f in market["filters"]
        }

        price_filter = filters_by_type.get("PRICE_FILTER", {})
        # Prefer MARKET_LOT_SIZE since this bot trades MARKET orders;
        # fall back to LOT_SIZE if it's absent.
        lot_filter = (
            filters_by_type.get("MARKET_LOT_SIZE")
            or filters_by_type.get("LOT_SIZE", {})
        )
        notional_filter = filters_by_type.get("MIN_NOTIONAL", {})

        return SymbolFilters(
            symbol=market.get("tabdealSymbol", symbol),
            base_asset=market["baseAsset"],
            quote_asset=market["quoteAsset"],
            tick_size=float(price_filter.get("tickSize", 0) or 0),
            min_price=float(price_filter.get("minPrice", 0) or 0),
            max_price=float(price_filter.get("maxPrice", 0) or 0),
            step_size=float(lot_filter.get("stepSize", 0) or 0),
            min_qty=float(lot_filter.get("minQty", 0) or 0),
            max_qty=float(lot_filter.get("maxQty", 0) or float("inf")),
            min_notional=float(notional_filter.get("minNotional", 0) or 0),
        )

    def get_free_balance(self, asset: str) -> float:
        """
        Free (non-frozen) balance for a given asset. Returns 0.0 if the
        asset isn't found in the account balances.
        """

        try:
            account = self._client.account()
        except (ClientException, ServerException) as exc:
            raise ExchangeError(f"Failed to fetch account: {exc}") from exc

        for balance in account.get("balances", []):
            if balance["asset"] == asset:
                return float(balance["free"])

        return 0.0

    def place_order(self, order: OrderRequest) -> OrderResult:
        """
        Submit an order. In dry-run mode (default), nothing is sent to
        Tabdeal — the order is returned as accepted so the rest of the
        pipeline can be exercised safely.
        """

        if self.dry_run:
            return OrderResult(
                accepted=True,
                order=order,
                exchange_order_id=None,
                raw_response={"dry_run": True},
            )

        try:
            response = self._client.new_order(
                symbol=order.symbol,
                side=_SIDE_MAP[order.side],
                type=_TYPE_MAP[order.type],
                quantity=str(order.quantity),
            )
        except (ClientException, ServerException) as exc:
            return OrderResult(
                accepted=False,
                order=order,
                rejection_reason=str(exc),
            )

        return OrderResult(
            accepted=True,
            order=order,
            exchange_order_id=response.get("orderId"),
            raw_response=response,
        )

    def cancel_order(self, symbol: str, order_id: int) -> dict:

        try:
            return self._client.cancel_order(
                symbol=symbol,
                order_id=order_id,
            )
        except (ClientException, ServerException) as exc:
            raise ExchangeError(
                f"Failed to cancel order {order_id}: {exc}"
            ) from exc

    def get_order(self, symbol: str, order_id: int) -> dict:

        try:
            return self._client.get_order(
                symbol=symbol,
                order_id=order_id,
            )
        except (ClientException, ServerException) as exc:
            raise ExchangeError(
                f"Failed to fetch order {order_id}: {exc}"
            ) from exc

    def get_open_orders(self, symbol: str) -> list[dict]:

        try:
            return self._client.get_open_orders(symbol=symbol)
        except (ClientException, ServerException) as exc:
            raise ExchangeError(
                f"Failed to fetch open orders for {symbol}: {exc}"
            ) from exc
