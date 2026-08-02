"""
Trend Following strategy.
"""

from app.models import Candle
from app.models import Signal

from app.state.models import MarketState

from app.strategy.base import Strategy


class TrendFollowingStrategy(Strategy):

    def __init__(
        self,
        direction_threshold: float = 0.0,
        strength_threshold: float = 25.0,
        quality_threshold: float = 0.70,
        efficiency_threshold: float = 0.15,
    ):

        self.direction_threshold = direction_threshold
        self.strength_threshold = strength_threshold
        self.quality_threshold = quality_threshold
        self.efficiency_threshold = efficiency_threshold

    def evaluate(
        self,
        candles: list[Candle],
        state: MarketState,
    ) -> list[Signal]:

        signals: list[Signal] = []

        for candle, direction, strength, quality, efficiency in zip(
            candles,
            state.direction.values,
            state.strength.values,
            state.quality.values,
            state.efficiency.values,
        ):

            if None in (
                direction,
                strength,
                quality,
                efficiency,
            ):
                continue

            if (
                direction > self.direction_threshold
                and strength > self.strength_threshold
                and quality > self.quality_threshold
                and efficiency > self.efficiency_threshold
            ):

                signals.append(
                    Signal(
                        timestamp=candle.timestamp,
                        side="BUY",
                        price=candle.close,
                        strategy="TrendFollowing",
                        score=self._score(strength, quality, efficiency),
                        reason=(
                            "Direction>0, "
                            "Strength>25, "
                            "Quality>0.70, "
                            "Efficiency>0.15"
                        ),
                    )
                )

            elif (
                direction < -self.direction_threshold
                and strength > self.strength_threshold
                and quality > self.quality_threshold
                and efficiency < -self.efficiency_threshold
            ):

                signals.append(
                    Signal(
                        timestamp=candle.timestamp,
                        side="SELL",
                        price=candle.close,
                        strategy="TrendFollowing",
                        score=self._score(strength, quality, abs(efficiency)),
                        reason=(
                            "Direction<0, "
                            "Strength>25, "
                            "Quality>0.70, "
                            "Efficiency<-0.15"
                        ),
                    )
                )

        return signals

    @staticmethod
    def _score(
        strength: float,
        quality: float,
        efficiency: float,
    ) -> float:
        """
        Composite confidence score in [0, 1], blending strength (ADX,
        capped at 100), quality, and efficiency. Weights are a starting
        point — tune once you have backtest results to compare against.
        """

        strength_norm = min(strength / 100.0, 1.0)
        quality_norm = min(max(quality, 0.0), 1.0)
        efficiency_norm = min(max(efficiency, 0.0), 1.0)

        score = (
            0.4 * strength_norm
            + 0.4 * quality_norm
            + 0.2 * efficiency_norm
        )

        return round(score, 4)