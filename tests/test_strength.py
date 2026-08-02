from app.state.pipeline import build_state
from app.strategy.pipeline import build_signals

def test_strategy(candles):

    state = build_state(candles)

    signals = build_signals(
        candles,
        state,
    )

    assert isinstance(signals, list)

    print()

    print(f"Signals: {len(signals)}")

    for signal in signals:

        print(signal)
