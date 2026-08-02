"""
Unit tests for app.risk (RiskManager, sizing, and rounding helpers).
"""

import pytest

from app.models import Candle, Signal, SymbolFilters
from app.risk import (
    RiskConfig,
    RiskManager,
    RiskRejected,
    round_down_to_step,
    round_to_tick,
)


def make_candle(ts: int, close: float) -> Candle:
    return Candle(
        timestamp=ts, open=close, high=close, low=close,
        close=close, volume=1.0,
    )


def make_signal(ts: int, side: str, price: float) -> Signal:
    return Signal(
        timestamp=ts, side=side, price=price,
        strategy="test", score=1.0,
    )


def make_filters(**overrides) -> SymbolFilters:
    defaults = dict(
        symbol="BTC_IRT",
        base_asset="BTC",
        quote_asset="IRT",
        tick_size=1.0,
        min_price=300.0,
        max_price=30_000_000_000.0,
        step_size=0.00000001,
        min_qty=0.00005,
        max_qty=1.0,
        min_notional=99000.0,
    )
    defaults.update(overrides)
    return SymbolFilters(**defaults)


# ---- rounding helpers ----

def test_round_down_to_step_basic():
    assert round_down_to_step(0.123456789, 0.0001) == 0.1234


def test_round_down_to_step_never_rounds_up():
    # 0.00019999... should round down to 0.0001, not up to 0.0002
    assert round_down_to_step(0.00019999, 0.0001) == 0.0001


def test_round_to_tick_rounds_to_nearest():
    assert round_to_tick(103.6, 1.0) == 104.0
    assert round_to_tick(103.4, 1.0) == 103.0


# ---- stop-loss / take-profit ----

def test_stop_loss_price_buy_is_below_entry():
    rm = RiskManager(config=RiskConfig(stop_loss_atr_multiplier=2.0))
    stop = rm.stop_loss_price(entry_price=100.0, atr=5.0, side="BUY")
    assert stop == 90.0


def test_stop_loss_price_sell_is_above_entry():
    rm = RiskManager(config=RiskConfig(stop_loss_atr_multiplier=2.0))
    stop = rm.stop_loss_price(entry_price=100.0, atr=5.0, side="SELL")
    assert stop == 110.0


def test_take_profit_price_buy_is_above_entry():
    rm = RiskManager(config=RiskConfig(take_profit_atr_multiplier=3.0))
    tp = rm.take_profit_price(entry_price=100.0, atr=5.0, side="BUY")
    assert tp == 115.0


# ---- position sizing ----

def test_position_size_respects_risk_per_trade():
    rm = RiskManager(config=RiskConfig(
        risk_per_trade_pct=0.01, max_position_pct=1.0,
    ))
    # balance=1,000,000 IRT, risk 1% = 10,000 IRT max loss.
    # entry=100,000, stop=95,000 -> stop distance=5,000
    # qty = 10,000 / 5,000 = 2.0
    qty = rm.position_size(
        free_quote_balance=1_000_000,
        entry_price=100_000,
        stop_loss_price=95_000,
    )
    assert qty == pytest.approx(2.0)


def test_position_size_capped_by_max_position_pct():
    rm = RiskManager(config=RiskConfig(
        risk_per_trade_pct=0.50,   # very aggressive risk setting
        max_position_pct=0.10,     # but hard-capped at 10% of balance
        balance_safety_margin=1.0,
    ))
    # Without the cap this would size a huge position from a tight stop.
    qty = rm.position_size(
        free_quote_balance=1_000_000,
        entry_price=100_000,
        stop_loss_price=99_999,   # very tight stop
    )
    max_qty_by_cap = (1_000_000 * 0.10) / 100_000
    assert qty == pytest.approx(max_qty_by_cap)


def test_position_size_rejects_zero_stop_distance():
    rm = RiskManager(config=RiskConfig())
    with pytest.raises(RiskRejected):
        rm.position_size(
            free_quote_balance=1_000_000,
            entry_price=100_000,
            stop_loss_price=100_000,
        )


