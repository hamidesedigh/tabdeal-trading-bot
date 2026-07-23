"""
Common data models.
"""

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class Trade:
    """
    Standard trade model used across the project.
    """

    id: int
    price: float
    quantity: float
    quote_quantity: float
    timestamp: int
    is_buyer_maker: bool