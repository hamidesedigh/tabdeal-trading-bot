"""
Simple database explorer.
"""

from app.storage import (
    count_trades,
    load_trades,
)

print("=" * 50)

print(f"Trades : {count_trades()}")

print()

print("First 2 trades")

for trade in load_trades(limit=2):
    print(trade)