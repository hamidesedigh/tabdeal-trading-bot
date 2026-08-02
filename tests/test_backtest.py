"""
Unit tests for app.backtest.run_backtest.
"""

from app.backtest import run_backtest
from app.models import Candle, Signal


def make_candle(ts: int, close: float) -> Candle:
    return Candle(
        timestamp=ts,
        open=close,
        high=close,
        low=close,
        close=close,
        volume=1.0,
    )


def make_signal(ts: int, side: str, price: float) -> Signal:
    return Signal(
        timestamp=ts,
        side=side,
        price=price,
        strategy="test",
        score=1.0,
    )


def test_single_winning_round_trip():
    candles = [
        make_candle(1, 100.0),
        make_candle(2, 110.0),
        make_candle(3, 120.0),
    ]
    signals = [
        make_signal(1, "BUY", 100.0),
        make_signal(3, "SELL", 120.0),
    ]

    result = run_backtest(candles, signals)

    assert len(result.trades) == 1
    assert result.trades[0].pnl_pct == 0.2
    assert result.win_rate_pct == 100.0
    assert round(result.total_return_pct, 2) == 20.0


def test_single_losing_round_trip():
    candles = [
        make_candle(1, 100.0),
        make_candle(2, 90.0),
    ]
    signals = [
        make_signal(1, "BUY", 100.0),
        make_signal(2, "SELL", 90.0),
    ]

    result = run_backtest(candles, signals)

    assert len(result.trades) == 1
    assert result.trades[0].pnl_pct == -0.1
    assert result.win_rate_pct == 0.0


def test_fees_reduce_pnl():
    candles = [
        make_candle(1, 100.0),
        make_candle(2, 101.0),
    ]
    signals = [
        make_signal(1, "BUY", 100.0),
        make_signal(2, "SELL", 101.0),
    ]

    result = run_backtest(candles, signals, fee_pct=0.005)

    # gross 1% - (0.5% * 2) round-trip fee = 0%
    assert round(result.trades[0].pnl_pct, 4) == 0.0


def test_no_signals_produces_no_trades_and_flat_equity():
    candles = [
        make_candle(1, 100.0),
        make_candle(2, 105.0),
    ]

    result = run_backtest(candles, [])

    assert result.trades == []
    assert result.equity_curve == [1.0, 1.0]
    assert result.total_return_pct == 0.0


def test_open_position_marks_to_market_unrealized_pnl():
    candles = [
        make_candle(1, 100.0),
        make_candle(2, 110.0),
    ]
    signals = [make_signal(1, "BUY", 100.0)]

    result = run_backtest(candles, signals)

    # No SELL, so no completed trade, but equity curve should reflect
    # the open position's unrealized gain.
    assert result.trades == []
    assert result.equity_curve[-1] == 1.1


def test_second_buy_while_in_position_is_ignored():
    candles = [
        make_candle(1, 100.0),
        make_candle(2, 105.0),
        make_candle(3, 120.0),
    ]
    signals = [
        make_signal(1, "BUY", 100.0),
        make_signal(2, "BUY", 105.0),  # should be ignored, already long
        make_signal(3, "SELL", 120.0),
    ]

    result = run_backtest(candles, signals)

    assert len(result.trades) == 1
    assert result.trades[0].entry_price == 100.0
    assert result.trades[0].exit_price == 120.0


def test_max_drawdown_calculation():
    candles = [
        make_candle(1, 100.0),
        make_candle(2, 200.0),  # peak while open
        make_candle(3, 150.0),  # drawdown from peak
    ]
    signals = [make_signal(1, "BUY", 100.0)]

    result = run_backtest(candles, signals)

    # equity curve: [1.0, 2.0, 1.5] -> drawdown from 2.0 to 1.5 = 25%
    assert round(result.max_drawdown_pct, 2) == 25.0
