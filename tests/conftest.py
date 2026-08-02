from app.candles import build_candles
from app.storage import load_trades

import pytest


@pytest.fixture(scope="session")
def candles():

    trades = load_trades()

    return build_candles(
        trades,
        timeframe="1h",
    )