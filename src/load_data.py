"""Build the SQLite database from the synthetic source CSV files."""

from __future__ import annotations

import sqlite3

import pandas as pd

from config import DATABASE_PATH, RAW_DATA_DIR, SQL_DIR, ensure_directories


def load_database() -> tuple[int, int]:
    """Create the database, enforce its schema, and return loaded row counts."""

    ensure_directories()
    properties_path = RAW_DATA_DIR / "properties.csv"
    bookings_path = RAW_DATA_DIR / "bookings.csv"
    if not properties_path.exists() or not bookings_path.exists():
        raise FileNotFoundError(
            "Source CSV files are missing. Run src/generate_sample_data.py first."
        )

    properties = pd.read_csv(properties_path, dtype={"property_id": "string"})
    bookings = pd.read_csv(
        bookings_path,
        dtype={"booking_id": "string", "property_id": "string"},
    )
    bookings["rating"] = pd.to_numeric(bookings["rating"], errors="coerce")

    schema_sql = (SQL_DIR / "01_schema.sql").read_text(encoding="utf-8")
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.executescript(schema_sql)
        properties.to_sql("properties", connection, if_exists="append", index=False)
        bookings.to_sql("bookings", connection, if_exists="append", index=False)

        property_count = connection.execute("SELECT COUNT(*) FROM properties").fetchone()[0]
        booking_count = connection.execute("SELECT COUNT(*) FROM bookings").fetchone()[0]

    return property_count, booking_count


def main() -> None:
    property_count, booking_count = load_database()
    print(f"Loaded {property_count} properties and {booking_count} bookings into SQLite.")


if __name__ == "__main__":
    main()
