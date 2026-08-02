"""
Simple long/flat backtester.

Simulates executing a strategy's Signal stream against historical
candles: BUY opens a long position (if flat), SELL closes it (if
holding). No shorting — matches spot trading on Tabdeal. Fill price is
taken directly from the signal (no slippage modeled); an optional
round-trip fee can be applied.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.models import Candle, Signal


@dataclass(slots=True, frozen=True)
class BacktestTrade:
    """
    One completed round-trip (entry + exit).
    """

    entry_time: int
    entry_price: float
    exit_time: int
    exit_price: float
    fee_pct: float = 0.0

    @property
    def pnl_pct(self) -> float:
        """
        Net return of this trade, as a fraction (0.01 = 1%).
        """

        gross = (self.exit_price - self.entry_price) / self.entry_price

        return gross - (self.fee_pct * 2)


@dataclass(slots=True)
class BacktestResult:
    """
    Aggregated results of a backtest run.
    """

    trades: list[BacktestTrade]
    equity_curve: list[float] = field(default_factory=list)

    @property
    def total_return_pct(self) -> float:
        if not self.equity_curve:
            return 0.0

        return (self.equity_curve[-1] - 1.0) * 100

    @property
    def win_rate_pct(self) -> float:
        if not self.trades:
            return 0.0

        wins = sum(1 for t in self.trades if t.pnl_pct > 0)

        return wins / len(self.trades) * 100

    @property
    def avg_trade_pnl_pct(self) -> float:
        if not self.trades:
            return 0.0

        return (
            sum(t.pnl_pct for t in self.trades)
            / len(self.trades)
            * 100
        )

    @property
    def max_drawdown_pct(self) -> float:
        peak = float("-inf")
        max_dd = 0.0

        for value in self.equity_curve:
            peak = max(peak, value)

            if peak > 0:
                drawdown = (peak - value) / peak
                max_dd = max(max_dd, drawdown)

        return max_dd * 100


def run_backtest(
    candles: list[Candle],
    signals: list[Signal],
    fee_pct: float = 0.0,
) -> BacktestResult:
    """
    Run a long/flat backtest.

    Parameters
    ----------
    candles
        Historical candles, ordered by timestamp.
    signals
        Signals produced by a strategy over the same candles.
    fee_pct
        Per-side trading fee as a fraction (e.g. 0.001 = 0.1%). Applied
        on both entry and exit.
    """

    signals_by_ts: dict[int, list[Signal]] = {}

    for signal in signals:
        signals_by_ts.setdefault(signal.timestamp, []).append(signal)

    trades: list[BacktestTrade] = []
    equity_curve: list[float] = []

    equity = 1.0
    position_open = False
    entry_time: int | None = None
    entry_price: float | None = None

    for candle in candles:

        for signal in signals_by_ts.get(candle.timestamp, []):

            if signal.side == "BUY" and not position_open:
                position_open = True
                entry_time = signal.timestamp
                entry_price = signal.price

            elif signal.side == "SELL" and position_open:
                trade = BacktestTrade(
                    entry_time=entry_time,
                    entry_price=entry_price,
                    exit_time=signal.timestamp,
                    exit_price=signal.price,
                    fee_pct=fee_pct,
                )
                equity *= 1 + trade.pnl_pct
                trades.append(trade)
                position_open = False
                entry_time = None
                entry_price = None

        if position_open:
            unrealized = (candle.close - entry_price) / entry_price
            equity_curve.append(equity * (1 + unrealized))
        else:
            equity_curve.append(equity)

    return BacktestResult(
        trades=trades,
        equity_curve=equity_curve,
    )
