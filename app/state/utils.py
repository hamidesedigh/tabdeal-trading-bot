"""
Utilities for state calculations.
"""

from __future__ import annotations


def linear_regression(values: list[float]) -> tuple[float, float]:
    """
    Ordinary Least Squares regression.

    Returns
    -------
    slope
    intercept
    """

    n = len(values)

    x_mean = (n - 1) / 2
    y_mean = sum(values) / n

    numerator = 0.0
    denominator = 0.0

    for i, y in enumerate(values):

        dx = i - x_mean
        dy = y - y_mean

        numerator += dx * dy
        denominator += dx * dx

    slope = numerator / denominator
    intercept = y_mean - slope * x_mean

    return slope, intercept