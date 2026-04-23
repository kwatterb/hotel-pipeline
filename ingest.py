import os
import requests
import pandas as pd
from logger import get_logger

log = get_logger("ingest")

# Kaggle Hotel Booking Demand dataset hosted on GitHub (no API key needed)
DATA_URL = "https://raw.githubusercontent.com/rfordatascience/tidytuesday/master/data/2020/2020-02-11/hotels.csv"
RAW_FILE = "data/hotels_raw.csv"


def fetch_data(mode: str = "full") -> pd.DataFrame:
    """
    Downloads the hotel dataset CSV and returns it as a DataFrame.
    - full: always re-downloads (falls back to cached file if download fails)
    - incremental: uses cached file if it exists, otherwise downloads
    """
    os.makedirs("data", exist_ok=True)

    if mode == "incremental" and os.path.exists(RAW_FILE):
        log.info(f"Incremental mode — loading cached file: {RAW_FILE}")
        df = pd.read_csv(RAW_FILE)
        log.info(f"Loaded {len(df):,} rows from cache")
        return df

    log.info(f"Downloading dataset from source...")
    try:
        response = requests.get(DATA_URL, timeout=30)
        response.raise_for_status()
        with open(RAW_FILE, "wb") as f:
            f.write(response.content)
        df = pd.read_csv(RAW_FILE)
        log.info(f"Downloaded and saved {len(df):,} rows to {RAW_FILE}")
        return df
    except requests.RequestException as e:
        log.warning(f"Download failed: {e}")
        if os.path.exists(RAW_FILE):
            log.info(f"Falling back to cached file: {RAW_FILE}")
            df = pd.read_csv(RAW_FILE)
            log.info(f"Loaded {len(df):,} rows from cache")
            return df
        raise RuntimeError(
            "Download failed and no cached file found. "
            "Place a hotels_raw.csv in the data/ folder to run offline."
        )
