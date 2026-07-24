"""
Application entry point.
"""

import time

from app.engine import run_cycle
from config import LIMIT, SYMBOL


def main():

    while True:

        candles = run_cycle(
            symbol=SYMBOL,
            limit=LIMIT,
        )

        print(candles[-1])

        time.sleep(60)


if __name__ == "__main__":
    main()