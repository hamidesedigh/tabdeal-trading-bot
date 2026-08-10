"""
Live trading loop: collect trades -> build candles/state -> generate
signals -> size & validate orders -> execute (or dry-run) on Tabdeal.

SAFETY:
  - DRY_RUN defaults to True. Orders are sized and validated but never
    actually sent. Flip it only after validating the strategy against
    more history than the ~4 days currently in data/trades.db, and after
    watching this script run in dry-run mode for a while.
  - Requires TABDEAL_API_KEY and TABDEAL_API_SECRET environment
    variables. Never hardcode credentials in source.

Usage:
    export TABDEAL_API_KEY=...
    export TABDEAL_API_SECRET=...
    python -m tools.run_live
"""

import time

from dotenv import load_dotenv

from app.candles import build_candles
from app.collector import fetch_trades
from app.exchange import ExchangeError, TabdealExchange
from app.indicators.atr import atr
from app.risk import RiskConfig, RiskManager, RiskRejected
from app.state.pipeline import build_state
from app.storage import initialize_database, insert_trades, load_trades
from app.strategy.pipeline import build_signals
from config import LIMIT, SYMBOL

DRY_RUN = True
TIMEFRAME = "5min"
POLL_SECONDS = 60
WARMUP_PERIOD = 20


def run_once(
    exchange: TabdealExchange,
    risk_manager: RiskManager,
) -> None:

    initialize_database()
    insert_trades(fetch_trades(symbol=SYMBOL, limit=LIMIT))

    trades = load_trades()
    candles = build_candles(trades, timeframe=TIMEFRAME)

    if len(candles) <= WARMUP_PERIOD:
        print(
            f"Only {len(candles)} candles available "
            f"(need > {WARMUP_PERIOD}); skipping this cycle."
        )
        return

    state = build_state(candles)
    signals = build_signals(candles, state)

    if not signals:
        return

    latest_signal = signals[-1]

    if latest_signal.timestamp != candles[-1].timestamp:
        # Only act on a signal from the most recently closed candle —
        # older signals have already been acted on (or missed).
        return

    atr_values = atr(candles)
    filters = exchange.get_symbol_filters(SYMBOL)

    quote_balance = exchange.get_free_balance(filters.quote_asset)
    base_balance = exchange.get_free_balance(filters.base_asset)

    try:
        order = risk_manager.build_order(
            latest_signal,
            candles,
            atr_values,
            filters,
            free_quote_balance=quote_balance,
            free_base_balance=base_balance,
        )
    except RiskRejected as exc:
        print(f"Signal rejected by risk manager: {exc}")
        return

    result = exchange.place_order(order)

    prefix = "[DRY RUN] " if exchange.dry_run else ""

    if result.accepted:
        print(f"{prefix}Order accepted: {order}")
    else:
        print(f"{prefix}Order rejected by exchange: {result.rejection_reason}")


def main() -> None:

    load_dotenv()

    exchange = TabdealExchange(dry_run=DRY_RUN)
    risk_manager = RiskManager(config=RiskConfig())

    print(f"Starting live loop (dry_run={DRY_RUN}) for {SYMBOL}...")

    while True:

        try:
            run_once(exchange, risk_manager)
        except ExchangeError as exc:
            print(f"Exchange error: {exc}")

        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    main()