def test_position_size_rejects_zero_balance():
    rm = RiskManager(config=RiskConfig())
    with pytest.raises(RiskRejected):
        rm.position_size(
            free_quote_balance=0,
            entry_price=100_000,
            stop_loss_price=95_000,
        )


# ---- build_order: BUY ----

def test_build_buy_order_produces_valid_order():
    rm = RiskManager(config=RiskConfig(
        risk_per_trade_pct=0.02, max_position_pct=1.0,
    ))
    candles = [make_candle(1, 5_000_000)]
    atr_values = [100_000.0]
    filters = make_filters(step_size=0.0001, min_notional=1000, max_qty=1000)
    signal = make_signal(1, "BUY", 5_000_000)

    order = rm.build_order(
        signal, candles, atr_values, filters,
        free_quote_balance=100_000_000,
        free_base_balance=0.0,
    )

    assert order.side == "BUY"
    assert order.type == "MARKET"
    assert order.symbol == filters.symbol
    assert order.quantity > 0
    # quantity must be a clean multiple of step_size
    assert round(order.quantity / filters.step_size) == pytest.approx(
        order.quantity / filters.step_size, abs=1e-6,
    )


def test_build_buy_order_rejects_when_below_min_notional():
    rm = RiskManager(config=RiskConfig(
        risk_per_trade_pct=0.0001,  # tiny risk -> tiny order
        max_position_pct=1.0,
    ))
    candles = [make_candle(1, 5_000_000)]
    atr_values = [100_000.0]
    filters = make_filters(min_notional=10_000_000_000)  # unreachably high
    signal = make_signal(1, "BUY", 5_000_000)

    with pytest.raises(RiskRejected):
        rm.build_order(
            signal, candles, atr_values, filters,
            free_quote_balance=100_000_000,
            free_base_balance=0.0,
        )


def test_build_order_rejects_missing_atr():
    rm = RiskManager(config=RiskConfig())
    candles = [make_candle(1, 5_000_000)]
    atr_values = [None]
    filters = make_filters()
    signal = make_signal(1, "BUY", 5_000_000)

    with pytest.raises(RiskRejected):
        rm.build_order(
            signal, candles, atr_values, filters,
            free_quote_balance=100_000_000,
            free_base_balance=0.0,
        )


def test_build_order_rejects_unknown_timestamp():
    rm = RiskManager(config=RiskConfig())
    candles = [make_candle(1, 5_000_000)]
    atr_values = [100_000.0]
    filters = make_filters()
    signal = make_signal(999, "BUY", 5_000_000)  # no matching candle

    with pytest.raises(RiskRejected):
        rm.build_order(
            signal, candles, atr_values, filters,
            free_quote_balance=100_000_000,
            free_base_balance=0.0,
        )


# ---- build_order: SELL ----

def test_build_sell_order_sells_full_base_balance():
    rm = RiskManager(config=RiskConfig())
    candles = [make_candle(1, 5_000_000)]
    atr_values = [100_000.0]
    filters = make_filters(step_size=0.0001, min_notional=1000)
    signal = make_signal(1, "SELL", 5_000_000)

    order = rm.build_order(
        signal, candles, atr_values, filters,
        free_quote_balance=0.0,
        free_base_balance=0.05,
    )

    assert order.side == "SELL"
    assert order.quantity == pytest.approx(0.05)


def test_build_sell_order_rejects_when_no_base_balance():
    rm = RiskManager(config=RiskConfig())
    candles = [make_candle(1, 5_000_000)]
    atr_values = [100_000.0]
    filters = make_filters()
    signal = make_signal(1, "SELL", 5_000_000)

    with pytest.raises(RiskRejected):
        rm.build_order(
            signal, candles, atr_values, filters,
            free_quote_balance=0.0,
            free_base_balance=0.0,
        )
