"""
Utility functions for technical indicators.
"""

from app.models import Candle


def closing_prices(candles: list[Candle]) -> list[float]:
    """
    Return candle closing prices.
    """

    return [candle.close for candle in candles]


def opening_prices(candles: list[Candle]) -> list[float]:
    """
    Return candle opening prices.
    """

    return [candle.open for candle in candles]


def high_prices(candles: list[Candle]) -> list[float]:
    """
    Return candle high prices.
    """

    return [candle.high for candle in candles]


def low_prices(candles: list[Candle]) -> list[float]:
    """
    Return candle low prices.
    """

    return [candle.low for candle in candles]


def volumes(candles: list[Candle]) -> list[float]:
    """
    Return candle volumes.
    """

    return [candle.volume for candle in candles]