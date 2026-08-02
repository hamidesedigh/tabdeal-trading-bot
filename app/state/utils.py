"""
Utilities for state calculations.
"""

from __future__ import annotations


def linear_regression(
    values: list[float],
) -> tuple[
    float,  # slope
    float,  # intercept
    float,  # r_squared
]:
    """
    Ordinary Least Squares regression.

    Returns
    -------
    slope
    intercept
    coefficient of determination (R²)
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

    #
    # Calculate R²
    #

    ss_total = 0.0
    ss_residual = 0.0

    for i, y in enumerate(values):

        predicted = slope * i + intercept

        ss_total += (y - y_mean) ** 2
        ss_residual += (y - predicted) ** 2

    if ss_total == 0:
        r_squared = 1.0
    else:
        r_squared = 1.0 - (ss_residual / ss_total)

    return (
        slope,
        intercept,
        r_squared,
    )