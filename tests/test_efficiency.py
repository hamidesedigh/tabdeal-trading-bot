from app.state.efficiency import efficiency


def test_efficiency(candles):

    state = efficiency(
        candles,
        period=20,
    )

    assert len(state.values) == len(candles)

    valid = [
        v
        for v in state.values
        if v is not None
    ]

    assert len(valid) > 0

    assert all(
        isinstance(v, float)
        for v in valid
    )