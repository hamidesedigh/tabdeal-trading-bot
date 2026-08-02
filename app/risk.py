"""
Risk management and order sizing.

Turns a Signal into a sized, exchange-valid OrderRequest, or rejects it.
This is deliberately one component rather than a separate "risk manager"
and "order builder": position sizing, stop-loss distance, exchange
precision rounding, and filter validation all depend on each other to
produce a single valid order, so splitting them would just mean passing
the same state back and forth between two objects.

Responsibilities:
  - position sizing based on risk-per-trade and stop-loss distance
  - stop-loss / take-profit price calculation (ATR-based)
  - rounding price/quantity to the exchange's tick/step size
  - enforcing exchange filters (min/max qty, min notional)
  - a hard cap on position size regardless of what risk sizing implies
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from app.models import Candle, OrderRequest, Signal, SymbolFilters


class RiskRejected(Exception):
    """
    Raised when a signal cannot be turned into a valid order — e.g.
    insufficient balance, below exchange minimums, missing ATR at the
    signal's timestamp, or an invalid stop distance.
    """


@dataclass(slots=True)
class RiskConfig:
    """
    Tunable risk parameters. Defaults are conservative starting points —
    tune them once you have more backtest history to validate against.
    """

    # Fraction of free quote-asset balance risked on a single trade
    # (the amount you'd lose if the stop-loss is hit).
    risk_per_trade_pct: float = 0.01        # 1%

    # Hard cap on position notional regardless of stop distance, as a
    # fraction of free balance. Protects against a very tight ATR-based
    # stop implying an oversized position.
    max_position_pct: float = 0.25          # 25% of free balance

    # ATR multiples used to place stop-loss / take-profit.
    stop_loss_atr_multiplier: float = 1.5
    take_profit_atr_multiplier: float = 3.0

    # Safety margin applied to free balance for MARKET buys, since the
    # exact fill price/fees aren't known in advance.
    balance_safety_margin: float = 0.995    # use up to 99.5% of what's free


def round_down_to_step(value: float, step: float) -> float:
    """
    Round `value` down to the nearest multiple of `step`.

    Exchanges reject quantities that aren't a multiple of stepSize, and
    rounding up could request more than the account holds — so quantity
    always rounds down.
    """

    if step <= 0:
        return value

    steps = math.floor(value / step)

    return round(steps * step, 12)


def round_to_tick(value: float, tick: float) -> float:
    """
    Round `value` to the nearest multiple of `tick` (for LIMIT prices).
    """

    if tick <= 0:
        return value

    return round(round(value / tick) * tick, 12)


@dataclass(slots=True)
class RiskManager:

    config: RiskConfig

    def stop_loss_price(
        self,
        entry_price: float,
        atr: float,
        side: str,
    ) -> float:
        """
        ATR-based stop-loss price for a new position.
        """

        distance = atr * self.config.stop_loss_atr_multiplier

        if side == "BUY":
            return entry_price - distance

        return entry_price + distance

    def take_profit_price(
        self,
        entry_price: float,
        atr: float,
        side: str,
    ) -> float:
        """
        ATR-based take-profit price for a new position.
        """

        distance = atr * self.config.take_profit_atr_multiplier

        if side == "BUY":
            return entry_price + distance

        return entry_price - distance

    def position_size(
        self,
        free_quote_balance: float,
        entry_price: float,
        stop_loss_price: float,
    ) -> float:
        """
        Size a position (in base asset units) so that a stop-loss hit
        loses no more than `risk_per_trade_pct` of free quote balance,
        capped at `max_position_pct` of balance regardless of stop
        distance.
        """

        if free_quote_balance <= 0:
            raise RiskRejected("No free quote balance available.")

        risk_amount = free_quote_balance * self.config.risk_per_trade_pct
        stop_distance = abs(entry_price - stop_loss_price)

        if stop_distance <= 0:
            raise RiskRejected("Stop-loss distance must be positive.")

        risk_sized_qty = risk_amount / stop_distance

        max_notional = (
            free_quote_balance
            * self.config.max_position_pct
            * self.config.balance_safety_margin
        )
        max_qty_by_cap = max_notional / entry_price

        return min(risk_sized_qty, max_qty_by_cap)

    def build_order(
        self,
        signal: Signal,
        candles: list[Candle],
        atr_values: list[float | None],
        filters: SymbolFilters,
        free_quote_balance: float,
        free_base_balance: float,
    ) -> OrderRequest:
        """
        Turn a Signal into a validated, exchange-ready market OrderRequest.

        BUY signals are sized by risk (risk_per_trade_pct of quote
        balance, capped by max_position_pct). SELL signals close the
        existing base-asset position — this bot only holds long spot
        positions, it does not short.

        Raises
        ------
        RiskRejected
            If the signal cannot be sized into a valid order.
        """

        index = self._index_for_timestamp(candles, signal.timestamp)

        if index is None:
            raise RiskRejected(
                f"No candle found for signal timestamp {signal.timestamp}."
            )

        atr = atr_values[index]

        if atr is None or atr <= 0:
            raise RiskRejected(
                f"No valid ATR at signal timestamp {signal.timestamp}; "
                "cannot size a stop-loss."
            )

        if signal.side == "BUY":
            return self._build_buy_order(
                signal, atr, filters, free_quote_balance,
            )

        if signal.side == "SELL":
            return self._build_sell_order(
                signal, filters, free_base_balance,
            )

        raise RiskRejected(f"Unknown signal side: {signal.side!r}")

    def _build_buy_order(
        self,
        signal: Signal,
        atr: float,
        filters: SymbolFilters,
        free_quote_balance: float,
    ) -> OrderRequest:

        stop_loss = self.stop_loss_price(signal.price, atr, "BUY")

        quantity = self.position_size(
            free_quote_balance,
            signal.price,
            stop_loss,
        )

        quantity = round_down_to_step(quantity, filters.step_size)

        self._validate(quantity, signal.price, filters)

        return OrderRequest(
            symbol=filters.symbol,
            side="BUY",
            type="MARKET",
            quantity=quantity,
            reason=signal.reason,
        )

    def _build_sell_order(
        self,
        signal: Signal,
        filters: SymbolFilters,
        free_base_balance: float,
    ) -> OrderRequest:
        """
        SELL signals close an existing long position by selling the full
        free base-asset balance held.
        """

        quantity = round_down_to_step(free_base_balance, filters.step_size)

        if quantity <= 0:
            raise RiskRejected(
                "No base asset balance to sell — nothing to close."
            )

        self._validate(quantity, signal.price, filters)

        return OrderRequest(
            symbol=filters.symbol,
            side="SELL",
            type="MARKET",
            quantity=quantity,
            reason=signal.reason,
        )

    @staticmethod
    def _validate(
        quantity: float,
        price: float,
        filters: SymbolFilters,
    ) -> None:

        if quantity < filters.min_qty:
            raise RiskRejected(
                f"Quantity {quantity} below exchange minimum "
                f"{filters.min_qty} for {filters.symbol}."
            )

        if quantity > filters.max_qty:
            raise RiskRejected(
                f"Quantity {quantity} above exchange maximum "
                f"{filters.max_qty} for {filters.symbol}."
            )

        notional = quantity * price

        if notional < filters.min_notional:
            raise RiskRejected(
                f"Order notional {notional:.2f} below exchange minimum "
                f"{filters.min_notional} for {filters.symbol}."
            )

    @staticmethod
    def _index_for_timestamp(
        candles: list[Candle],
        timestamp: int,
    ) -> int | None:

        for i, candle in enumerate(candles):
            if candle.timestamp == timestamp:
                return i

        return None
