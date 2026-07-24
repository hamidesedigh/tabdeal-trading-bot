"""
SQLite storage for trades.
"""

from pathlib import Path
import sqlite3

from app.models import Trade

DATABASE_PATH = Path("data/trades.db")


def get_connection() -> sqlite3.Connection:
    """
    Create a SQLite connection.
    """
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    return sqlite3.connect(DATABASE_PATH)


def initialize_database() -> None:
    """
    Create database tables if they do not exist.
    """

    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY,
                price REAL NOT NULL,
                quantity REAL NOT NULL,
                quote_quantity REAL NOT NULL,
                timestamp INTEGER NOT NULL,
                is_buyer_maker INTEGER NOT NULL
            )
            """
        )


def insert_trades(trades: list[Trade]) -> None:
    """
    Insert trades into database.

    Existing trade IDs are ignored.
    """

    with get_connection() as conn:
        conn.executemany(
            """
            INSERT OR IGNORE INTO trades (
                id,
                price,
                quantity,
                quote_quantity,
                timestamp,
                is_buyer_maker
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    trade.id,
                    trade.price,
                    trade.quantity,
                    trade.quote_quantity,
                    trade.timestamp,
                    int(trade.is_buyer_maker),
                )
                for trade in trades
            ],
        )


def load_trades(limit: int | None = None) -> list[Trade]:
    """
    Load trades ordered by timestamp.
    """

    query = """
        SELECT
            id,
            price,
            quantity,
            quote_quantity,
            timestamp,
            is_buyer_maker
        FROM trades
        ORDER BY timestamp
    """

    if limit is not None:
        query += " LIMIT ?"

    with get_connection() as conn:

        if limit is None:
            rows = conn.execute(query).fetchall()
        else:
            rows = conn.execute(query, (limit,)).fetchall()

    return [
        Trade(
            id=row[0],
            price=row[1],
            quantity=row[2],
            quote_quantity=row[3],
            timestamp=row[4],
            is_buyer_maker=bool(row[5]),
        )
        for row in rows
    ]


def count_trades() -> int:
    """
    Return number of stored trades.
    """

    with get_connection() as conn:
        row = conn.execute(
            "SELECT COUNT(*) FROM trades"
        ).fetchone()

    return row[0]