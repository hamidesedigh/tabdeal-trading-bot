from app.models import Candle
from app.state.direction import direction


def test_direction_length():

    candles = []

    for i in range(40):
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

    state = direction(candles, period=20)

    assert len(state.values) == len(candles)