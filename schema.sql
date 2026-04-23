-- Run this once to initialize the database
-- SQLite compatible

CREATE TABLE IF NOT EXISTS properties (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hotel_type TEXT NOT NULL,          -- 'City Hotel' or 'Resort Hotel'
    country TEXT,
    market_segment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    property_id INTEGER,
    is_canceled INTEGER NOT NULL,      -- 0 or 1
    lead_time INTEGER,                 -- days between booking and arrival
    arrival_year INTEGER,
    arrival_month TEXT,
    arrival_date INTEGER,
    stays_weekend_nights INTEGER,
    stays_week_nights INTEGER,
    adults INTEGER,
    children INTEGER,
    babies INTEGER,
    reserved_room_type TEXT,
    assigned_room_type TEXT,
    booking_changes INTEGER,
    deposit_type TEXT,
    customer_type TEXT,
    FOREIGN KEY (property_id) REFERENCES properties(id)
);

CREATE TABLE IF NOT EXISTS pricing (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id INTEGER,
    adr REAL,                          -- average daily rate
    required_parking_spaces INTEGER,
    total_special_requests INTEGER,
    FOREIGN KEY (booking_id) REFERENCES bookings(id)
);

CREATE TABLE IF NOT EXISTS pipeline_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    mode TEXT,                         -- 'full' or 'incremental'
    rows_ingested INTEGER,
    rows_cleaned INTEGER,
    rows_loaded INTEGER,
    status TEXT,
    error_message TEXT
);
