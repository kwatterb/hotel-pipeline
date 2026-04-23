import sqlite3
import pandas as pd
from logger import get_logger

log = get_logger("load")

DB_FILE = "data/hotel_pipeline.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    """Creates tables from schema.sql if they don't exist."""
    with open("schema.sql", "r") as f:
        conn.executescript(f.read())
    conn.commit()
    log.debug("Database schema initialized")


def load(df: pd.DataFrame, conn: sqlite3.Connection) -> int:
    """
    Loads cleaned data into properties, bookings, and pricing tables.
    Returns total rows inserted across all tables.
    """
    total_inserted = 0
    cursor = conn.cursor()

    log.info(f"Loading {len(df):,} rows into database...")

    for _, row in df.iterrows():
        # Insert or ignore duplicate property types
        cursor.execute("""
            INSERT INTO properties (hotel_type, country, market_segment)
            VALUES (?, ?, ?)
        """, (row["hotel_type"], row["country"], row["market_segment"]))
        property_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO bookings (
                property_id, is_canceled, lead_time, arrival_year, arrival_month,
                arrival_date, stays_weekend_nights, stays_week_nights,
                adults, children, babies, reserved_room_type, assigned_room_type,
                booking_changes, deposit_type, customer_type
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            property_id, row["is_canceled"], row["lead_time"],
            row["arrival_year"], row["arrival_month"], row["arrival_date"],
            row["stays_weekend_nights"], row["stays_week_nights"],
            row["adults"], row["children"], row["babies"],
            row["reserved_room_type"], row["assigned_room_type"],
            row["booking_changes"], row["deposit_type"], row["customer_type"]
        ))
        booking_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO pricing (booking_id, adr, required_parking_spaces, total_special_requests)
            VALUES (?, ?, ?, ?)
        """, (
            booking_id, row.get("adr"), row.get("required_parking_spaces"),
            row.get("total_special_requests")
        ))

        total_inserted += 1

    conn.commit()
    log.info(f"Inserted {total_inserted:,} records across properties/bookings/pricing")
    return total_inserted


def write_pipeline_log(conn: sqlite3.Connection, mode: str, rows_ingested: int,
                        rows_cleaned: int, rows_loaded: int,
                        status: str, error: str = None) -> None:
    """Writes a summary row to the pipeline_log table after each run."""
    conn.execute("""
        INSERT INTO pipeline_log (mode, rows_ingested, rows_cleaned, rows_loaded, status, error_message)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (mode, rows_ingested, rows_cleaned, rows_loaded, status, error))
    conn.commit()
