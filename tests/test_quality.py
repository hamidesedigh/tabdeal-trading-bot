from app.models import Candle
from app.state.quality import quality


def test_quality_length():

    candles = []

    for i in range(50):
        candles.append(
            Candle(
                timestamp=i,
                open=i,
                high=i,
                low=i,
                close=i,
                volume=1,
            )
        )

    state = quality(candles)

    assert len(state.values) == len(candles)

def test_quality_perfect_trend():

    candles = []

    for i in range(50):

        candles.append(
            Candle(
                timestamp=i,
                open=i,
                high=i,
                low=i,
                close=i * 10,
                volume=1,
            )
        )

    state = quality(candles)

    assert state.values[-1] > 0.999