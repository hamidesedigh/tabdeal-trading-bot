"""
Unit tests for TrendFollowingStrategy.

These use synthetic candles and a synthetic MarketState so the strategy
logic is tested in isolation, independent of live Tabdeal data or the
SQLite trades table.
"""

from app.models import Candle
from app.state.models import MarketState, StateSeries
from app.strategy.trend_following import TrendFollowingStrategy


def make_candles(n: int) -> list[Candle]:
    return [
        Candle(
            timestamp=1_700_000_000 + i * 60,
            open=100.0 + i,
            high=101.0 + i,
            low=99.0 + i,
            close=100.0 + i,
            volume=10.0,
        )
        for i in range(n)
    ]


def make_state(
    direction: list[float | None],
    strength: list[float | None],
    quality: list[float | None],
    efficiency: list[float | None],
) -> MarketState:
    return MarketState(
        direction=StateSeries(name="direction", values=direction),
        strength=StateSeries(name="strength", values=strength),
        quality=StateSeries(name="quality", values=quality),
        efficiency=StateSeries(name="efficiency", values=efficiency),
    )


def test_buy_signal_emitted_when_all_thresholds_align():
    candles = make_candles(1)
    state = make_state(
        direction=[1.5],
        strength=[30.0],
        quality=[0.80],
        efficiency=[0.20],
    )

    strategy = TrendFollowingStrategy()
    signals = strategy.evaluate(candles, state)

    assert len(signals) == 1
    signal = signals[0]
    assert signal.side == "BUY"
    assert signal.strategy == "TrendFollowing"
    assert signal.price == candles[0].close
    assert 0.0 <= signal.score <= 1.0


def test_sell_signal_emitted_when_all_thresholds_align():
    candles = make_candles(1)
    state = make_state(
        direction=[-1.5],
        strength=[30.0],
        quality=[0.80],
        efficiency=[-0.20],
    )

    strategy = TrendFollowingStrategy()
    signals = strategy.evaluate(candles, state)

    assert len(signals) == 1
    assert signals[0].side == "SELL"


def test_no_signal_when_strength_below_threshold():
    candles = make_candles(1)
    state = make_state(
        direction=[1.5],
        strength=[10.0],
        quality=[0.80],
        efficiency=[0.20],
    )

    strategy = TrendFollowingStrategy()
    signals = strategy.evaluate(candles, state)

    assert signals == []


def test_no_signal_when_any_state_value_is_none():
    candles = make_candles(1)
    state = make_state(
        direction=[None],
        strength=[30.0],
        quality=[0.80],
        efficiency=[0.20],
    )

    strategy = TrendFollowingStrategy()
    signals = strategy.evaluate(candles, state)

    assert signals == []


def test_mixed_series_only_emits_signals_where_conditions_hold():
    candles = make_candles(3)
    state = make_state(
        direction=[1.5, -1.5, 0.0],
        strength=[30.0, 30.0, 30.0],
        quality=[0.80, 0.80, 0.80],
        efficiency=[0.20, -0.20, 0.20],
    )

    strategy = TrendFollowingStrategy()
    signals = strategy.evaluate(candles, state)

    assert len(signals) == 2
    assert signals[0].side == "BUY"
    assert signals[1].side == "SELL"
