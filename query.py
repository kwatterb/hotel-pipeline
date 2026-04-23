"""
Run this after the pipeline to inspect what's in the database.
Usage: python query.py
"""

import sqlite3
import pandas as pd

DB_FILE = "data/hotel_pipeline.db"

conn = sqlite3.connect(DB_FILE)

print("\n--- Pipeline Run Log ---")
log_df = pd.read_sql("SELECT * FROM pipeline_log ORDER BY run_at DESC LIMIT 5", conn)
print(log_df.to_string(index=False))

print("\n--- Booking Counts by Hotel Type ---")
df1 = pd.read_sql("""
    SELECT p.hotel_type, COUNT(b.id) as total_bookings,
           ROUND(AVG(pr.adr), 2) as avg_daily_rate,
           SUM(b.is_canceled) as cancellations
    FROM bookings b
    JOIN properties p ON b.property_id = p.id
    JOIN pricing pr ON pr.booking_id = b.id
    GROUP BY p.hotel_type
""", conn)
print(df1.to_string(index=False))

print("\n--- Top 10 Countries by Bookings ---")
df2 = pd.read_sql("""
    SELECT p.country, COUNT(b.id) as bookings
    FROM bookings b
    JOIN properties p ON b.property_id = p.id
    GROUP BY p.country
    ORDER BY bookings DESC
    LIMIT 10
""", conn)
print(df2.to_string(index=False))

print("\n--- Avg Daily Rate by Arrival Month ---")
df3 = pd.read_sql("""
    SELECT b.arrival_month, ROUND(AVG(pr.adr), 2) as avg_adr, COUNT(*) as bookings
    FROM bookings b
    JOIN pricing pr ON pr.booking_id = b.id
    GROUP BY b.arrival_month
    ORDER BY avg_adr DESC
""", conn)
print(df3.to_string(index=False))

conn.close()
