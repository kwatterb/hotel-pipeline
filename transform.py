import pandas as pd
from logger import get_logger

log = get_logger("transform")

# Columns we expect from the raw CSV
REQUIRED_COLUMNS = [
    "hotel", "is_canceled", "lead_time", "arrival_date_year",
    "arrival_date_month", "arrival_date_day_of_month",
    "stays_in_weekend_nights", "stays_in_week_nights",
    "adults", "children", "babies", "reserved_room_type",
    "assigned_room_type", "booking_changes", "deposit_type",
    "customer_type", "country", "market_segment", "adr",
    "required_car_parking_spaces", "total_of_special_requests"
]


def validate_schema(df: pd.DataFrame) -> None:
    """Raises ValueError if any expected columns are missing."""
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing columns in raw data: {missing}")


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans and normalizes the raw hotel DataFrame.
    Returns a cleaned copy — does not modify the original.
    """
    log.info(f"Starting transform on {len(df):,} rows")
    validate_schema(df)
    df = df.copy()

    # --- Null handling ---
    null_counts = df.isnull().sum()
    cols_with_nulls = null_counts[null_counts > 0]
    if not cols_with_nulls.empty:
        log.debug(f"Null counts before cleaning:\n{cols_with_nulls}")

    df["children"] = df["children"].fillna(0)
    df["country"] = df["country"].fillna("Unknown")
    df.dropna(subset=["adults", "adr", "is_canceled"], inplace=True)

    # --- Type casting ---
    df["children"] = df["children"].astype(int)
    df["is_canceled"] = df["is_canceled"].astype(int)
    df["lead_time"] = df["lead_time"].astype(int)

    # --- Anomaly detection ---
    # Negative ADR (average daily rate) makes no sense
    negative_adr = df[df["adr"] < 0]
    if len(negative_adr) > 0:
        log.warning(f"Flagging {len(negative_adr)} rows with negative ADR — setting to NaN")
        df.loc[df["adr"] < 0, "adr"] = None

    # Zero-guest bookings are likely data errors
    zero_guests = df[(df["adults"] == 0) & (df["children"] == 0) & (df["babies"] == 0)]
    if len(zero_guests) > 0:
        log.warning(f"Dropping {len(zero_guests)} bookings with zero guests")
        df = df[~((df["adults"] == 0) & (df["children"] == 0) & (df["babies"] == 0))]

    # Extreme lead times (>2 years) are suspicious
    extreme_lead = df[df["lead_time"] > 730]
    if len(extreme_lead) > 0:
        log.warning(f"Found {len(extreme_lead)} bookings with lead_time > 730 days")

    # --- Normalize column names for DB load ---
    df.rename(columns={
        "hotel": "hotel_type",
        "arrival_date_year": "arrival_year",
        "arrival_date_month": "arrival_month",
        "arrival_date_day_of_month": "arrival_date",
        "stays_in_weekend_nights": "stays_weekend_nights",
        "stays_in_week_nights": "stays_week_nights",
        "required_car_parking_spaces": "required_parking_spaces",
        "total_of_special_requests": "total_special_requests"
    }, inplace=True)

    log.info(f"Transform complete — {len(df):,} rows after cleaning")
    return df
